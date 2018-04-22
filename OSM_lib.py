#!/bin/python
# -*- coding: utf-8 -*-
import re

leaveCityNameAnywayRE=re.compile(r"(?ix)((^|\s)((Noord|Zuid)?station|dorp|markt|kerk|centrum|Veldekensstraat)(\s|$))") # case insensitive search for terms surrounded by whitespace
citynamesToOmit = [
                   (r"Gent",""), # !Sas-van-Gent
                   (r"Antwerpen",""),
                   (r"Sint-Agatha-Berchem",""),
                   (r"Berchem",""), # !Sint-Agatha-Berchem
                   (r"Burcht",""),
                   (r"Borsbeek",""),
                   (r"Borgerhout",""),
                   (r"Deurne",""), # !Deurne (bij Diest)
                   (r"Hoboken",""),
                   (r"Ekeren",""),
                   (r"Merksem",""),
                   (r"Mortsel",""),
                   (r"Wilrijk",""),
                   (r"Zwijndrecht",""),
                   (r"Brussel",""),
                   (r"Anderlecht",""),
                   (r"Elsene",""),
                   (r"Etterbeek",""),
                   (r"Evere",""),
                   (r"Ganshoren",""),
                   (r"Jette",""),
                   (r"Koekelberg",""),
                   (r"Oudergem",""),
                   (r"Schaarbeek",""),
                   (r"Sint-Gillis",""),
                   (r"Sint-Jans-Molenbeek",""),
                   (r"Sint-Joost-ten-Node",""),
                   (r"Sint-Lambrechts-Woluwe",""),
                   (r"Sint-Pieters-Woluwe",""),
                   (r"Ukkel",""),
                   (r"Vorst",""), # !Vorst (bij Veerle) !Vorst-Laakdal
                   (r"Watermaal-Bosvoorde",""),
                   (r"Sint-Job-in-'t Goor","Sint-Job-in-'t-Goor "),
                   (r'Petegem A/D Leie','Petegem-aan-de-Leie '),
                   (r"Liège",""),
                   #(r"Moeskroen",""),
                   (r"Ronse/Renaix",""),
                   (r"Ellezelles / Elzele ",""),
                   (r"Bever/Bievene",""),
                   (r"Zittert-Lummen","Zétrud Lumay "),
                   (r"Geldenaken","Jodoigne "),
                   (r"Moeskroen","Mouscron "),
                   (r"Mark","Marcq "),
                   (r"Edingen","Enghien "),
                   ]
