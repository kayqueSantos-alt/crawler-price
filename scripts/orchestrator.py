import sys
import os
import json
import logging
import importlib
import argparse
from datetime import datetime

path = os.getenv('REPOSITORY_PRICE')
sys.path.append(path)

# Adiciona o diretorio raiz do projeto (pai de scripts/) ao path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.logging_config import setup_logging
setup_logging()

from modules.general import General
from modules.efizitools import Efizi

logger = logging.getLogger("crawlers")

# ============================================================
# CONFIGURACAO DE REGIOES — crawlers regionais (concorrentes)
# Cada entrada: "NOME DA LOJA": ("modulo.path", "NomeClasse")
# ============================================================

REGION_CONFIG = {
    "sudeste": {
        "states": ["SP_INTERIOR","SP_CAPITAL", "MG", "RJ", "ES"],
        "cep_source": "bigquery",
        "crawlers": {
            "AMOEDO": ("marketplaces_crawlers.amoedo", "Amoedo"),
            "BABA MATERIAIS": ("marketplaces_crawlers.baba_materiais", "BabaMateriais"),
            "BALAROTI": ("marketplaces_crawlers.balaroti", "Balaroti"),
            "BARATÃO DA CONSTRUÇÃO": ("marketplaces_crawlers.baratao_construcao", "Baratao"),
            "BREMENKAMP": ("marketplaces_crawlers.bremenkamp", "Bremenkamp"),
            "CACIQUE HOME CENTER": ("marketplaces_crawlers.cacique", "Cacique"),
            "CARREFOUR": ("marketplaces_efizi.carrefour", "Carrefour"),
            "CASA MATTOS": ("marketplaces_crawlers.casa_mattos", "CasaMattos"),
            "CASA MIMOSA": ("marketplaces_crawlers.casa_mimosa", "CasaMimosa"),
            "CHATUBA": ("marketplaces_crawlers.chatuba", "Chatuba"),
            "CONSTRUBEL": ("marketplaces_crawlers.construbel", "Construbel"),
            "COPAFER": ("marketplaces_crawlers.copafer", "Copafer"),
            "EFIZI MADEIRA MADEIRA": ("marketplaces_efizi.madeiramadeira", "MadeiraMadeira"),
            "EFIZI MAGALU": ("marketplaces_efizi.magalu", "Magalu"),
            "EFIZI MERCADO LIVRE": ("marketplaces_efizi.mercado_livre", "MercadoLivre"),
            "GUEMAT": ("marketplaces_crawlers.guemat", "Guemat"),
            "LEROY MERLIN": ("marketplaces_crawlers.leroy_merlin", "Leroy"),
            "LOJAS PEDRAO": ("marketplaces_crawlers.lojas_pedrao", "LojasPedrao"),
            "OBRAMAX": ("marketplaces_crawlers.obramax", "Obramax"),
            "PADOVANI": ("marketplaces_crawlers.padovani", "Padovani"),
            "SODIMAC": ("marketplaces_crawlers.sodimac", "Sodimac"),
            "TROPEIRO": ("marketplaces_crawlers.hidraulico_tropeiro", "Tropeiro"),
            "VILA TELHAS": ("marketplaces_crawlers.vila_telhas", "VilaTelhas"),
        },
    },
    "nordeste": {
        "states": ["BA", "PB", "MA", "SE", "CE", "RN"],
        "cep_source": "row",
        "crawlers": {
            "ACAL HOME CENTER": ("marketplaces_crawlers.acal_home_center", "AcalHomeCenter"),
            "AFP CONSTRUCAO": ("marketplaces_crawlers.afp", "AFP"),
            "CARAJÁS": ("marketplaces_crawlers.carajas", "Carajas"),
            "CARREFOUR": ("marketplaces_efizi.carrefour", "Carrefour"),
            "CASA FACIL CONSTRUÇÃO": ("marketplaces_crawlers.casamaisfacil", "CasaMaisFacil"),
            "EFIZI MADEIRA MADEIRA": ("marketplaces_efizi.madeiramadeira", "MadeiraMadeira"),
            "EFIZI MAGALU": ("marketplaces_efizi.magalu", "Magalu"),
            "EFIZI MERCADO LIVRE": ("marketplaces_efizi.mercado_livre", "MercadoLivre"),
            "ENGECOPI": ("marketplaces_crawlers.engecopi", "Engecopi"),
            "FERREIRA COSTA": ("marketplaces_crawlers.ferreira_costa", "FerreiraCosta"),
            "LEROY MERLIN": ("marketplaces_crawlers.leroy_merlin", "Leroy"),
            "NORMATEL": ("marketplaces_crawlers.normatel", "Normatel"),
            "PARAIBA HOME CENTER": ("marketplaces_crawlers.paraibaHomeCenter", "ParaibaHomeCenter"),
            "PISOLAR": ("marketplaces_crawlers.pisolar", "Pisolar"),
            "POTIGUAR": ("marketplaces_crawlers.potiguar", "Potiguar"),
            "VENEZA": ("marketplaces_crawlers.veneza", "Veneza"),
        },
    },
    "norte": {
        "states": ["TO"],
        "cep_source": "row",
        "crawlers": {
            "CARREFOUR": ("marketplaces_efizi.carrefour", "Carrefour"),
            "EFIZI VIA VAREJO": ("marketplaces_efizi.via_varejo", "ViaVarejo"),
            "EFIZI MADEIRA MADEIRA": ("marketplaces_efizi.madeiramadeira", "MadeiraMadeira"),
            "EFIZI MAGALU": ("marketplaces_efizi.magalu", "Magalu"),
            "EFIZI MERCADO LIVRE": ("marketplaces_efizi.mercado_livre", "MercadoLivre"),
            "FERPAM": ("marketplaces_crawlers.ferpam", "Ferpam"),
            "JL MEURER": ("marketplaces_crawlers.jl_meurer", "Jl_meurer"),
            "LEROY MERLIN": ("marketplaces_crawlers.leroy_merlin", "Leroy"),
        },
    },
    "sul": {
        "states": ["SC", "RS", "PR"],
        "cep_source": "row",
        "crawlers": {
            "BALAROTI": ("marketplaces_crawlers.balaroti", "Balaroti"),
            "BIGOLIN": ("marketplaces_crawlers.bigolin", "Bigolin"),
            "CARREFOUR": ("marketplaces_efizi.carrefour", "Carrefour"),
            "CASAS DA AGUA": ("marketplaces_crawlers.casas_da_agua", "Casas_da_agua"),
            "EFIZI MADEIRA MADEIRA": ("marketplaces_efizi.madeiramadeira", "MadeiraMadeira"),
            "EFIZI MAGALU": ("marketplaces_efizi.magalu", "Magalu"),
            "EFIZI MERCADO LIVRE": ("marketplaces_efizi.mercado_livre", "MercadoLivre"),
            "LEROY MERLIN": ("marketplaces_crawlers.leroy_merlin", "Leroy"),
            "PANORAMA": ("marketplaces_crawlers.panorama", "Panorama"),
            "QUEVEDO": ("marketplaces_crawlers.quevedo", "Quevedo"),
            "REDEMAC": ("marketplaces_crawlers.redemac", "Redemac"),
            "TAQI": ("marketplaces_crawlers.taqi", "Taqi"),
        },
    },
    "centro_oeste": {
        "states": ["GO", "MT", "DF", "MS"],
        "cep_source": "row",
        "crawlers": {
            "CAMPEÃO DA CONSTRUÇÃO": ("marketplaces_crawlers.campeao_da_construcao", "Campeao_da_construcao"),
            "CARREFOUR": ("marketplaces_efizi.carrefour", "Carrefour"),
            "CASTELO FORTE": ("marketplaces_crawlers.castelo_forte", "Castelo_forte"),
            "CONSTRULAR FÁCIL": ("marketplaces_crawlers.constrular_facil", "Constrular_facil"),
            "EFIZI MADEIRA MADEIRA": ("marketplaces_efizi.madeiramadeira", "MadeiraMadeira"),
            "EFIZI MAGALU": ("marketplaces_efizi.magalu", "Magalu"),
            "EFIZI MERCADO LIVRE": ("marketplaces_efizi.mercado_livre", "MercadoLivre"),
            "LEROY MERLIN": ("marketplaces_crawlers.leroy_merlin", "Leroy"),
            "SERPAL": ("marketplaces_crawlers.serpal", "Serpal"),
            "SERTAO": ("marketplaces_crawlers.sertao", "Sertao"),
            "TODIMO": ("marketplaces_crawlers.todimo", "Todimo"),
            "WANDERSON MATERIAIS": ("marketplaces_crawlers.wanderson_materiais", "WandersonMateriais"),
        },
    },
}

