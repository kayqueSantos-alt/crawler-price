import requests
import cloudscraper
import json
import time
import logging
import re
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, Timeout, ConnectionError

logger = logging.getLogger("crawlers")


class BaseCrawler:
    """
    Classe base para todos os crawlers de marketplaces.
    Centraliza: timeout, retry com backoff, logging, validacao de saida,
    delay entre requests e tratamento de erros.
    """

    # Configuracoes padrao (podem ser sobrescritas por subclasse)
    TIMEOUT = 15
    MAX_RETRIES = 3
    BACKOFF_FACTOR = 2  # segundos: 2, 4, 8
    DELAY_BETWEEN_REQUESTS = 1.0  # segundos entre requests ao mesmo dominio
    USE_CLOUDSCRAPER = False

    # --- HTTP helpers com retry e timeout ---

    @classmethod
    def _get_session(cls):
        """Retorna requests.Session ou cloudscraper conforme config da subclasse."""
        if cls.USE_CLOUDSCRAPER:
            return cloudscraper.create_scraper()
        session = requests.Session()
        return session

    @classmethod
    def _request_with_retry(cls, method, url, **kwargs):
        """
        Faz request HTTP com retry e backoff exponencial.
        Retorna o objeto Response.
        Lanca RequestException apos esgotar tentativas.
        """
        kwargs.setdefault("timeout", cls.TIMEOUT)
        session = cls._get_session()

        last_exception = None
        for attempt in range(1, cls.MAX_RETRIES + 1):
            try:
                response = getattr(session, method)(url, **kwargs)
                response.raise_for_status()
                return response
            except (Timeout, ConnectionError) as e:
                last_exception = e
                wait = cls.BACKOFF_FACTOR * attempt
                logger.warning(
                    f"[{cls.__name__}] Tentativa {attempt}/{cls.MAX_RETRIES} falhou para {url}: {e}. "
                    f"Aguardando {wait}s..."
                )
                time.sleep(wait)
            except RequestException as e:
                # Erros HTTP 4xx/5xx — retry so para 429 e 5xx
                status = getattr(e.response, "status_code", None)
                if status and (status == 429 or status >= 500):
                    last_exception = e
                    wait = cls.BACKOFF_FACTOR * attempt
                    logger.warning(
                        f"[{cls.__name__}] HTTP {status} para {url}. "
                        f"Tentativa {attempt}/{cls.MAX_RETRIES}. Aguardando {wait}s..."
                    )
                    time.sleep(wait)
                else:
                    logger.error(f"[{cls.__name__}] Erro HTTP {status} para {url}: {e}")
                    raise

        logger.error(
            f"[{cls.__name__}] Todas as {cls.MAX_RETRIES} tentativas falharam para {url}"
        )
        raise last_exception

    @classmethod
    def get(cls, url, **kwargs):
        """GET com retry, timeout e delay."""
        response = cls._request_with_retry("get", url, **kwargs)
        time.sleep(cls.DELAY_BETWEEN_REQUESTS)
        return response

    @classmethod
    def post(cls, url, **kwargs):
        """POST com retry, timeout e delay."""
        response = cls._request_with_retry("post", url, **kwargs)
        time.sleep(cls.DELAY_BETWEEN_REQUESTS)
        return response

    # --- Parsing helpers ---

    @classmethod
    def get_soup(cls, url, **kwargs):
        """Faz GET e retorna BeautifulSoup do HTML."""
        response = cls.get(url, **kwargs)
        return BeautifulSoup(response.content, "html.parser")

    @classmethod
    def get_json(cls, url, **kwargs):
        """Faz GET e retorna JSON parseado."""
        response = cls.get(url, **kwargs)
        return response.json()

    @classmethod
    def post_json(cls, url, **kwargs):
        """Faz POST e retorna JSON parseado."""
        response = cls.post(url, **kwargs)
        return response.json()

    @classmethod
    def extract_ld_json(cls, soup, index=0):
        """
        Extrai dados de <script type="application/ld+json"> do HTML.
        Retorna dict parseado ou None se nao encontrar.
        """
        scripts = soup.find_all("script", {"type": "application/ld+json"})
        if not scripts:
            logger.warning(f"[{cls.__name__}] Nenhum ld+json encontrado na pagina")
            return None

        if index >= len(scripts):
            logger.warning(
                f"[{cls.__name__}] Indice {index} fora do range (total: {len(scripts)} scripts ld+json)"
            )
            return None

        try:
            text = scripts[index].string or scripts[index].text
            return json.loads(text)
        except (json.JSONDecodeError, AttributeError) as e:
            logger.error(f"[{cls.__name__}] Erro ao parsear ld+json: {e}")
            return None

    @classmethod
    def find_ld_json_with_field(cls, soup, field):
        """
        Busca o primeiro ld+json que contenha um campo especifico.
        Mais robusto que buscar por indice fixo.
        """
        scripts = soup.find_all("script", {"type": "application/ld+json"})
        for script in scripts:
            try:
                text = script.string or script.text
                data = json.loads(text)
                if field in str(data):
                    return data
            except (json.JSONDecodeError, AttributeError):
                continue
        logger.warning(f"[{cls.__name__}] Nenhum ld+json com campo '{field}' encontrado")
        return None

    # --- Price helpers ---

    @classmethod
    def parse_price(cls, price_str):
        """
        Converte string de preco para float.
        Aceita formato brasileiro (R$ 1.234,56) e decimal padrao (129.90).
        Retorna None se nao conseguir converter.
        """
        if price_str is None:
            return None
        if isinstance(price_str, (int, float)):
            return float(price_str)

        cleaned = str(price_str).strip()
        cleaned = re.sub(r'[a-zA-Z$\s]', '', cleaned)

        if "," in cleaned:
            # Formato brasileiro: 1.234,56 -> 1234.56
            cleaned = cleaned.replace(".", "").replace(",", ".")
        # Se nao tem virgula, assume que "." ja e separador decimal (129.90)

        try:
            value = float(cleaned)
            return value if value > 0 else None
        except (ValueError, TypeError):
            logger.warning(f"[{cls.__name__}] Nao foi possivel converter preco: '{price_str}'")
            return None

    @classmethod
    def parse_deadline(cls, deadline_str):
        """
        Normaliza prazo de frete para string numerica.
        Ex: "5bd" -> "5", "10 dias uteis" -> "10", "3d" -> "3"
        """
        if deadline_str is None:
            return None
        text = str(deadline_str)
        numbers = re.findall(r'\d+', text)
        if numbers:
            return numbers[0]
        return None

    # --- Resultado padronizado ---

    @classmethod
    def build_result(cls, valor_produto=None, valor_frete=None, prazo_frete=None, **extra):
        """
        Monta o dicionario de resultado padronizado.
        Garante que os campos obrigatorios sempre existam.
        """
        result = {
            "valor_produto": valor_produto,
            "valor_frete": valor_frete,
            "prazo_frete": prazo_frete,
        }
        result.update(extra)
        return result

    @classmethod
    def validate_result(cls, result):
        """
        Valida o resultado do crawler.
        Loga warnings para campos ausentes ou suspeitos.
        Retorna o resultado (nao bloqueia).
        """
        if result.get("valor_produto") is None:
            logger.warning(f"[{cls.__name__}] valor_produto retornou None")

        price = result.get("valor_produto")
        if price is not None and (price <= 0 or price > 500000):
            logger.warning(f"[{cls.__name__}] valor_produto suspeito: {price}")

        freight = result.get("valor_frete")
        if freight is not None and isinstance(freight, (int, float)) and freight > 10000:
            logger.warning(f"[{cls.__name__}] valor_frete suspeito: {freight}")

        return result

    # --- SKU mapping helper ---

    @classmethod
    def get_product_id(cls, sku, d_para):
        """
        Busca ID do produto no mapeamento de-para.
        Lanca KeyError com mensagem clara se SKU nao existir.
        """
        if sku not in d_para:
            raise KeyError(
                f"[{cls.__name__}] SKU '{sku}' nao encontrado no mapeamento. "
                f"SKUs disponiveis: {list(d_para.keys())}"
            )
        return d_para[sku]

    # --- Metodo principal (cada subclasse implementa) ---

    @classmethod
    def crawler(cls, url, cep, sku, *args, **kwargs):
        """
        Metodo principal que cada crawler deve implementar.
        Subclasses devem sobrescrever este metodo.
        """
        raise NotImplementedError(
            f"{cls.__name__} precisa implementar o metodo crawler()"
        )
