import MySQLdb
import numpy as np
from unicodedata import normalize 

db = MySQLdb.connect(host="localhost", user="root", passwd="abc123", db="camarafiltrado")

cur = db.cursor()

    
#################    
#wordclouds por estado
    
#pega conjunto de propostas
    
cur.execute("select id_proposicao from proposicoes where ano=2013 and tipo='PL' and autor1 in(select id_autor from autores_proposicoes where tipo='TipoParlamentar_10000');")
rows = cur.fetchall()
proposicoes = [element for tupl in rows for element in tupl]


print "numero de proposicoes de deputados:", len(proposicoes)

uf2tex = {}
#para cada proposta, pega autor e uf
for proposicao in proposicoes:
    cur.execute("select inteiro_teor from proposicoes where id_proposicao=(%s)", (proposicao,))
    textocod = str(cur.fetchone()[0])
    texto = normalize('NFKD', textocod.decode("latin1")).encode('ASCII','ignore').lower()
    #print texto[:20]
    cur.execute("select uf from deputados where id_deputado in (select autor1 from proposicoes where id_proposicao=(%s))", (proposicao,))
    uf = cur.fetchone()[0] #pega o uf do deputado
    
    #para cada UF, junta todas as propostas
    if texto:
        #texto = unicode(texto,encoding='latin1')
        if uf not in uf2tex.keys():
            uf2tex[uf] = texto
        else:
            uf2tex[uf] += texto

    
import wordcloud

stopwords = ["o", "e", "a", "as", "de", "da", "do", "dos", "das", "um", "uma", "umas", "que", "em", "no", "por", "com", "para", "os", "ao", "se", "na", "ou", "como", "pela", "mais", "nos", "ser" ]
stopwords += ["n", "s", "p", "c", "1", "000", "5", "0", "2", "3", "4", "00", "2013", "m", "es", "lei", "art", "rio", "ncia", "comiss", "projeto", "dio", "ria", "d", "brasil", "comissao", "nao", "sim"]
stopwords += ["aos", "sua", "anos", "2012", "pelo", "sobre", "seu", "1o", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "b", "i", "ii", "iii", "f", "2000", "2001", "2002", "2003", "2004"]
stopwords += ["2005", "2006", "2007", "2008", "2009", "2010", "2011", "d", "nas", "250", "dois", "esta", "tem", "sr", "relator", "11", "12", "sobre", "senador", "foi", "senhor", "sem", "trata"]
stopwords += ["040", "sao", "mas", "deputados", "deputado", "camara", "ha", "todos", "mil", "foi", "sem", "05", "caput", "fins", "tema", "quando", "poder", "2o", "paulo", "68", "r", "seis"]
# Separate into a list of (word, frequency).

for estado in uf2tex.keys():
    TEXT = uf2tex[estado]
    words = wordcloud.process_text(TEXT, stopwords=stopwords)
    # Computa a posicao das palavras
    elements = wordcloud.fit_words(words, font_path="/usr/share/fonts/truetype/msttcorefonts/arial.ttf")
    # Desenha as palavras no arquivo png
    wordcloud.draw(elements, estado+".png", font_path="/usr/share/fonts/truetype/msttcorefonts/arial.ttf", scale=2)#width=500, height=500,
        
        
        
        
        
        
        
        
#######################################################


#clusterizacoes (ou predicao)

#1- renda X idade

#pega data de nascimento e renda de cada deputado



query = '''select d.id_deputado, sum(valor) as bens, data_nascimento, partido_atual, eleicao_partido
from deputados as d, deputados_eleicoes_bens as deb
where d.id_deputado = deb.id_deputado and data_nascimento is not null and partido_atual is not null
group by deb.id_deputado;'''

cur.execute(query)
rows = cur.fetchall()

rendas = np.array([[tupl[0], int(tupl[1])]  for tupl in rows])





#select d.nome_completo, sum(deb.valor) from deputados as d, deputados_eleicoes_bens as deb where d.id_deputado = deb.id_deputado group by deb.id_deputado limit 10;

#2- votos

query = '''SELECT v.id_votacao, id_partido, voto
FROM votos as vs
INNER JOIN 
	(SELECT distinct id_votacao from votos  ORDER BY rand() LIMIT 10) as v
  ON vs.id_votacao = v.id_votacao;'''

cur.execute(query)  
rows = cur.fetchall()


votacoes = list(set([tupl[0] for tupl in rows]))
partidos = list(set([tupl[1] for tupl in rows]))

matriz_votos = np.empty((len(votacoes), len(partidos)))

for tupl in rows:
    matriz_votos[votacoes.index(tupl[0]), partidos.index(tupl[1])] += int(tupl[2])
    

    