# ============================================================
# CONFIGURACAO EFIZI MARKETPLACES — mesmos crawlers, estados diferentes
# ============================================================

_EFIZI_MKT_CRAWLERS = {
    "EFIZI CARREFOUR": ("marketplaces_efizi.carrefour", "Carrefour"),
    "EFIZI LEROY MERLIN": ("marketplaces_crawlers.leroy_merlin", "Leroy"),
    "EFIZI MAGALU": ("marketplaces_efizi.magalu", "Magalu"),
    "EFIZI MERCADO LIVRE": ("marketplaces_efizi.mercado_livre", "MercadoLivre"),
    "EFIZI MADEIRA MADEIRA": ("marketplaces_efizi.madeiramadeira", "MadeiraMadeira"),
}

EFIZI_MARKETPLACES_CONFIG = {
    "efizi_sudeste": {
        "states": ["SP", "MG", "RJ", "ES"],
        "crawlers": _EFIZI_MKT_CRAWLERS,
    },
    "efizi_nordeste": {
        "states": ["BA", "PB", "MA", "SE", "CE", "RN", "PI", "PE", "AL"],
        "crawlers": _EFIZI_MKT_CRAWLERS,
    },
    "efizi_norte": {
        "states": ["TO"],
        "crawlers": _EFIZI_MKT_CRAWLERS,
    },
    "efizi_sul": {
        "states": ["SC", "RS", "PR"],
        "crawlers": _EFIZI_MKT_CRAWLERS,
    },
    "efizi_centro_oeste": {
        "states": ["GO", "MT", "DF", "MS"],
        "crawlers": _EFIZI_MKT_CRAWLERS,
    },
}

