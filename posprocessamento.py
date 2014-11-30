from collections import Counter
predicadosRemovidos = {"# of episodes","notable work(s)", "buried in","coronation","country","cover artist","genres","dvd release date","influences","language","nationality","notable works","occupation","original run","series","size","media type"}
conversao = {
	"alias":"hasAlias",
	"allegiance":"hasAllegianceWith",
	"ancestral weapon":"hasAncestralWeapon",
	"author":"authorIs",
	"banner" : "hasCoatOfArms",
	"battles":"hasBattle",
	"book(s)" : "appearsIn",
	"books":"appearsIn",
	"born in" : "bornIn",
	"born" : "bornIn",
	"cadet branch":"hasCadetBranch",
	"culture":"hasCulture",
	"coat of arms" : "hasCoatOfArms",
	"conflict":"conflictHappenedIn",
	"current commander" : "currentLordIs",
	"current lord" : "currentLordIs",
	"destroyed" : "destroyedIn",#
	"disbanded" : "diedOut",#
	"date":"dateIs",
	"died in" : "diedIn",
	"died" : "diedIn",
	"died out" : "diedOut",
	"father":"father",
	"followed by":"followedBy",
	"founded":"wasFounded",
	"founder":"wasFoundedBy",
	"full name":"fullNameIs",
	"genre(s)":"hasGenre",
	"government":"isGovernedBy",
	"heir":"heirIs",
	"isbn":"hasISBN",
	"issue":"hasIssue",
	"location":"locationIs",
	"mother":"motherIs",
	"motto/war cry":"hasWords",#
	"name":"nameIs",
	"named for":"isNamedFor",
	"notable places":"notablePlaceIs",#
	"organizations":"organizations",
	"other titles":"otherTitles",
	"overlord":"isOverlordOf",
	"pages":"pages",
	"place":"place",
	"played by":"playedBy",
	"preceded by":"precededBy",
	"predecessor":"predecessorIs",
	"publisher":"publisherIs",
	"queen":"queenIs",
	"race":"hasRace",
	"region":"fromRegion",
	"reign":"reigned",
	"released":"wasReleased",
	"religion":"hasReligion",
	"result": "resultWas",#
	"royal house":"belongsToRoyalHouse",
	"seat":"seatIs",
	"spouse" : "spouse",
	"spouse(s)" : "spouse",
	"successor":"sucessorIs",
	"title":"titlesIs",
	"tv series":"appearsInSeason",
	"words":"hasWords"
}

dataType={"Battle":["dateIs","nameIs", "place", "resultWas"],
	"Book":["authorIs","followedBy","hasGenre","hasISBN","nameIs", "pages","publisherIs","wasReleased"],
	"Character":["appearsInSeason","bornIn","diedIn","fullNameIs","hasAlias","hasCulture","hasRace","nameIs","otherTitles","playedBy","reigned","titlesIs"],
	"City":["destroyedIn","locationIs","hasReligion","isGovernedBy","isNamedFor","nameIs","notablePlaceIs","organizations","wasFounded"],
	"House":["diedOut","fromRegion","hasAncestralWeapon","hasCoatOfArms","hasWords","nameIs","wasFounded","titlesIs"],
	"War":["dateIs","nameIs", "resultWas"]
}

ObjectProperties = {"Battle": [("conflictHappenedIn","War")],
	"Book":[("precededBy","Book")],
	"City":[],
	"Character":[("appearsIn","Book"),("belongsToRoyalHouse","House"),("father","Character"),("hasAllegianceWith","House"),("hasIssue","Character"),("heirIs","Character"),("motherIs","Character"),("queenIs","Character"),("spouse","Character"),("sucessorIs","Character")],
	"House":[("currentLordIs","Character"),("hasCadetBranch","House"),("heirIs","Character"),("overlordIs","House"),("seatIs","City"),("wasFoundedBy","Character")],
	"War":[("hasBattle","Battle")]
}

def forcaIntegridade(triplas, classes):
	for sujeito in triplas:
		triplasFinais = []
		classeSujeito = classes[sujeito]
		for predicado, objeto in triplas[sujeito]:
			if predicado in dataType[classeSujeito] and not objeto.startswith('/index.php/'):
				triplasFinais += [(predicado, objeto)]

			for predicadoEsperado, objetoEsperado in ObjectProperties[classeSujeito]:
				if predicado == predicadoEsperado and objeto.startswith('/index.php/') and classes[objeto] == objetoEsperado:
					triplasFinais += [(predicado, objeto)]

		triplas[sujeito] = triplasFinais
	return triplas

def infereTipo(triplas):
	sujeitos = {}
	for sujeito in triplas:
		sujeitos[sujeito] = Counter()
		for (predicado, objeto) in triplas[sujeito]:
			
			# tenta parear com ObjectProperty
			for classe in ObjectProperties:
				for (predicadoEsperado, objetoEsperado) in ObjectProperties[classe]:
					if predicado == predicadoEsperado:
						sujeitos[sujeito].update([classe])

						if objeto.startswith('/index.php/'):
							if objeto not in sujeitos:
								sujeitos[objeto] = Counter()
							sujeitos[objeto].update([objetoEsperado])
						
			# tenta parear com DataType
			for classe in dataType:
				for predicadoEsperado in dataType[classe]:
					if predicado == predicadoEsperado:
						sujeitos[sujeito].update([classe])
	#print([sujeito + '->' + str(sujeitos[s].most_common(1)) for s in sujeitos].sort())
	return sujeitos

