import MySQLdb
import numpy as np

db = MySQLdb.connect(host="localhost", user="root", db="camarafiltrado")

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
    texto = cur.fetchone()[0]
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
stopwords += ["n", "s", "p", "c", "1", "000", "5", "0", "2", "3", "4", "00", "2013", "m", "es", "lei", "art", "rio", "ncia", "comiss", "projeto", "dio", "ria"] #stopwords especificas desse corpora
# Separate into a list of (word, frequency).

for estado in uf2tex.keys():
    TEXT = uf2tex[estado]
    words = wordcloud.process_text(TEXT, stopwords=stopwords)
    # Computa a posicao das palavras
    elements = wordcloud.fit_words(words, font_path="/usr/share/fonts/TTF/arial.ttf")
    # Desenha as palavras no arquivo png
    wordcloud.draw(elements, estado+".png", font_path="/usr/share/fonts/TTF/arial.ttf", scale=2)#width=500, height=500,
        
        
        
        
        
        
        
        
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
    

    