# ============================================================
# IMPORT DINAMICO COM CACHE
# ============================================================

_crawler_cache = {}


def load_crawler(module_path, class_name):
    cache_key = f"{module_path}.{class_name}"
    if cache_key not in _crawler_cache:
        module = importlib.import_module(module_path)
        _crawler_cache[cache_key] = getattr(module, class_name)
    return _crawler_cache[cache_key]


# ============================================================
# DISPATCHER — determina assinatura e chama o crawler certo
# ============================================================

def get_signature_type(loja_name):
    """Substring match para preservar o comportamento dos scripts originais."""
    if "FERREIRA COSTA" in loja_name:
        return "ferreira"
    if "LEROY MERLIN" in loja_name:
        return "leroy"
    if "CARREFOUR" in loja_name:
        return "carrefour"
    if "MERCADO LIVRE" in loja_name:
        return "marketplace"
    if "MAGALU" in loja_name:
        return "marketplace"
    return "default"


def find_crawler_in_dict(loja_name, crawlers_dict):
    """Busca exata primeiro, depois substring para lojas especiais."""
    if loja_name in crawlers_dict:
        return crawlers_dict[loja_name]
    for key in crawlers_dict:
        if key in loja_name:
            return crawlers_dict[key]
    return None


def call_crawler(loja_name, crawler_class, row, cep, data_product, state):
    sig = get_signature_type(loja_name)
    if sig == "leroy":
        return crawler_class.crawler(row["LINK"], cep, row["SKU"], row["LOJA"])
    elif sig == "carrefour":
        return crawler_class.crawler(row["LINK"], cep, row["SKU"], row["LOJA"], data_product)
    elif sig == "marketplace":
        return crawler_class.crawler(row["LINK"], cep, row["SKU"], row["LOJA"], data_product)
    elif sig == "ferreira":
        return crawler_class.crawler(row["LINK"], cep, row["SKU"], state)
    else:
        return crawler_class.crawler(row["LINK"], cep, row["SKU"])


# ============================================================
# FILTRO DE LOJAS — verifica se loja esta nos filtros do usuario
# ============================================================

def loja_matches_filter(loja_name, filter_lojas):
    """Retorna True se a loja passa no filtro (ou se nao ha filtro)."""
    if not filter_lojas:
        return True
    for fl in filter_lojas:
        if fl.upper() in loja_name.upper() or loja_name.upper() in fl.upper():
            return True
    return False