import re
def limpaUrl(url):
	return re.sub(r'[^A-Za-z\/_.]', '', url).lower()

def importaTriplas(arqName):
	linhas = open(arqName, 'r').read().split('\n')[1:-1]
	triplas = {}
	for l in linhas:
		elementos = l.split(';')
		sujeito, predicado, objeto = elementos[0].strip('"'), elementos[1].strip('"'), elementos[2].strip('"')

		sujeito = limpaUrl(sujeito)
		if objeto.startswith('/index.php/'):
			objeto = limpaUrl(objeto)

		if (sujeito not in triplas):
			triplas[sujeito] = []
		triplas[sujeito] += [(predicado, objeto.replace('&','') )]
	return triplas

def removeLinksExtras(triplas):
	for sujeito in triplas:
		elementos = triplas[sujeito]
		for i in range(len(elementos)):
			(predicado, objeto) = elementos[i]
			if objeto.startswith('/index.php/') and objeto not in triplas:
				elementos[i] = None
		triplas[sujeito] = [t for t in elementos if t is not None]
	return triplas

def listaNomes(triplas):
	lista = {}
	for sujeito in triplas:
		elementos = triplas[sujeito]
		for i in range(len(elementos)):
			predicado, objeto = elementos[i][0], elementos[i][1]
			if predicado == 'nameIs':
				lista[objeto] = sujeito
	return lista

def localizaRelacoes(triplas):
	lista = listaNomes(triplas)
	for sujeito in triplas:
		elementos = triplas[sujeito]
		for i in range(len(elementos)):
			(predicado, objeto) = elementos[i]
			#unica diferenca do anterior eh a condicao. TODO Generalizar
			if objeto in lista and sujeito != lista[objeto] and (predicado, lista[objeto]) not in elementos:
				triplas[sujeito][i] = (predicado, lista[objeto])
	return triplas

def substituicaoBasica(triplas):
	for sujeito in triplas:
		elementos = triplas[sujeito]
		elementosAdicionais = []
		for i in range(len(elementos)):
			(predicado, objeto) = elementos[i]
			predicado = predicado.lower()
			#unica diferenca do anterior eh a condicao. TODO Generalizar
			if predicado in predicadosRemovidos:
				elementos[i] = None
			if predicado in conversao:
				elementos[i] = (conversao[predicado], objeto)
			if '|' in objeto:
				elementosAdicionais += [ (predicado,  s.strip()) for s in objeto.split('|') ]
				elementos[i] = None
		triplas[sujeito] = [t for t in elementos if t is not None] + elementosAdicionais
	return triplas

def salvaResultado(triplas, classe, arqSaida):
	f = open(arqSaida, 'w')
	f.write('"Sujeito";"Classe";"Predicado";"Objeto"\n')
	l = []
	for sujeito in triplas:
		for predicado, objeto in triplas[sujeito]:
			l += ['"'+ '";"'.join([ sujeito, classe[sujeito], predicado, objeto ]) + '"\n']
	l.sort()
	[f.write(i) for i in l ]

def geraOWL(triplas, classes):
	templateInicio = '''\t<!-- http://awoiaf.westeros.org/index.php#%s -->
	<owl:NamedIndividual rdf:about="http://awoiaf.westeros.org/index.php#%s">
		<rdf:type rdf:resource="http://awoiaf.westeros.org/index.php#%s"/>\n\n'''
	templateDataType = '''\t\t<%s>%s</%s>\n'''
	templateObjetProperty = '''\t\t<%s rdf:resource="http://awoiaf.westeros.org/index.php#%s" />\n'''
	templateFim = '''\t</owl:NamedIndividual>\n\n'''

	resultado = ""
	
	sujeitos = list(triplas.keys())
	sujeitos.sort()

	for sujeito in sujeitos:
		url = sujeito.replace('/index.php/', '')
		classeSujeito = classes[sujeito]

		resultado += templateInicio % (url, url, classeSujeito)

		for predicado, objeto in triplas[sujeito]:
			if predicado in dataType[classeSujeito]:
				resultado += templateDataType % (predicado, objeto, predicado)
			else:
				resultado += templateObjetProperty % (predicado, objeto.replace('/index.php/', '') )

		resultado += templateFim
	return resultado


def pipelinePosProcessamento(arqEntrada='triplas27112014_004031.csv', arqSaida='populacao30112014.owl', ontologiaBase='ontologiaBase.owl'):
	triplas = importaTriplas(arqEntrada)
	triplas = substituicaoBasica(triplas)
	triplas = removeLinksExtras(triplas)
	triplas = localizaRelacoes(triplas)
	inferencia = infereTipo(triplas)

	classes = { sujeito : inferencia[sujeito].most_common(1)[0][0] for sujeito in inferencia }
	triplas = forcaIntegridade(triplas, classes)

	salvaResultado(triplas, classes, 'triplas_posprocessamento_30112014.csv')

	base = open(ontologiaBase, 'r').read()
	f = open(arqSaida, 'w')

	resultado = base.replace( '''<!-- SUBSTITUIR -->''' ,geraOWL(triplas, classes))
	
	f.write(resultado)
	f.close()

	return triplas, listaNomes(triplas), inferencia,  classes, resultado

pipelinePosProcessamento()
#substituicaoBasica('triplas27112014_004031.csv', 'triplas27112014_004031_convertido.csv')