# Scraping de Precos - Concorrentes

Sistema de coleta automatizada de precos e fretes de concorrentes em marketplaces brasileiros.

---

## Estrutura do Projeto

```
scraping review/
├── scripts/
│   ├── orchestrator.py              # Ponto de entrada unico (agendador + manual)
│   ├── sudeste.py                   # Script regional (legado, ainda funciona)
│   ├── nordeste.py
│   ├── norte.py
│   ├── sul.py
│   ├── centro_oeste.py
│   ├── efizi_marketplaces_*.py      # Scripts efizi marketplace (legado)
│   └── efizi_efizi.py               # Script efizi ecommerce (legado)
├── modules/
│   ├── base_crawler.py              # Classe base com retry, timeout, logging
│   ├── logging_config.py            # Configuracao de logs
│   ├── general.py                   # send_to_database, send_email_error
│   ├── efizitools.py                # BigQuery, Google Sheets, email
│   └── crawler_settings.py          # Utilitarios legados (Crawler)
├── marketplaces_crawlers/           # ~50 crawlers de lojas regionais
├── marketplaces_efizi/              # 6 crawlers de marketplaces (Magalu, ML, etc)
└── logs/                            # Logs diarios (crawlers_YYYY-MM-DD.log)
```

---

## Orchestrator (orchestrator.py)

Modulo unico que substitui os 11 scripts separados. Roda todas as regioes e tipos
por padrao, ou permite filtrar por loja, estado, regiao ou tipo.

### Uso Basico

```bash
# Rodar TUDO (usar no Agendador de Tarefas)
python scripts/orchestrator.py

# Ver o que seria executado sem rodar nada
python scripts/orchestrator.py --dry-run

# Listar todas as lojas disponiveis por regiao
python scripts/orchestrator.py --listar-lojas
```

### Filtros

```bash
# Por loja
python scripts/orchestrator.py --loja SODIMAC
python scripts/orchestrator.py --loja "LEROY MERLIN"
python scripts/orchestrator.py --loja SODIMAC BREMENKAMP

# Por estado
python scripts/orchestrator.py --estado SP
python scripts/orchestrator.py --estado SP MG RJ

# Por regiao
python scripts/orchestrator.py --regiao sudeste
python scripts/orchestrator.py --regiao sudeste nordeste

# Por tipo de execucao
python scripts/orchestrator.py --tipo regional              # So crawlers regionais
python scripts/orchestrator.py --tipo efizi_marketplace     # So efizi nos marketplaces
python scripts/orchestrator.py --tipo efizi_efizi           # So efizi ecommerce

# Combinar filtros
python scripts/orchestrator.py --regiao sudeste --estado SP --loja BREMENKAMP
python scripts/orchestrator.py --tipo regional --regiao sul --estado RS
```

### Regioes Disponiveis (--regiao)

| Regiao | Tipo | Estados |
|--------|------|---------|
| `sudeste` | regional | SP, MG, RJ, ES |
| `nordeste` | regional | BA, PB, MA, SE, CE, RN |
| `norte` | regional | TO |
| `sul` | regional | SC, RS, PR |
| `centro_oeste` | regional | GO, MT, DF, MS |
| `efizi_sudeste` | efizi_marketplace | SP, MG, RJ, ES |
| `efizi_nordeste` | efizi_marketplace | BA, PB, MA, SE, CE, RN, PI, PE, AL |
| `efizi_norte` | efizi_marketplace | TO |
| `efizi_sul` | efizi_marketplace | SC, RS, PR |
| `efizi_centro_oeste` | efizi_marketplace | GO, MT, DF, MS |
| `efizi_efizi` | efizi_efizi | (Google Sheets) |

### Tipos de Execucao (--tipo)

| Tipo | O que faz | Banco |
|------|-----------|-------|
| `regional` | Coleta precos de concorrentes regionais (~50 lojas) | Apenas INSERT |
| `efizi_marketplace` | Coleta precos da Efizi nos marketplaces (Magalu, ML, etc) | DELETE do dia + INSERT |
| `efizi_efizi` | Coleta precos do ecommerce Efizi (fonte: Google Sheets) | Apenas INSERT |

---

## Agendador de Tarefas (Windows)

### Configuracao

1. Abrir **Agendador de Tarefas** do Windows
2. Criar nova tarefa
3. Em **Acao**, configurar:
   - Programa: `python`
   - Argumentos: `scripts/orchestrator.py`
   - Iniciar em: `C:\Users\KayqueSantos\Desktop\dev\scraping review`
4. Configurar horario/frequencia desejada

### Variavel de Ambiente Necessaria

O sistema precisa da variavel de ambiente `REPOSITORY_PRICE` apontando para o diretorio do projeto:

```
REPOSITORY_PRICE=C:\Users\KayqueSantos\Desktop\dev\competitor_price_crawler
```

---

