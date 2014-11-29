predicadosRemovidos = {"# of episodes","buried in","coronation","country","cover artist","destroyed","disbanded","genres","dvd release date","influences","language","nationality","population","notable works","occupation","original run","series","size","media type","motto war cry","result"}
conversao = {
	"Alias":"hasAlias",
	"Allegiance":"hasAllegianceWith",
	"Ancestral Weapon":"hasAncestralWeapon",
	"Author":"authorIs",
	"Banner" : "hasCoatOfArms",
	"Battles":"hasBattle",
	"Book(s)" : "appearsIn",
	"Book(s)":"appearsIn",
	"Books" : "appearsIn",
	"Books":"appearsIn",
	"Born in" : "bornIn",
	"Born" : "bornIn",
	"Cadet Branch":"hasCadetBranch",
	"Cadet Branch":"hasCulture",
	"Coat Of Arms" : "hasCoatOfArms",
	"Coat of Arms":"hasCoatOfArms",
	"Conflict":"conflictHappenedIn",
	"Current Comander" : "currentLordIs",
	"Current Lord" : "currentLordIs",
	"Date":"dateIs",
	"Died in" : "diedIn",
	"Died" : "diedIn",
	"Father":"father",
	"Followed by":"followedBy",
	"Founded":"wasFounded",
	"Founder":"wasFoundedBy",
	"Full Name":"fullNameIs",
	"Genre(s)":"hasGenre",
	"Government":"isGovernedBy",
	"Heir":"heirIs",
	"ISBN":"hasISBN",
	"Issue":"hasIssue",
	"Location":"locationIs",
	"Mother":"motherIs",
	"name":"nameIs",
	"Named for":"isNamedFor",
	"Notable places":"notablePlaceIs",#
	"Organizations":"organizations",
	"Other Titles":"otherTitles",
	"Overlord":"isOverlordOf",
	"Pages":"pages",
	"Place":"place",
	"Played By":"playedBy",
	"Preceded By":"precededBy",
	"Predecessor":"predecessorIs",
	"Publisher":"publisherIs",
	"Queen":"queenIs",
	"Race":"hasRace",
	"Region":"fromRegion",
	"Reign":"reigned",
	"Released":"wasReleased",
	"Religion":"hasReligion",
	"Royal House":"belongsToRoyalHouse",
	"Seat":"seatIs",
	"Spouse" : "spouse",
	"Spouse(s)" : "spouse",
	"Successor":"sucessorIs",
	"Title":"titlesIs",
	"TV series":"appearsInSeason",
	"Words":"hasWords"
}

def substituicaoBasica(arqEntrada, arqSaida):
	linhas = open(arqEntrada, 'r').read().split('\n')[:-1]
	arq = open(arqSaida, 'w')
	for l in linhas:
		if l.split('";"')[1] in predicadosRemovidos:
			continue
		for predicado in conversao:
			l = l.replace(';"'+predicado+'";', ';"'+conversao[predicado]+'";')
		arq.write(l+'\n')

substituicaoBasica('triplas27112014_004031.csv', 'triplas27112014_004031_convertido.csv')