# ============================================================
# RUNNER A — REGIONAIS (concorrentes)
# ============================================================

def run_regional(region_name, config, credentials, data_product, ceps_df,
                 filter_states=None, filter_lojas=None, sem_efizi=False):
    logger.info(f"=== REGIONAL: {region_name.upper()} ===")

    states = config["states"]
    if filter_states:
        states = [s for s in states if s in filter_states]
    if not states:
        return

    # Importa apenas crawlers necessarios
    crawlers_dict = {}
    for store_name, (mod, cls) in config["crawlers"].items():
        if sem_efizi and store_name.upper().startswith("EFIZI"):
            continue
        if not loja_matches_filter(store_name, filter_lojas):
            continue
        try:
            crawlers_dict[store_name] = load_crawler(mod, cls)
        except Exception as e:
            logger.error(f"Erro ao importar {store_name} ({mod}.{cls}): {e}")
    if not crawlers_dict:
        logger.info(f"Nenhuma loja para processar em {region_name}")
        return

    # Query produtos
    region_products = Efizi.get_bigquery(
        f"select * from bi.produtos_sites where estado in ({str(states)[1:-1]})",
        "efizi-analises", credentials
    )

    for state in states:
        try:
            # CEP: tabela bi.ceps para sudeste, row["CEP"] para o resto
            cep_from_table = None
            if config["cep_source"] == "bigquery" and ceps_df is not None:
                if state == "SP_CAPITAL":
                    ceps_do_estado = ceps_df[(ceps_df["UF"] == "SP") & (ceps_df["LOCALIDADE"] == "Capital")]
                elif state == "SP_INTERIOR":
                    ceps_do_estado = ceps_df[(ceps_df["UF"] == "SP") & (ceps_df["LOCALIDADE"] == "Interior")]
                else:
                    ceps_do_estado = ceps_df[ceps_df["UF"] == state]
                if ceps_do_estado.empty:
                    logger.warning(f"Nenhum CEP em bi.ceps para {state}, pulando")
                    continue
                cep_from_table = str(ceps_do_estado.iloc[0]['CEP']).replace("-", "").strip()

            competitors_state = region_products[region_products["ESTADO"] == state]
            list_prices = []

            logger.info(f"Processando {state} ({len(competitors_state)} produtos)")

            for index, row in competitors_state.iterrows():
                try:
                    loja_name = row["LOJA"]

                    # Verifica filtro de loja no nivel do produto
                    if filter_lojas and not loja_matches_filter(loja_name, filter_lojas):
                        continue

                    crawler_class = find_crawler_in_dict(loja_name, crawlers_dict)
                    if crawler_class is None:
                        continue

                    cep = cep_from_table if cep_from_table else row["CEP"]

                    prod_obj = call_crawler(loja_name, crawler_class, row, cep, data_product, state)

                    prod_obj["cep"] = cep
                    prod_obj["estado"] = state
                    prod_obj["loja"] = loja_name
                    prod_obj["link"] = row["LINK"]
                    prod_obj["sku"] = row["SKU"]
                    prod_obj["produto"] = row["PRODUTO"]

                    valor = prod_obj.get("valor_produto", "N/A")
                    frete = prod_obj.get("valor_frete", "N/A")
                    logger.info(
                        f"[{state}] {loja_name} | SKU: {row['SKU']} | "
                        f"{row['PRODUTO']} | Valor: {valor} | Frete: {frete}"
                    )

                    list_prices.append(prod_obj.copy())

                except Exception as e:
                    cep_err = cep_from_table if cep_from_table else row.get("CEP", "")
                    logger.warning(
                        f"[{state}] ERRO {row['LOJA']} | SKU: {row['SKU']} | "
                        f"{row.get('PRODUTO', '?')} | {type(e).__name__}: {e}"
                    )
                    try:
                        General.send_email_error(state, str(e), cep_err, row["LOJA"], row["SKU"], row["LINK"])
                    except Exception as email_err:
                        logger.error(f"Falha ao enviar email de erro: {email_err}")

            if list_prices:
                General.send_to_database(list_prices)
                logger.info(f"Dados salvos para {state} ({len(list_prices)} itens)")

        except Exception as e:
            logger.error(f"ERRO CRITICO no estado {state}: {e}")
            try:
                General.send_email_error(state, str(e))
            except Exception as email_err:
                logger.error(f"Falha ao enviar email de erro: {email_err}")


