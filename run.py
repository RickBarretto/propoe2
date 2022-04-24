from model.mives import Mives
from model.poem_builder import Poem_builder
from model.filter import Filter
from configuration.conf import *

seed = None

mives = Mives(mives_xml)
sentences = Filter(mives.sentences, metrificacao,
                   padrao_ritmico, seed).get_rhymes()
builder = Poem_builder(sentences, metrificacao,
                       padrao_ritmico, pesos_avaliacao, seed)
builder.build(verbose=True)
builder.result()
builder.save(caminho_poema)
