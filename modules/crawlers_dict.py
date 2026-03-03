# from modules.efizitools import Efizi
from marketplaces_crawlers.afp import AFP
from marketplaces_crawlers.taqi import Taqi
from marketplaces_efizi.magalu import Magalu
from marketplaces_crawlers.todimo import Todimo
from marketplaces_crawlers.serpal import Serpal
from marketplaces_crawlers.sertao import Sertao
from marketplaces_crawlers.veneza import Veneza
from marketplaces_crawlers.ferpam import Ferpam
from marketplaces_crawlers.amoedo import Amoedo
from marketplaces_crawlers.guemat import Guemat
from marketplaces_efizi.carrefour import Carrefour
from marketplaces_crawlers.carajas import Carajas
from marketplaces_crawlers.pisolar import Pisolar
from marketplaces_crawlers.sodimac import Sodimac
from marketplaces_crawlers.obramax import Obramax
from marketplaces_crawlers.cacique import Cacique
from marketplaces_crawlers.chatuba import Chatuba
from marketplaces_crawlers.copafer import Copafer
from marketplaces_crawlers.quevedo import Quevedo
from marketplaces_crawlers.bigolin import Bigolin
from marketplaces_crawlers.redemac import Redemac
from marketplaces_crawlers.potiguar import Potiguar
from marketplaces_crawlers.engecopi import Engecopi
from marketplaces_crawlers.normatel import Normatel
from marketplaces_crawlers.padovani import Padovani
from marketplaces_crawlers.balaroti import Balaroti
from marketplaces_crawlers.panorama import Panorama
from marketplaces_efizi.via_varejo import ViaVarejo
from marketplaces_crawlers.leroy_merlin import Leroy
from marketplaces_efizi.quero_quero import QueroQuero
from marketplaces_crawlers.jl_meurer import Jl_meurer
from marketplaces_crawlers.lojas2001 import Lojas2001
from marketplaces_crawlers.construbel import Construbel
from marketplaces_crawlers.bremenkamp import Bremenkamp
from marketplaces_crawlers.casa_mimosa import CasaMimosa
from marketplaces_crawlers.casa_mattos import CasaMattos
from marketplaces_crawlers.vila_telhas import VilaTelhas
from marketplaces_efizi.mercado_livre import MercadoLivre
from marketplaces_crawlers.lojas_pedrao import LojasPedrao
from marketplaces_crawlers.constru_shop import ConstruShop
from marketplaces_crawlers.baratao_construcao import Baratao
from marketplaces_efizi.madeiramadeira import MadeiraMadeira
from marketplaces_crawlers.casas_da_agua import Casas_da_agua
from marketplaces_crawlers.castelo_forte import Castelo_forte
from marketplaces_crawlers.casamaisfacil import CasaMaisFacil
from marketplaces_crawlers.baba_materiais import BabaMateriais
from marketplaces_crawlers.hidraulico_tropeiro import Tropeiro
from marketplaces_crawlers.ferreira_costa import FerreiraCosta
from marketplaces_crawlers.acal_home_center import AcalHomeCenter
from marketplaces_crawlers.constrular_facil import Constrular_facil
from marketplaces_crawlers.paraibaHomeCenter import ParaibaHomeCenter
from marketplaces_crawlers.wanderson_materiais import WandersonMateriais
from marketplaces_crawlers.campeao_da_construcao import Campeao_da_construcao

def crawlers():
    return {
        "ACAL HOME CENTER": AcalHomeCenter,
        "AFP CONSTRUCAO": AFP,
        "AMOEDO": Amoedo,
        "BABA MATERIAIS": BabaMateriais,
        "BALAROTI": Balaroti,
        "BARATÃO DA CONSTRUÇÃO": Baratao,
        "BIGOLIN": Bigolin,
        "BREMENKAMP": Bremenkamp,
        "CACIQUE HOME CENTER": Cacique,
        # "CARREFOUR": Carrefour,
        "CASA MATTOS": CasaMattos,
        "CHATUBA": Chatuba,
        "CAMPEÃO DA CONSTRUÇÃO": Campeao_da_construcao,
        "CONSTRUBEL": Construbel,
        "CONSTRUSHOP": ConstruShop,
        "COPAFER": Copafer,
        "CARAJÁS": Carajas,
        "CASA FACIL CONSTRUÇÃO": CasaMaisFacil,
        "CASA MIMOSA": CasaMimosa,
        "CASAS DA AGUA": Casas_da_agua,
        "CASTELO FORTE": Castelo_forte,
        "CONSTRULAR FÁCIL": Constrular_facil,
        "EFIZI MADEIRA MADEIRA": MadeiraMadeira,
        "EFIZI MAGALU": Magalu,
        "EFIZI MERCADO LIVRE": MercadoLivre,
        "EFIZI QUERO QUERO": QueroQuero,
        # "EFIZI VIA VAREJO": ViaVarejo,
        "ENGECOPI": Engecopi,
        "FERPAM": Ferpam,
        "FERREIRA COSTA": FerreiraCosta,
        "GUEMAT": Guemat,
        "JL MEURER": Jl_meurer,
        "LEROY MERLIN": Leroy,
        "LOJAS PEDRAO": LojasPedrao,
        # "LOJAS 2001": Lojas2001,
        "NORMATEL": Normatel,
        "OBRAMAX": Obramax,
        "SODIMAC": Sodimac,
        "PADOVANI": Padovani,
        "PANORAMA": Panorama,
        "PARAIBA HOME CENTER": ParaibaHomeCenter,
        "PISOLAR": Pisolar,
        "POTIGUAR": Potiguar,
        "QUEVEDO": Quevedo,
        "REDEMAC": Redemac,
        "SERPAL": Serpal,
        "SERTAO": Sertao,
        "TAQI": Taqi,
        "TODIMO": Todimo,
        "TROPEIRO": Tropeiro,
        "VENEZA": Veneza,
        "VILA TELHAS": VilaTelhas,
        "WANDERSON MATERIAIS": WandersonMateriais
    }