# ============================================================
# RUNNER B — EFIZI MARKETPLACES (delete + insert)
# ============================================================

def run_efizi_marketplace(region_name, config, credentials, data_product,
                          filter_states=None, filter_lojas=None):
    from pandas import DataFrame

    logger.info(f"=== EFIZI MARKETPLACE: {region_name.upper()} ===")

    states = config["states"]
    if filter_states:
        states = [s for s in states if s in filter_states]
    if not states:
        return

    # Importa crawlers
    crawlers_dict = {}
    for store_name, (mod, cls) in config["crawlers"].items():
        if not loja_matches_filter(store_name, filter_lojas):
            continue
        try:
            crawlers_dict[store_name] = load_crawler(mod, cls)
        except Exception as e:
            logger.error(f"Erro ao importar {store_name} ({mod}.{cls}): {e}")
    if not crawlers_dict:
        return

    hoje = datetime.now().strftime("%Y-%m-%d")

    # Query filtrando por lojas efizi (mesmo padrao dos scripts originais)
    store_names = list(crawlers_dict.keys())
    region_products = Efizi.get_bigquery(
        f"select LOJA, LINK, SKU, PRODUTO, CEP, ESTADO from bi.produtos_sites "
        f"where LOJA in ({str(store_names)[1:-1]}) "
        f"and LOJA not in ('EFIZI VIA VAREJO', 'EFIZI CARREFOUR')",
        "efizi-analises", credentials
    )

    for state in states:
        try:
            competitors_state = region_products[region_products["ESTADO"] == state]
            list_prices = []

            logger.info(f"Efizi MKT processando {state} ({len(competitors_state)} produtos)")

            for index, row in competitors_state.iterrows():
                try:
                    loja_name = row["LOJA"]

                    if filter_lojas and not loja_matches_filter(loja_name, filter_lojas):
                        continue

                    crawler_class = find_crawler_in_dict(loja_name, crawlers_dict)
                    if crawler_class is None:
                        continue

                    cep = row["CEP"]
                    prod_obj = call_crawler(loja_name, crawler_class, row, cep, data_product, state)

                    prod_obj["cep"] = cep
                    prod_obj["estado"] = state
                    prod_obj["loja"] = loja_name
                    prod_obj["link"] = row["LINK"]
                    prod_obj["sku"] = row["SKU"]
                    prod_obj["produto"] = row["PRODUTO"]

                    valor = prod_obj.get("valor_produto", "N/A")
                    frete = prod_obj.get("valor_frete", "N/A")
                    logger.info(
                        f"[{state}] {loja_name} | SKU: {row['SKU']} | "
                        f"{row['PRODUTO']} | Valor: {valor} | Frete: {frete}"
                    )

                    list_prices.append(prod_obj.copy())

                except Exception as e:
                    logger.warning(
                        f"[{state}] ERRO {row['LOJA']} | SKU: {row['SKU']} | "
                        f"{row.get('PRODUTO', '?')} | {type(e).__name__}: {e}"
                    )
                    try:
                        General.send_email_error(state, str(e), row["CEP"], row["LOJA"], row["SKU"], row["LINK"])
                    except Exception as email_err:
                        logger.error(f"Falha ao enviar email de erro: {email_err}")

            if list_prices:
                data = DataFrame(list_prices)

                # SP_INTERIOR / SP_CAPITAL remapping (so para efizi_sudeste)
                if region_name == "efizi_sudeste":
                    data.loc[data["cep"].isin([
                        "13310-161", "13308-096", "14050-050",
                        "14095-180", "13400-050", "18190-000"
                    ]), "estado"] = "SP_INTERIOR"
                    data.loc[data["cep"].isin([
                        "01050-050", "01420-001"
                    ]), "estado"] = "SP_CAPITAL"

                lojas = list({obj["loja"] for obj in list_prices})

                # DELETE dados do dia antes de inserir
                Efizi.get_bigquery(
                    f"delete from bi.precos_produtos_sites "
                    f"where estado in ({str(list(data['estado'].unique()))[1:-1]}) "
                    f"and dia = '{hoje}' "
                    f"and loja in ({str(lojas)[1:-1]})",
                    "efizi-analises", credentials
                )

                General.send_to_database(list_prices)
                logger.info(f"Efizi MKT dados salvos para {state} ({len(list_prices)} itens)")

        except Exception as e:
            logger.error(f"ERRO CRITICO efizi marketplace {state}: {e}")
            try:
                General.send_email_error(state, str(e))
            except Exception as email_err:
                logger.error(f"Falha ao enviar email de erro: {email_err}")


