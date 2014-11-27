import re
from html import unescape
from urllib.request import *
from datetime import datetime

import unicodedata
def normalizaTexto(texto):
    if texto.startswith('/index.php/'):
        return texto
    texto = unicodedata.normalize("NFKD", texto).encode('ASCII', 'ignore').decode()
    texto = re.sub(r'\[[0-9]+\]','',texto)
    texto = texto.replace('\"','')
    texto = re.sub(r'[ \t\n\r\f\v]+',' ',texto)
    texto = texto.replace(' ,', ',')
    return texto.strip()

def formatoCSV(triplas):
    string = ''
    for t in triplas:
        sujeito = t[0]
        predicado = t[1]
        objeto = t[2]

        #se nao tenho objetos naquele predicado, ignoro-o
        if len(objeto) == 0  :
            continue
        string += '"'+sujeito + '";"' + predicado + '";"' + objeto + '"\n'
    return string

def getInfobox(pagina):
    infobox = pagina.split('<table class="infobox infobox-body"')
    if len(infobox)==1:
        print("infobox nao existe")
        return ''
    #Pego o que vem depois da tag de inicio do infobox
    infobox = infobox[1]
    #removo tudo que vem depois da tag de fechamento
    infobox = infobox.split('</table>')[0]
    #limpo os excessos da tag
    infobox = re.sub('^[^>]+>', '', infobox)
    return infobox
    
def removeTags(texto):
    return unescape(re.sub('<[^<]+?>', '', texto)).strip()

def localizaUrls(texto):
    regexp = re.compile('(?<=\<a href\=\")[^> ]+(?=\")')
    urls = regexp.findall(texto)
    urls = [ u for u in urls if '#' not in u and u.startswith('/index.php/') ]
    return urls

def urlsLista(texto):
    regexp = re.compile('(?<=\<li\> \<a href\=\")[^> ]+(?=\")')
    urls = regexp.findall(texto)
    urls = [ u for u in urls if '#' not in u and u.startswith('/index.php/') ]
    return urls


def removeLixo(texto):
    texto = texto.split('</head>')[1]
    texto = texto.split('<div class="printfooter">')[0]
    texto = re.sub(r'<script.*</script>', '', texto)
    return texto
           
def parseiaObjetos(texto):
    objetos = []
    if len(texto) > 1:
        objetos += localizaUrls(texto)
        objetos += [ removeTags(i) for i in texto.split('<br>') ]
    return objetos

def parseiaTriplas(texto, sujeito):
     linhas = texto.split('<tr class="">')
     triplas = []
     for l in linhas:
        #tento achar o texto da primeira coluna do infobox
         tabela = l.split('</th>')
         predicado = removeTags(tabela[0])

         #se o predicado nao existe, passo para prox linhas
         if predicado == '' or len(tabela) != 2:
             continue
            
         objetos = parseiaObjetos(tabela[1])
         triplas +=[ ( sujeito, normalizaTexto(predicado), normalizaTexto(o) ) for o in objetos]
     return triplas
    
def getPagina(url):
    import urllib.request
    opener = urllib.request.build_opener()    
    opener.addheaders = [('User-Agent', 'Opera/9.80 (Windows NT 6.1; WOW64; U; de) Presto/2.10.289 Version/12.01'), ('Accept-Language', 'de-DE,de;q=0.9,en;q=0.8'), ('Accept', 'text/html, application/xml;q=0.9, application/xhtml+xml, image/png, image/webp, image/jpeg, image/gif, image/x-xbitmap, */*;q=0.1')]
    f = opener.open('http://awoiaf.westeros.org%s' % url)
    content = f.read().decode(errors="ignore")
    f.close()
    return content

def getListaPersonagens():
    return urlsLista(removeLixo(getPagina('/index.php/List_of_Characters')))

def getTitle(texto):
    regexp = re.compile('(?<=\<title\>).+(?=- A Wiki of Ice and Fire\<\/title\>)')
    titulo = regexp.findall(texto)[0]
    return normalizaTexto(titulo)

def crawlingPipeline(proximos, visitados):
    f = open('triplas'+ datetime.now().strftime('%d%m%Y_%H%M%S')+'.csv', 'w')
    log = open('log' + datetime.now().strftime('%d%m%Y_%H%M%S')+'.txt', 'w')
    f.write('"Sujeito";"Predicado";"Objeto"\n')
    i = 0
    ultimaVisita = datetime.now()
    tMedio = ultimaVisita-ultimaVisita #nao sei zerar esse tipo de dado
    try:
        while len(proximos) > 0:
            atual = proximos.pop(0)
            if atual in visitados:
                continue
            
            #log basico
            i += 1
            deltaT = datetime.now() - ultimaVisita
            tMedio += 1.0/i*( deltaT - tMedio )
            andamento = "\n" + str(i) + "/"+ str(len(proximos) + i ) + "\t" + atual + "\t"+ datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\t" + str(100.0*i/(len(proximos)+i)) +"%\tEstimado " + str( tMedio*len(proximos) )
            log.write(andamento)
            print(andamento)
            ultimaVisita = datetime.now()

            #processamento propriamente dito
            pagina = getPagina(atual)
            infobox = getInfobox(pagina)

            if infobox == '':
                log.write("\tInfobox nao existe")
                continue
            
            triplas = parseiaTriplas(texto=infobox, sujeito=atual)
            triplas += [ (atual, "name" , getTitle(pagina)) ]

            #persistencia
            string = formatoCSV(triplas)
            f.write(string)
            f.flush()
            log.flush()
            
            #final da busca em largura
            visitados.add(atual)
            proximos += [ t[2] for t in triplas if len(t) == 3 and t[2].startswith('/index.php/') and t[2] not in visitados and t[2] not in proximos]
    except Exception as e:
        log.write("proximos=" + str(proximos) + "\n" )
        log.write("visitados=" + str(visitados) +"\n" )
        log.write(str(e))
        raise e
    f.close()
    log.close()

proximos = getListaPersonagens()
#proximos = open('C:/Users/Gabriel/proximos.csv','r').read().split('\n')
visitados = set("/index.php/George_R._R._Martin")
#visitados = set(open('C:/Users/Gabriel/visitados.csv','r').read().split('\n'))
crawlingPipeline(proximos, visitados)