## BaseCrawler (base_crawler.py)

Classe base que todos os crawlers herdam. Fornece:

- **Timeout**: 15 segundos por requisicao
- **Retry com backoff**: 3 tentativas (2s, 4s, 8s de espera)
- **Logging estruturado**: warnings e erros gravados em `logs/crawlers_YYYY-MM-DD.log`
- **Validacao de resultado**: alerta para valores None, negativos ou suspeitos
- **Rate limiting**: 1 segundo entre requisicoes
- **Tratamento de excecoes especificas**: sem `except:` generico

### Metodos Principais

| Metodo | Descricao |
|--------|-----------|
| `get_soup(url)` | Requisicao GET + BeautifulSoup |
| `get_json(url)` | Requisicao GET retornando JSON |
| `post_json(url, ...)` | Requisicao POST retornando JSON |
| `extract_ld_json(soup)` | Extrai dados de `<script type="application/ld+json">` |
| `parse_price(price_str)` | Converte "R$ 1.234,56" ou "129.90" para float |
| `build_result(...)` | Monta dict padrao {valor_produto, valor_frete, prazo_frete} |
| `validate_result(result)` | Valida e loga warnings para valores suspeitos |
| `get_product_id(sku, d_para)` | Busca SKU no dicionario de-para com erro claro |

---

## Logs

Os logs ficam em `logs/crawlers_YYYY-MM-DD.log` (um arquivo por dia).

- **Console**: nivel INFO (tudo aparece)
- **Arquivo**: nivel WARNING (so warnings e erros sao gravados)

Exemplo de log:

```
[2026-03-03 10:30:15] WARNING - [Sodimac] Erro ao extrair preco de https://...: KeyError
[2026-03-03 10:30:18] WARNING - [BaseCrawler] valor_produto is None
[2026-03-03 10:30:20] ERROR - [VilaTelhas] Erro de rede ao acessar https://...: ConnectionError
```

---

## Lojas por Regiao

### Sudeste (SP, MG, RJ, ES)

AMOEDO, BABA MATERIAIS, BALAROTI, BARATAO DA CONSTRUCAO, BREMENKAMP,
CACIQUE HOME CENTER, CARREFOUR, CASA MATTOS, CASA MIMOSA, CHATUBA,
CONSTRUBEL, COPAFER, GUEMAT, LEROY MERLIN, LOJAS PEDRAO, OBRAMAX,
PADOVANI, SODIMAC, TROPEIRO, VILA TELHAS

### Nordeste (BA, PB, MA, SE, CE, RN)

ACAL HOME CENTER, AFP CONSTRUCAO, CARAJAS, CARREFOUR, CASA FACIL CONSTRUCAO,
ENGECOPI, FERREIRA COSTA, LEROY MERLIN, NORMATEL, PARAIBA HOME CENTER,
PISOLAR, POTIGUAR, VENEZA

### Norte (TO)

CARREFOUR, FERPAM, JL MEURER, LEROY MERLIN

### Sul (SC, RS, PR)

BALAROTI, BIGOLIN, CARREFOUR, CASAS DA AGUA, LEROY MERLIN,
PANORAMA, QUEVEDO, REDEMAC, TAQI

### Centro-Oeste (GO, MT, DF, MS)

CAMPEAO DA CONSTRUCAO, CARREFOUR, CASTELO FORTE, CONSTRULAR FACIL,
LEROY MERLIN, SERPAL, SERTAO, TODIMO, WANDERSON MATERIAIS

### Efizi Marketplaces (todas regioes)

EFIZI CARREFOUR, EFIZI LEROY MERLIN, EFIZI MADEIRA MADEIRA,
EFIZI MAGALU, EFIZI MERCADO LIVRE

---

## Fluxo de Dados

```
BigQuery (bi.produtos_sites)     Google Sheets (Efizi)
         |                                |
         v                                v
   Orchestrator                    Orchestrator
         |                                |
         v                                v
   Crawler.crawler(url, cep, sku)  EfiziEcommerce.crawler(...)
         |                                |
         v                                v
   {valor_produto, valor_frete,    {valor_produto, valor_frete,
    prazo_frete}                    prazo_frete}
         |                                |
         v                                v
   General.send_to_database() --> BigQuery (bi.precos_produtos_sites)
```

---

## Adicionando uma Nova Loja

1. Criar o crawler em `marketplaces_crawlers/nova_loja.py` herdando de `BaseCrawler`
2. Adicionar o mapeamento em `scripts/orchestrator.py` no `REGION_CONFIG` da regiao correspondente:
   ```python
   "NOVA LOJA": ("marketplaces_crawlers.nova_loja", "NovaLoja"),
   ```
3. Se a loja tiver assinatura especial (mais que `url, cep, sku`), adicionar em `get_signature_type()`
4. Cadastrar os produtos/links no BigQuery (`bi.produtos_sites`)