# ============================================================
# RUNNER C — EFIZI ECOMMERCE (Google Sheets)
# ============================================================

def run_efizi_efizi():
    logger.info("=== EFIZI ECOMMERCE ===")

    credentials_bi = Efizi.get_credentials("CREDENTIALS_BI")
    credentials_bi = json.loads(credentials_bi)

    EfiziEcommerce = load_crawler("marketplaces_efizi.efizi", "EfiziEcommerce")

    prices_links = Efizi.read_sheet(
        "1LjbYLnyVU_kn8zqwa7lw1Wh_DbFhyaHWBxFbpzF2-kI",
        "EFZ",
        path + "/credentials/service_account_google_sheets.json"
    )

    for index, row in prices_links.iterrows():
        try:
            if row["LOJA"] == "EFIZI":
                efizi_prices = EfiziEcommerce.crawler(
                    row["LINK"], row["LOJA"], row["SKU"], row["PRODUTO"]
                )
                logger.info(
                    f"[EFIZI] SKU: {row['SKU']} | {row['PRODUTO']} | "
                    f"{len(efizi_prices)} registros"
                )
                General.send_to_database(efizi_prices)
        except Exception as e:
            tb = sys.exc_info()[2]
            lineno = tb.tb_lineno
            Efizi.send_email(
                credentials_bi["email"],
                credentials_bi["password"],
                "ti@efizi.com.br",
                "[ERRO] PRECOS EFIZI",
                f"""
                    Houve erro no seguinte passo:
                    Loja: {row["LOJA"]}
                    Sku: {row["SKU"]}
                    Link: {row["LINK"]}
                    Erro na linha: {lineno}
                    {str(e)}
                """,
                "plain"
            )

    logger.info("Efizi ecommerce finalizado")


# ============================================================
# LISTAR LOJAS
# ============================================================

def listar_lojas():
    print("\n========== LOJAS POR REGIAO (REGIONAL) ==========\n")
    for region, config in REGION_CONFIG.items():
        print(f"  {region.upper()} ({', '.join(config['states'])})")
        for loja in sorted(config["crawlers"].keys()):
            print(f"    - {loja}")
        print()

    print("========== LOJAS EFIZI MARKETPLACES ==========\n")
    print(f"  Lojas (todas regioes):")
    for loja in sorted(_EFIZI_MKT_CRAWLERS.keys()):
        print(f"    - {loja}")
    print()
    for region, config in EFIZI_MARKETPLACES_CONFIG.items():
        print(f"  {region.upper()}: {', '.join(config['states'])}")
    print()

    print("========== EFIZI ECOMMERCE ==========\n")
    print("  Fonte: Google Sheets")
    print("  Crawler: EfiziEcommerce")
    print()


# ============================================================
# CLI
# ============================================================

def parse_args():
    all_regions = list(REGION_CONFIG.keys()) + list(EFIZI_MARKETPLACES_CONFIG.keys()) + ["efizi_efizi"]

    parser = argparse.ArgumentParser(
        description="Orchestrator - Coleta de precos de concorrentes"
    )
    parser.add_argument(
        "--regiao", nargs="+", choices=all_regions,
        help="Regioes a executar. Sem argumento = todas."
    )
    parser.add_argument(
        "--estado", nargs="+",
        help="Filtrar por estados (ex: SP MG RJ)"
    )
    parser.add_argument(
        "--loja", nargs="+",
        help="Filtrar por loja (ex: SODIMAC 'LEROY MERLIN')"
    )
    parser.add_argument(
        "--tipo", nargs="+",
        choices=["regional", "efizi_marketplace", "efizi_efizi"],
        help="Tipo de execucao. Sem argumento = todos."
    )
    parser.add_argument(
        "--sem-efizi", action="store_true",
        help="Exclui todos os crawlers EFIZI (marketplace, ecommerce e lojas EFIZI dentro das regionais)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Mostra o que seria executado sem rodar crawlers"
    )
    parser.add_argument(
        "--listar-lojas", action="store_true",
        help="Lista todas as lojas disponiveis por regiao"
    )
    return parser.parse_args()


