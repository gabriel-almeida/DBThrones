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

dataType={"BATTLE":["dateIs","nameIs", "resultWas"],
	"BOOK":["authorIs","followedBy","hasGenre","hasISBN","nameIs", "pages","publisherIs","wasReleased"],
	"CHARACTER":["appearsInSeason","bornIn","diedIn","fullNameIs","hasAlias","hasCulture","hasRace","nameIs","otherTitles","playedBy","reigned","titlesIs"],
	"CITY":["destroyedIn","hasReligion","isGovernedBy","isNamedFor","nameIs","notablePlaceIs","organizations","wasFounded"],
	"HOUSE":["diedOut","hasAncestralWeapon","hasCoatOfArms","hasWords","nameIs","wasFounded","titlesIs"],
	"WAR":["nameIs"]
}

ObjectProperties = {"BATTLE": [("conflictHappenedIn","WAR"),("place","CITY"),("place","REGION")],
	"BOOK":[("precededBy","BOOK")],
	"CHARACTER":[("appearsIn","BOOK"),("belongsToRoyalHouse","HOUSE"),("father","CHARACTER"),("hasAllegianceWith","HOUSE"),("hasIssue","CHARACTER"),("heirIs","CHARACTER"),("motherIs","CHARACTER"),("queenIs","CHARACTER"),("spouse","CHARACTER"),("sucessorIs","CHARACTER")],
	"CITY":[("locationIs","REGION")],
	"HOUSE":[("currentLordIs","CHARACTER"),("fromRegion","REGION"),("hasCadetBranch","HOUSE"),("heirIs","CHARACTER"),("overlordIs","HOUSE"),("seatIs","CITY"),("wasFoundedBy","CHARACTER")],
	"WAR":[("hasBattle","BATTLE")]
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

def importaTriplas(arqName):
	linhas = open(arqName, 'r').read().split('\n')[1:-1]
	triplas = {}
	for l in linhas:
		elementos = l.split(';')
		sujeito, predicado, objeto = elementos[0].strip('"'), elementos[1].strip('"'), elementos[2].strip('"')
		if (sujeito not in triplas):
			triplas[sujeito] = []
		triplas[sujeito] += [(predicado, objeto)]
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

def removeTriplasRedundantes(triplas):
	lista = listaNomes(triplas)
	for sujeito in triplas:
		elementos = triplas[sujeito]
		for i in range(len(elementos)):
			(predicado, objeto) = elementos[i]
			#unica diferenca do anterior eh a condicao. TODO Generalizar
			if objeto in lista and (predicado, lista[objeto]) in elementos:
				elementos[i] = None
		triplas[sujeito] = [t for t in elementos if t is not None]
	return triplas

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


def pipelinePosProcessamento(arqEntrada='triplas27112014_004031.csv'):
	#, arqSaida):
	#arq = open(arqSaida, 'w')
	triplas = importaTriplas(arqEntrada)
	triplas = substituicaoBasica(triplas)
	#triplas = removeTriplasRedundantes(triplas)
	#triplas = removeLinksExtras(triplas)
	triplas = localizaRelacoes(triplas)
	inferencia = infereTipo(triplas)

	classes = { sujeito : inferencia[sujeito].most_common(1)[0][0] for sujeito in inferencia }
	triplas = forcaIntegridade(triplas, classes)

	salvaResultado(triplas, classes, 'triplas_posprocessamento_30112014.csv')
	return triplas, listaNomes(triplas), inferencia,  classes

pipelinePosProcessamento()
#substituicaoBasica('triplas27112014_004031.csv', 'triplas27112014_004031_convertido.csv')