commonabbreviations=[
    (500,0,r"Mol Gompel ","Gompel "),
    (500,0,r"'T","'t"),
    (500,0,r"T'","'t "),
    (500,0,r'(?u)T Zand',"'t Zand"),
    (500,0,r"'S","'s"),
    (500,1,r"Erps-Kwerps D'Ieteren","Erps-Kwerps D'Ieteren"),
    (500,0,r"(?ui)D'\s*","d'"),
    (500,0,r"(?ui)l'\s*","l'"),
    (500,0,r"Aux","aux"),
    (500,0,r"Ij","IJ"),
    (500,0,r'Premetrostation ',''),
    (500,0,r"Hof Ten Berg","Hof-ten-Berg"),

    (500,1,r"Anderlecht Kol.Veteranensquare","Koloniale Veteranen - Vétérans Coloniaux"),
    (500,1,r"(?ui)\bMarg\.*v\.*Oostenrijk","Margaretha van Oostenrijk - Marguerite d'Autriche"),
    (500,0,r'Sas Van Gent (Nl)','Sas van Gent'),
    (500,0,r'(?u)^Mo\s','Moelingen '),
    (500,0,r"(?u)^SPV\s","Sint-Pieters-Voeren "),
    (500,0,r"(?u)^SMV\s","Sint-Martens-Voeren "),
    (500,0,r"(?u)^SGV\s","'s Gravenvoeren "),

    (500,0,r'(?ui)\bkerk','Kerk'),
    (500,0,r'(?ui)\bPl(\.|\b)','Plaats'), # could be Plein, as well
    
    (400,1,r"Haasrode Industr. Interleuvenlaan","Haasrode Industriezone Interleuvenlaan"),
    (500,0,r'(?u)str(\.|$)','straat'),
    (500,0,r'O. Dendermondsestwg','Ouden Dendermondsesteenweg'),
    (300,1,r"Stwg.Tervuren /Stwg.Vilvoorde","Steenweg Tervuren/Steenweg Vilvoorde"),
    (300,1,r"Voormezele O. Mesenstwg.","Voormezele Oude Mesensesteenweg"),
    (500,0,r'(?u)\Bstwg\.*','steenweg'),
    (500,0,r'(?u)(St(wg|w|g)\.*)','Steenweg '),
    (500,0,r"(?ui)\bAv\.*\s","Avenue "),
    (500,0,r"(?ui)\bReu\b","Rue"),
    (500,0,r"Allee","Allée"),
    (500,0,r"(?ui)\bCite\b","Cité"),
    (500,0,r'(?ui)\Station\s-\sPerron\b','Station Perron'),
    (500,0,r'stadion','Stadion'),
    (500,0,r'(?u)\bperron\b','Perron'),
    (500,0,r'Prov.','Provinciaal'),
    (500,0,r'Recreatiecentr.','Recreatiecentrum'),
    (500,0,r'(?u)\Bbn\b','baan'),
    (500,0,r'(?u)centr\.','centrum'),
    (500,0,r'(?ui)\bDom\.','Domein'),
    (500,0,r'(?ui)Krpt\.*','Kruispunt'),
    (500,0,r'Keiheuvel Gt Kamping','Keiheuvel Grote Camping'),

    (500,0,r'(?u)\bBurg\.\s*','Burgemeester '),
    (400,1,r"Wemmel Cdt. J. De Blockplein","Wemmel Commandant J. de Blockplein"),
    (500,0,r"(?ui)\bJ\.*\s*De\s*Block","Jozef De Block"),
    (500,0,r'Cdt.','Commandant'),
    (500,0,r'Bos En Lommer','Bos en Lommer'),

    (500,1,r'Roesbrugge Dr. Gheysen','Roesbrugge Dokter Joseph Gheysen'),
    (500,0,r'(?u)\bDr\.','Dokter '),
    (100,0,r"(?ui)\bKon\.*\s*Tech\.*\s*Atheneum\b","Koninklijk Technisch Atheneum"),
    (500,0,r"Kta","KTA"),
    (500,0,r'(?ui)Vti','VTI'),
    (500,0,r'(?ui)\bVko','VKO'),
    (500,0,r" Rvt "," RVT "),
    (500,1,r'Turnhout Sint-Pieterinstituut','Turnhout Sint-Pietersinstituut'),
    (500,0,r'(?u)\s*Inst\.\s',' Instituut '),
    (500,0,r'(?u)Electr\.','Electrische'),
    (500,0,r'Ecole','École'),
    (500,0,r"(?u)\bEtat\b","État"),
    (500,0,r"(?u)\binrit\b","Inrit"),
    (500,0,r"(?ui)L'Ecluse", "L'Écluse"),
    
    (500,0,r'(?u)^(.*)(A\.*[Zz]\.*\s*)(\b.*)$',r'\1AZ \3'),
    (500,0,r'(?ui)O\.*C\.*M\.*W\.*-*','OCMW '),
    (500,0,r'(?u)-?\b(VIII|VII|VI|III|IV|II)\s-*(.+)$',r' \1-\2'),
    
    (400,0,r'OPZ','Openbaar Psychiatrisch Ziekenhuis'),
    (500,0,r'(?ui)(P\.?Z\.?)','Psychiatrisch Ziekenhuis'),
    (500,0,r'(?ui)Ger\.*\s*Centrum','Geriatrisch Centrum'),

    (500,0,r'(?ui)\bF\.*\s*Adriaenssens','Frans Adriaenssens'),
    (500,0,r"(?ui)\bW\.*\s*Alexander","Willem Alexander"),
    (500,0,r"(?ui)\bChem\.*\s*d\s*Angoussart","Chemin d'Angoussart"),
    
    (500,0,r"Barriere","Barrière"),
    (500,0,r"(?ui)\bE\.*\s*Beauduin","Emile Beauduin"),
    (500,0,r'De Becker Remypl.','de Becker Remyplein'),
    (500,0,r"(?ui)\bP\.*\s*Benoit","Peter Benoit"),
    (500,0,r"(?ui)\bBrasschaat\s*Berrelei","Brasschaat Berrélei"),
    (500,0,r"(?ui)\bBesch\.*Werkplaats","Beschermde Werkplaats"),
    (500,0,r"(?ui)\bA\.*Blieck","Albert Blieck"),
    (500,0,r'K. Boom','Karel Boom'),
    (500,0,r'(?ui)L\.*p\.*\sBoon','Louis Paul Boon'),
    (500,0,r'Hospitaal J.Bracops','Hospitaal Joseph Bracops'),
    (500,0,r"(?ui)\bBrouw\.*\s*Lorier","Brouwerij Lorier"),
    (500,0,r'Brouw.','Brouwerij'),
    (500,0,r'Brussel Noord','Brussel Noordstation'),
    (500,0,r'Brussel Zuid','Brussel Zuidstation'),

    (500,0,r"(?ui)\bE\.*Carels","Emile Carels"),
    (500,0,r"(?ui)\bTh\.*\s*V\.*\s*Cauwenberghs","Theofiel Van Cauwenberghs"),
    (500,0,r'E. Claes','Ernest Claes'),
    (500,0,r"(?ui)\bP\.*\s*Coloma","Pedro Coloma"),
    (500,0,r"(?ui)\P\.*\s*Coomans","Pieter Coomans"),
    (500,0,r'(?ui)\bP\.\sCop','Pastoor Cop'),
    (500,0,r'(?ui)\bH\.*\s*Conscience','Hendrik Conscience'),
    (500,0,r'(?ui)S\.*J\.*\s*Ceulemans','S. Jos Ceulemans'),
    (500,0,r'A. Cuppens','August Cuppens'),

    (500,0,r'Pr. Daens','Priester Daens'),
    (500,0,r"(?ui)\bGer\.*\s*Centrum\s*P\.*\s*Damiaan","Geriatrisch Centrum Pater Damiaan"),
    (500,0,r'(?ui)\bP\.\s?Damiaan','Pater Damiaan'),
    (500,0,r"(?ui)\bF\.*\s*De\s*Laet","Frans De Laet"),
    (500,0,r'A.Demanez','Albert Demanez'),
    (500,0,r'Déportes','Déportés'),
    (500,0,r"(?ui)\bJ\.*\s*De\s*Doncker","Jan De Doncker"),
    (500,0,r'(?ui)\bJ\.?\s*Dooghe','Julius Dooghe'),
    (500,0,r'Jette De Greef','Guillaume De Greef'),
    (500,0,r'(?ui)\bG\.*\s*De Kleermaekers','Guillaume De Kleermaekers'),
    (500,0,r'(?ui)\bJ\.*\s*B\.*\s*Delcorte','Jules Delcorde'),
    (500,0,r"(?ui)\bF\.*\s*Van\s*Dun","Frans van Dun"),
    (400,0,r"(?ui)\bJ\.*P\.*\s*David","Jan Baptist David"),
    (500,0,r"(?ui)\bJ\.*\s*David","Jan David"),
                     
    (500,0,r'C.Everaart',' Cornelis Everaart'),
    (500,1,r'Meerle Groot Eysel','Meerle Groot Eyssel'),
    (500,1,r'Meerle Dorp','Meerledorp'),
    
    (500,0,r"(?ui)\bJ\.*\s*B\.*\s*Francis","Jan Baptist Francis"),

    (500,0,r"Gabriel","Gabriël"),
    (500,0,r"(?ui)\bM\.*\s*Gandhi","Mahatma Gandhi"),
    (500,0,r"Gare Ir","Gare IR"),
    (500,0,r'(?ui)\bGebr\.','Gebroeders'),
    (500,0,r"(?ui)\bW\.*\s*Geets","Willem Geets"),
    (500,0,r"De Geloes","de Geloes"),
    (500,0,r'(?ui)\bG\.?\s*Gezelle','Guido Gezelle'),
    (500,0,r"(?u)N\.*\s*Gombert","Nikolaas Gombert"),
    (500,0,r"(?ui)\bG\.*\s*Le\s*Grelle","Gerard Le Grelle"),
    (500,0,r"Reusel Ned. Grens Reusel","Reusel Nederlandse Grens"),
    (500,0,r'(?ui)\bLod\.*\s*Guns','Louis Guns'),

    (500,0,r'(?ui)P\.*\s*De\s*Halleux','Paul De Halleux'),
    (500,0,r'(?ui)P\.*\s*Hens','Pater Hens'),
    (500,0,r"(?ui)\bR\.*\s*Henry","René Henry"),
    (500, 0, "'s-", "'s "),
    (500,0,r"(?ui)\bW\.*\s*Herreyns","Willem Herreyns"),
    (500,0,r"La Houppe/d'Hoppe","La Houppe/D'Hoppe"),
                     
    (500,0,r'(?ui)\bH\.?\s*Familie','Heilige Familie'),
    (200,1,r'Heist Olvo','Heist Olvo'),
    (200,1,r'O.L.V.Middelareskerk','Onze-Lieve-Vrouw-Middelareskerk'),
    (200,0,r"Ganshoren H.Hart College","Heilig Hart College - Collège Sacré Coeur"),
    (500,0,r'(?ui)\bH\.*\s*Hart','Heilig Hart'),
    (500,1,r'O.L.V.-ten-Steen','Onze-Lieve-Vrouw-ten-Steen'),
    (500,0,r'(?ui)M\.\s*Middelares','Maria Middelares'),
    (500,0,r"(?ui)\bM\.*\s*Middelares\s*-\s*Maalte","Maria Middelares - Maalte"),
    (500,0,r'Brugge O.L.V. Kerk','Brugge Onze-Lieve-Vrouwekerk'),
    (500,0,r'(?ui)O\.*L\.*V\.*\s*College','Onze-Lieve-Vrouwcollege'),
    (500,0,r'(?ui)O\.*L\.*V\.*\s*Dreef','Onze-Lieve-Vrouwdreef'),
    (500,1,r'O.L.V.-Lombeek','Onze-Lieve-Vrouw-Lombeek'),
    (500,0,r'(?ui)O\.*L\.*V\.*\s*Plein','Onze-Lieve-Vrouwplein'),
    (500,0,r'(?ui)O\.*L\.*V\.*\s*-*Straat','Onze-Lieve-Vrouwstraat'),
    (500,0,r'(?ui)Onze\sLieve\sVrouw\sInstituut','Onze-Lieve-Vrouwinstituut'),
    (500,0,r'(?ui)O\.*L\.*V\.*-*Ziekenhuis','Onze-Lieve-Vrouwziekenhuis'),
    (500,0,r'(?ui)O\.*L\.*V\.*(\s|-)*K(?P<kerkkapel>erk|apel)',r'Onze-Lieve-Vrouwk\2'),
    (500,0,r'(?ui)(\bO(nze)?\.*\s*-*L(ieve)?\.*\s*-*V(\.|rouw)*)','Onze-Lieve-Vrouw'),
    (500,0,r'(?ui)St\.*-Siméon','Saint-Siméon'),
    (500,0,r'(?u)St\.*-\b','Sint-'),

    (500,0,r'(?ui)\bK(on)*\.?\s*Astrid','Koningin Astrid'),
    (500,0,r'(?ui)\bK(on)*\.?\s*Elisabeth','Koningin Elisabeth'),
    (500,0,r'(?ui)\bJ\.?\s*Charlotte','Josephine Charlotte'),

    (500,0,r'(?ui)Jachtl\.','Jachtlaan'),
    (500,0,r'Jambede Bois','Jambe de Bois'),
    (500,0,r"J. Jennes","Jozef Jennes"),
    (500,0,r' Jh ',' Jeugdherberg '),

    (500,0,r"(?ui)\bV\.*\s*Kegels","Victor Kegels"),
    (500,0,r"Wemmel H. de Keersmaekerlaan","Wemmel H. De Keersmaekerlaan"),
    (500,0,r"(?ui)\bG\.*De\s*Kleermaekers","Guillaume De Kleermaekers"),

    (500,0,r"(?ui)\bG\.*\s*Lambert","Guillaume Lambert"),
    (500,0,r"Herentals Lange Pad","Herentals Langepad"),
    (500,0,r'E. Lauder','Estée Lauder'),
    (500,0,r'Lokeren T Lavertje',"Lokeren 't Lavertje"),
    (500,0,r'(?ui)K\.*\s*De\s*Lens','Karel Lodewijk de Lens'),
    (500,0,r'(?ui)\bG\.*\s*Le\s*Grelle','Gerard Le Grelle'),
    (500,0,r'O.Leuvense Baan','Oude Leuvense Baan'),
    (500,0,r'(?ui)B.\s*Leysen','Bert Leysen'),
    (500,0,r"(?ui)De\s*Linde\s*Plein","De Lindeplein"),
    (500,0,r"Th.Van Loostraat","Thomas Van Loostraat"),

    (500,0,r'Brussel Magnolia','Magnolia - Magnolias'),
    (500,0,r'Marie Joseplein','Marie-Joséplein'),
    (500,0,r"(?ui)\bJ\.*de\s*Meeus","Graaf Joseph De Meeus"),
    (500,0,r"Mesanges","Mésanges"),
    (500,0,r"(?ui)\bC\.*Meunier","Constantin Meunier"),
    (500,0,r"(?ui)\bL\.*\s*Mortelmans","Lodewijk Mortelmans"),
    (500,0,r"Brussel Modelwijk 4","Modelwijk 4 - Cité Modèle 4"),
    (500,0,r"(?ui)\bJ\.*\s*Moretus","Jules Moretus"),
    (500,0,r"(?ui)\bE\.*\s*Moyaerts","Emile Moyaerts"),
    (500,0,r'(?ui)H\.*Moeremans','Henri Moeremans'),
    (500,0,r'(?ui)I\.*Meyskens','Isidoor Meyskens'),
    
    (500,0,r"Moeskroen Boomkwekerijstraat","Rue de la Pépinière"),
    (500,0,r"Moeskroen Busstation","Gare routière"),
    (500,0,r"Moeskroen Coq Anglais","Coq anglais"),
    (500,0,r"Moeskroen Gerechtsplein","Place de la Justice"),
    (500,0,r"Moeskroen Hospitaal","Hôpital"),
    (500,0,r"Moeskroen Koninklijke Laan","Avenue Royale"),
    (500,0,r"Moeskroen Leopoldstraat","Rue Léopold"),
    (500,0,r"Moeskroen Luxemburgstraat","Rue du Luxembourg"),
    (500,0,r"Moeskroen Marktplein","Place du Marché"),
    (500,0,r"Moeskroen Metropole","Métropole"),
    (500,0,r"Moeskroen Nmbs-Station","Gare SNCB"),
    (500,0,r"Moeskroen Petit Cornil","Petit-Cornil"),
    (500,0,r"Moeskroen Petit Pont","Petit-Pont"),
    (500,0,r"Moeskroen Phenix","Phoenix"),
    (500,0,r"Moeskroen Picardieplaats","Place Picardie"),
    
    (500,0,r"(?ui)\bL\.*Nantier","Leopold Nantier"),
    (500,0,r"(?ui)\bGebr\.*\s*Naudts","Gebroeders Naudts"),
    (500,0,r"(?ui)\bP\.*Nollekens","Pieter Nollekens"),
    (400,0,r'(?ui)\bnr\.*\s*(?P<number>\d+)',r' nummer \1'),
    (500,0,r'(?ui)\bnr\.*\s*(?P<naar>\w+)',r' naar \1 '),
    (500,0,r"P. Van Neylen","Pastoor Van Neylen"),

    (500,0,r"(?ui)\bMarg\.*v\.*Oostenrijk","Margaretha van Oostenrijk - Marguerite d'Autriche"),
    (500,0,r'Opgeeistenlaan','Opgeëistenlaan'),

    (500,0,r'(?ui)\bJ\.*\s*Palfijn','Jan Palfijn'),
    (500,0,r"Au Pelerin","Au Pèlerin"),
    (500,1,r'Dessel Perestraat','Dessel Peresstraat'),
    (500,0,r"(?ui)\bA\.*\s*Piessens","Alfons Piessens"),
    (500,1,r'Ukkel Pijnbomenstraat','Ukkel Pijnbomenweg'),
    (500,1,' (piloot bediening MSD)',''),
    (500,0,r"(?ui)\bLt\.*\s*Philippart","Luitenant Philippart"),
    (500,0,r"(?ui)\bJ\.*\s*Posenaer","Jozef Posenaer"),
    (500,0,r"(?ui)\bAug\.*Plovie","August Plovie"),

    (500,0,r'(?u)\bReg\.','Regiment'),
    (500,0,r'(?ui)\bJ\.*\s*Reusens','Jozef Reusens'),
    (500,0,r"(?ui)\bT\.*\s*Reyn","Theofiel Reyn"),
    (500,0,r'(?ui)\bRingl\.','Ringlaan'),
    (500,0,r"L. Robbe","Louis Robbe"),
    (500,0,r'K. Roeland','Klokke Roeland'),
    (500,0,r"(?ui)\bA\.*\s*Rodenbach","Albrecht Rodenbach"),
    (500,0,r'(?ui)\bF\.*\s*Roosevelt','Franklin Roosevelt'),
    (500,0,r"(?ui)\bL\.*Ruelens","Leopold Ruelens"),

    (500,0,r'(?ui)J\.*\s*.*?M\.*\s*Sabbe','Julius en Maurits Sabbe'),
    (500,0,r'(?ui)\bM\.?\s*Sabbe','Maurits Sabbe'),
    (500,0,r'(?ui)\bH\.*\s*Schoofs','Hendrik Schoofs'),
    (500,0,r'(?ui)\bR\.*\s*Schuman',' Robert Schuman'),
    (500,0,r'(?ui)Serg\.*\s*\b','Sergeant '),
    (500,0,r'Sint-Pieters Station','Sint-Pietersstation'),
    (500,0,r"(?ui)\bAnderlecht\s*Sint-Niklaas","Saint-Nicolas - Sint-Niklaas"),
    (500,0,r"(?ui)\bE\.*Sohie","Edgard Sohie"),
    (500,0,r'(?ui)\bE\.*\s*Soudan','Eugène Soudan'),
    (500,0,r"(?ui)\bP\.*\s*H\.*\s*Spaak","Paul Henri Spaak"),
    (500,0,r"(?ui)\bH\.*\s*Stassen","Henri Stassen"),
    (500,0,r"(?ui)\bJ\.*Stas","Jan Stas"),
    (500,0,r'Karel De Stoute',"Karel de Stoute"),
    (500,0,r'(?ui)T\sSteppeke',"'t Steppeke"),
    (500,0,r"(?ui)\bE\.*\s*Steurs","Eduard Steurs"),
    (500,0,r"(?ui)\bG\.*\s*Stijnen","Gerardus Stijnen"),
    (500,0,r"(?ui)\bJ\.*\s*Stobbaerts","Jan Stobbaerts"),
    (400,0,r'Stijn Streuvelstraat','Stijn Streuvelsstraat'),
    (500,0,r'(?u)S\.*\s*Streuvels','Stijn Streuvels'),

    # (500,0,r'(?ui)E\.*\s*Thieffry','Edmond Thieffry'),
    (500,0,r"(?ui)K\.*\s*Van\s*Thillo","Karel Van Thillo"), 
    (500,1,r'Tessenderlo Tessenderlo Chemie','Tessenderlo Chemie'),
    (500,0,r'T. Tuts','Theo Tuts'),

    (500,0,r"(?ui)\bL\.*\s*Van\s*Bercken","Lodewijk Van Bercken"),
    (500,0,r'(?ui)\bJ\.?\s*Van Hoof','Jef Van Hoof'),
    (500,0,r'(?ui)\bK\.?\s*V\.?\s*Mander','Karel Van Mander'),
    (500,0,r'(?ui)\bJ\.*\s*Van\s*Rijswijck','Jan Van Rijswijck'),
    (500,0,r"(?ui)\bCl\.*\s*Vanophem","Clement Vanophem"),
    (500,0,r"(?ui)\bO\.*\s*Van\s*Kesbeeck","Oscar Van Kesbeeck"),
    (500,1,r"TIELT A. VAN ZANDVOORDESTRAAT","Tielt Van Zandvoordestraat"),
    (500,0,r"TIELT TRAMSTRAAT","Tielt Tramstraat"),
    (500,0,r'C.V.D. Bussche',' Camiel Van den Bussche'),
    (500,0,r"(?ui)\bVan\s*Den\s*Nest","Van den Nest"),
    # (500,0,r'(?ui)E\.*Vander\s*Steenenstr\.*','Emile Vandersteenen'),
    # (500,0,r'(?ui)J\.*Vanderstraetenstr\.*','Jan Vanderstraeten'),
    (500,0,r"(?ui)\bD\.*\s*Vander\s*Vaeren","Désiré Vandervaeren"), 
    (500,0,r'E. Van Der Velde','Emiel Van Der Velde'),
    (500,0,r"(?ui)\bE\.*\s*Vandervelde","Emile Vandervelde"),
    (500,0,r'Vandewielelaan','Gomar Vandewielelaan'),
    (500,0,r"(?ui)\bR\.*\s*Verbeeck","René Verbeeck"),
    (500,0,r"(?ui)\bJ\.*\s*Van\s*Geel","Jan Frans van Geel"),
    (500,0,r'(?ui)A\.*\s*Vesalius','Andreas Vesalius'),
    (500,0,r"(?ui)\bC\.*\s*Verhavert","Cypriaan Verhavert"),
    (500,0,r'(?ui)\bR\.*\s*Veremanss*','Renaat Veremanss'),
    (500,0,r"(?ui)\bF\.*\s*Verbiest","Ferdinand Verbiest"),
    (500,0,r"(?ui)\bC\.*\s*Vissenaeken","Cornelius Vissenaekens"),
    (500,0,r"(?ui)\bH\.*\s*Vos","Herman Vos"),
    (500,0,r'(?ui)Fr\.*\s*De\s*Vriendt','Frans De Vriendt'),

    (500,1,r'Eglise Saint-Walburge','Église Sainte-Walburge'),
    (500,0,r'Eglise','Église'),
    (500,1,r"Wilsele Wijgm.stwg./Transf.","Wilsele Wijgmaalsesteenweg/Transformatorstation"),
    (500,0,r'J. De Wilde','Jean De Wilde'),
    (500,0,r'R. Willeme','René Willeme'),
    (500,0,r"(?ui)\bJ\.*F\.*\s*Willems","Jan Frans Willems"),
    (500,0,r"(?ui)\bK\.*\s*De\s*Wint","Karel De Wint"),
    (500,0,r'(?ui)\bW\.*\s*Wood','William Wood'),
    
    (500,0,r"(?ui)\bL\.*Wouters","Louis Wouters"),
    (500,0,r"(?ui)\bP\.*\s*Van\s*Lommel","P. van Lommel"),
    (500,0,r"(?ui)\bK\.*\s*Van\s*De\s*Woestijne","Karel Van de Woestijne"),
    
    (500,0,r"Weg Op Zwankendamme","Weg op Zwankendamme"),
    
    (500,0,r'Industriezone Bl Toren','Industriezone Blauwe Toren'),
    (500,0,r"(?ui)\bHotel\s*De\s*Ville","Hôtel De Ville"),
    (500,0,r"Park De Rode Poort","Park de Rode Poort"),
    (500,0,r"Baron De Serret","Baron de Serret"),
    (500,0,r"Fort Van Beieren","Fort van Beieren"),
    (500,0,r"(?ui)\bCC\b","Cultureel Centrum"),
    (500,0,r"(?ui)\bRue\s*Th\.*Piat","Rue Théophile Piat"),
    (500,0,r'Leuven Naamse Poort','Leuven Naamsepoort'),
    (500,0,r'Leuven Tiense Poort','Leuven Tiensepoort'),
    (500,0,r'Leuven Tervuurse Poort','Leuven Tervuursepoort'),
    
   

    (998,0,r',',', '),
    (999,0,r'(?i)\s+',' '),

   ]
def nameconversion(identifier,zone):
    name=identifier
    for order, final, short,long in commonabbreviations:
        if short == long and short == identifier:
            # print ('Winner: ' + short)
            if final:
                break
            else:
                continue
        # print(zone + '  ' + name + '  ' + short + '  ' + long)
        origname=name
        if short[0:2]=='(?':
            if name: name=re.sub(short,long,name)
        else:
            if name: name=name.replace(short,long)
        if origname!=name:
            # print ('Winner: ' + short)
            if final: break
    return omitlargercitynames(name,zone).strip()

def omitlargercitynames(name,zone):
    if not(name): name=''
    if name and not(leaveCityNameAnywayRE.search(name)) and not((zone in ['79','80','61','68']) or 'Sas van Gent' in name):
        #zone 79,80: Vorst bij Veerle, zone 61,68: Deurne bij Diest, zone 31: Sas van Gent
        for city, replacement in citynamesToOmit:
            if city in name:
                name = name.replace(city+' ',replacement).strip()
                continue
    return name

def xmlsafe(name):
    return name.replace('&','&amp;').replace("'","&apos;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def urlsafe(name):
    return xmlsafe(name).replace(' ','%20')