# ============================================================
# MAIN
# ============================================================

def main():
    args = parse_args()

    if args.listar_lojas:
        listar_lojas()
        return

    logger.info("=" * 60)
    logger.info("ORCHESTRATOR INICIADO")
    logger.info(f"Filtros: regiao={args.regiao}, estado={args.estado}, loja={args.loja}, tipo={args.tipo}, sem_efizi={args.sem_efizi}")
    logger.info("=" * 60)

    # Flags de tipo
    should_run_regional = args.tipo is None or "regional" in args.tipo
    should_run_efizi_mkt = (args.tipo is None or "efizi_marketplace" in args.tipo) and not args.sem_efizi
    should_run_efizi_ecom = (args.tipo is None or "efizi_efizi" in args.tipo) and not args.sem_efizi

    # Credenciais (carrega uma vez)
    credentials = Efizi.load_json_credentials(credentials="./google_cloud_producao.json")

    # data_product (usado por Carrefour, MercadoLivre, Magalu)
    data_product = Efizi.get_bigquery(
        "select sku, altura, categoria, largura, comprimento, peso from bi.categoria_fr",
        "efizi-analises", credentials
    )

    # CEPs (so carrega se sudeste regional vai rodar)
    ceps_df = None
    sudeste_will_run = should_run_regional and (args.regiao is None or "sudeste" in args.regiao)
    if sudeste_will_run:
        ceps_df = Efizi.get_bigquery(
            "select UF, LOCALIDADE, CEP from bi.ceps",
            "efizi-analises", credentials
        )

    contadores = {"regioes": 0, "erros_importacao": 0}

    # --- REGIONAIS ---
    if should_run_regional:
        for region_name, config in REGION_CONFIG.items():
            if args.regiao and region_name not in args.regiao:
                continue

            if args.dry_run:
                states = config["states"]
                if args.estado:
                    states = [s for s in states if s in args.estado]
                lojas = [l for l in config["crawlers"].keys()
                         if loja_matches_filter(l, args.loja)
                         and not (args.sem_efizi and l.upper().startswith("EFIZI"))]
                print(f"[DRY RUN] Regional: {region_name.upper()}")
                print(f"  Estados: {states}")
                print(f"  Lojas ({len(lojas)}): {', '.join(sorted(lojas))}")
                print()
                continue

            run_regional(
                region_name, config, credentials, data_product, ceps_df,
                filter_states=args.estado, filter_lojas=args.loja,
                sem_efizi=args.sem_efizi
            )
            contadores["regioes"] += 1

    # --- EFIZI MARKETPLACES ---
    if should_run_efizi_mkt:
        for region_name, config in EFIZI_MARKETPLACES_CONFIG.items():
            if args.regiao and region_name not in args.regiao:
                continue

            if args.dry_run:
                states = config["states"]
                if args.estado:
                    states = [s for s in states if s in args.estado]
                lojas = [l for l in config["crawlers"].keys() if loja_matches_filter(l, args.loja)]
                print(f"[DRY RUN] Efizi MKT: {region_name.upper()}")
                print(f"  Estados: {states}")
                print(f"  Lojas ({len(lojas)}): {', '.join(sorted(lojas))}")
                print()
                continue

            run_efizi_marketplace(
                region_name, config, credentials, data_product,
                filter_states=args.estado, filter_lojas=args.loja
            )
            contadores["regioes"] += 1

    # --- EFIZI ECOMMERCE ---
    if should_run_efizi_ecom:
        if args.regiao is None or "efizi_efizi" in args.regiao:
            if args.dry_run:
                print("[DRY RUN] Efizi Ecommerce (Google Sheets)")
                print()
            else:
                run_efizi_efizi()
                contadores["regioes"] += 1

    logger.info("=" * 60)
    logger.info(f"ORCHESTRATOR FINALIZADO - {contadores['regioes']} blocos executados")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
