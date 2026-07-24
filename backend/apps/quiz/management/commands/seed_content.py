"""
Peuple la base avec du contenu educatif reel : categories de quiz, heros
historiques haitiens, chapitres d'aventure (un par departement) et leurs
questions. Idempotent (get_or_create partout) : peut etre relance sans
creer de doublons.

Usage : python manage.py seed_content
"""
import random

from django.core.management.base import BaseCommand

from apps.geography.models import Department, Level
from apps.heroes.models import Hero
from apps.quiz.models import Answer, Category, Question

CATEGORIES = [
    {
        "slug": "histoire",
        "name": "Histoire",
        "description": "La revolution haitienne et les grands evenements qui ont fait la nation.",
        "color": "#0057B8",
        "order": 1,
    },
    {
        "slug": "geographie",
        "name": "Geographie",
        "description": "Les 10 departements, les villes et les paysages d'Haiti.",
        "color": "#4CAF50",
        "order": 2,
    },
    {
        "slug": "heros",
        "name": "Heros",
        "description": "Les figures historiques qui ont marque Haiti.",
        "color": "#FFD447",
        "order": 3,
    },
    {
        "slug": "constitution",
        "name": "Constitution",
        "description": "Les textes fondateurs et les institutions de la Republique.",
        "color": "#D21034",
        "order": 4,
    },
    {
        "slug": "civisme",
        "name": "Civisme",
        "description": "Symboles nationaux et institutions civiques.",
        "color": "#8E44AD",
        "order": 5,
    },
    {
        "slug": "culture",
        "name": "Culture",
        "description": "Langues, musique, gastronomie et traditions haitiennes.",
        "color": "#FF8A00",
        "order": 6,
    },
]

HEROES = [
    {
        "slug": "toussaint-louverture",
        "name": "Toussaint Louverture",
        "biography": (
            "General en chef de l'armee de Saint-Domingue, il transforme d'anciens "
            "esclaves en une armee capable de tenir tete aux puissances coloniales. "
            "Capture par piege en 1802, il meurt en captivite au Fort de Joux, en "
            "France, l'annee suivante, sans voir l'independance qu'il a rendue possible."
        ),
        "quote": (
            "En me renversant, on n'a abattu a Saint-Domingue que le tronc de "
            "l'arbre de la liberte ; il repoussera par les racines, car elles "
            "sont profondes et nombreuses."
        ),
        "rarity": "legendary",
        "order": 1,
    },
    {
        "slug": "jean-jacques-dessalines",
        "name": "Jean-Jacques Dessalines",
        "biography": (
            "Ancien lieutenant de Toussaint Louverture, il prend la tete de "
            "l'armee indigene et proclame l'independance d'Haiti le 1er janvier "
            "1804 a Gonaives, devenant le premier chef d'Etat du pays sous le nom "
            "de Jacques Ier."
        ),
        "quote": "L'independance ou la mort.",
        "rarity": "legendary",
        "order": 2,
    },
    {
        "slug": "henri-christophe",
        "name": "Henri Christophe",
        "biography": (
            "Ancien general de la revolution, il fonde le Royaume d'Haiti dans le "
            "nord du pays et devient le roi Henri Ier. Il fait construire la "
            "Citadelle Laferriere pour prevenir tout retour des troupes francaises."
        ),
        "quote": "",
        "rarity": "epic",
        "order": 3,
    },
    {
        "slug": "alexandre-petion",
        "name": "Alexandre Petion",
        "biography": (
            "Premier president de la Republique d'Haiti (1807-1818), il redistribue "
            "des terres aux soldats et aux paysans. Il fournit armes, hommes et "
            "refuge a Simon Bolivar, contribuant a la liberation de l'Amerique du Sud."
        ),
        "quote": "",
        "rarity": "epic",
        "order": 4,
    },
    {
        "slug": "catherine-flon",
        "name": "Catherine Flon",
        "biography": (
            "Filleule de Dessalines selon la tradition, elle coud le premier "
            "drapeau haitien le 18 mai 1803 au Congres de l'Arcahaie, en retirant "
            "la bande blanche du drapeau francais."
        ),
        "quote": "",
        "rarity": "rare",
        "order": 5,
    },
    {
        "slug": "capois-la-mort",
        "name": "Capois-La-Mort",
        "biography": (
            "Officier de l'armee indigene, Francois Capois se distingue par son "
            "courage a la bataille de Vertieres le 18 novembre 1803 : demonte par "
            "un boulet, il se releve aussitot et charge de nouveau, forcant meme "
            "les troupes francaises a saluer sa bravoure."
        ),
        "quote": "",
        "rarity": "rare",
        "order": 6,
    },
    {
        "slug": "charlemagne-peralte",
        "name": "Charlemagne Peralte",
        "biography": (
            "Ne a Hinche, il dirige la resistance des Cacos contre l'occupation "
            "americaine d'Haiti (1915-1934). Il est assassine par les Marines "
            "americains en 1919 apres avoir ete trahi."
        ),
        "quote": "",
        "rarity": "epic",
        "order": 7,
    },
    {
        "slug": "anacaona",
        "name": "Anacaona",
        "biography": (
            "Cacique (reine) taino de Xaragua et poetesse, elle incarne la "
            "resistance des peuples autochtones face a la colonisation espagnole. "
            "Elle est executee par les autorites espagnoles au debut du 16e siecle."
        ),
        "quote": "",
        "rarity": "rare",
        "order": 8,
    },
    {
        "slug": "sanite-belair",
        "name": "Sanite Belair",
        "biography": (
            "Officiere de l'armee indigene, elle combat aux cotes de son mari "
            "Charles Belair contre le retablissement de l'esclavage. Capturee "
            "par les troupes francaises, elle est executee en 1802."
        ),
        "quote": "",
        "rarity": "rare",
        "order": 9,
    },
    {
        "slug": "marie-jeanne-lamartiniere",
        "name": "Marie-Jeanne Lamartiniere",
        "biography": (
            "Combattante de la bataille de la Crete-a-Pierrot en mars 1802, elle "
            "se bat aux cotes de son mari sous les ordres de Dessalines contre "
            "l'armee francaise du general Leclerc."
        ),
        "quote": "",
        "rarity": "rare",
        "order": 10,
    },
]

# Une entree par departement (cle = slug du Department deja charge via la
# fixture geography/departments.json). "hero" reference le slug d'un Hero
# ci-dessus, debloque en terminant ce chapitre.
LEVELS = {
    "ouest": {
        "name": "Naissance du drapeau",
        "description": "Port-au-Prince, la capitale, et le Congres de l'Arcahaie ou est ne le drapeau haitien.",
        "hero": "catherine-flon",
        "questions": [
            {
                "cat": "geographie", "diff": "easy",
                "text": "Quelle ville est la capitale d'Haiti, situee dans le departement de l'Ouest ?",
                "answers": ["Port-au-Prince", "Cap-Haitien", "Jacmel", "Gonaives"],
                "explanation": "Port-au-Prince est la capitale d'Haiti et la principale ville du departement de l'Ouest.",
            },
            {
                "cat": "histoire", "diff": "medium",
                "text": "Le 18 mai 1803, au Congres de l'Arcahaie (departement de l'Ouest), quel evenement fondateur a eu lieu ?",
                "answers": [
                    "La creation du drapeau haitien",
                    "La signature de la premiere constitution",
                    "La bataille de Vertieres",
                    "L'abolition officielle de l'esclavage",
                ],
                "explanation": "C'est au Congres de l'Arcahaie que le drapeau bleu et rouge est cree, symbole de l'union pour l'independance.",
            },
            {
                "cat": "heros", "diff": "easy", "type": "true_false",
                "text": "Catherine Flon aurait cousu le premier drapeau haitien en retirant la bande blanche du drapeau francais.",
                "correct": True,
                "explanation": "Selon la tradition, Catherine Flon coud le drapeau le 18 mai 1803 a l'Arcahaie.",
            },
            {
                "cat": "histoire", "diff": "easy",
                "text": "Quelle couleur a ete retiree du drapeau francais pour creer le drapeau haitien ?",
                "answers": ["Le blanc", "Le bleu", "Le rouge", "Le vert"],
                "explanation": "Le blanc est retire, ne laissant que le bleu et le rouge, symbole de l'union des Haitiens.",
            },
            {
                "cat": "geographie", "diff": "easy",
                "text": "Arcahaie, ou fut cree le drapeau haitien, se trouve dans quel departement ?",
                "answers": ["Ouest", "Nord", "Sud", "Artibonite"],
                "explanation": "L'Arcahaie est une commune du departement de l'Ouest.",
            },
            {
                "cat": "heros", "diff": "medium",
                "text": "Catherine Flon etait, selon la tradition, la filleule de quel personnage historique ?",
                "answers": ["Jean-Jacques Dessalines", "Toussaint Louverture", "Henri Christophe", "Alexandre Petion"],
                "explanation": "La tradition orale haitienne presente Catherine Flon comme la filleule de Dessalines.",
            },
        ],
    },
    "nord": {
        "name": "La Citadelle Laferriere",
        "description": "Cap-Haitien et le Royaume d'Haiti fonde par Henri Christophe dans le Nord.",
        "hero": "henri-christophe",
        "questions": [
            {
                "cat": "geographie", "diff": "easy",
                "text": "Quelle ville est la capitale du departement du Nord ?",
                "answers": ["Cap-Haitien", "Port-au-Prince", "Hinche", "Jeremie"],
                "explanation": "Cap-Haitien est la principale ville du Nord et l'ancienne capitale coloniale.",
            },
            {
                "cat": "heros", "diff": "easy",
                "text": "Qui a fait construire la Citadelle Laferriere ?",
                "answers": ["Henri Christophe", "Toussaint Louverture", "Alexandre Petion", "Jean-Jacques Dessalines"],
                "explanation": "Henri Christophe fait construire la Citadelle pour defendre le Royaume du Nord.",
            },
            {
                "cat": "histoire", "diff": "medium",
                "text": "Pourquoi la Citadelle Laferriere a-t-elle ete construite ?",
                "answers": [
                    "Pour se defendre d'un possible retour des troupes francaises",
                    "Pour servir de palais royal permanent",
                    "Pour abriter le premier gouvernement d'Haiti",
                    "Pour commemorer la bataille de Vertieres",
                ],
                "explanation": "Apres l'independance, la crainte d'un retour francais pousse Christophe a batir cette forteresse.",
            },
            {
                "cat": "histoire", "diff": "medium", "type": "true_false",
                "text": "Henri Christophe s'est proclame roi et a fonde le Royaume d'Haiti dans le nord du pays.",
                "correct": True,
                "explanation": "Christophe regne sous le nom d'Henri Ier de 1811 a 1820.",
            },
            {
                "cat": "culture", "diff": "medium",
                "text": "La Citadelle Laferriere et le Palais Sans-Souci sont classes par quelle organisation internationale ?",
                "answers": ["L'UNESCO", "L'ONU", "L'Union Africaine", "L'OEA"],
                "explanation": "Le site est inscrit au patrimoine mondial de l'UNESCO depuis 1982.",
            },
            {
                "cat": "heros", "diff": "hard",
                "text": "Comment le roi Henri Christophe est-il mort, en 1820 ?",
                "answers": ["Il s'est suicide", "Il a ete assassine", "Il est mort au combat", "Il est mort de maladie"],
                "explanation": "Affaibli et menace par une revolte, Henri Christophe se serait donne la mort avec une balle d'or.",
            },
        ],
    },
    "nord-est": {
        "name": "Terre de resistance",
        "description": "Fort-Liberte et la frontiere avec la Republique Dominicaine.",
        "hero": "toussaint-louverture",
        "questions": [
            {
                "cat": "geographie", "diff": "easy",
                "text": "Quelle ville est la capitale du departement du Nord-Est ?",
                "answers": ["Fort-Liberte", "Cap-Haitien", "Ouanaminthe", "Port-de-Paix"],
                "explanation": "Fort-Liberte est le chef-lieu du departement du Nord-Est.",
            },
            {
                "cat": "geographie", "diff": "easy",
                "text": "Le departement du Nord-Est partage une frontiere terrestre avec quel pays ?",
                "answers": ["La Republique Dominicaine", "Cuba", "La Jamaique", "Porto Rico"],
                "explanation": "Haiti et la Republique Dominicaine partagent l'ile d'Hispaniola.",
            },
            {
                "cat": "heros", "diff": "medium",
                "text": "Quel surnom celebre a ete donne a Toussaint Louverture par ses contemporains ?",
                "answers": ["Le Spartacus noir", "Le lion d'Haiti", "Le pere de la nation", "Le roi noir"],
                "explanation": "Toussaint Louverture est souvent compare a Spartacus pour son role de liberateur.",
            },
            {
                "cat": "heros", "diff": "medium", "type": "true_false",
                "text": "Toussaint Louverture est mort en Haiti, entoure des siens.",
                "correct": False,
                "explanation": "Il est mort en captivite en France, au Fort de Joux, loin d'Haiti.",
            },
            {
                "cat": "histoire", "diff": "hard",
                "text": "En quelle annee Toussaint Louverture a-t-il ete capture par les forces francaises ?",
                "answers": ["1802", "1799", "1804", "1806"],
                "explanation": "Il est capture par piege en juin 1802 puis deporte en France.",
            },
            {
                "cat": "heros", "diff": "medium",
                "text": "Quel titre Toussaint Louverture occupait-il a la tete de l'armee de Saint-Domingue ?",
                "answers": ["General en chef", "Empereur", "Roi", "President"],
                "explanation": "Il devient general en chef de l'armee et gouverneur de Saint-Domingue.",
            },
        ],
    },
    "nord-ouest": {
        "name": "La victoire de Vertieres",
        "description": "Port-de-Paix et le souvenir de la bataille decisive de l'independance.",
        "hero": "capois-la-mort",
        "questions": [
            {
                "cat": "geographie", "diff": "easy",
                "text": "Quelle ville est la capitale du departement du Nord-Ouest ?",
                "answers": ["Port-de-Paix", "Fort-Liberte", "Gonaives", "Cap-Haitien"],
                "explanation": "Port-de-Paix est le chef-lieu du departement du Nord-Ouest.",
            },
            {
                "cat": "histoire", "diff": "medium",
                "text": "A quelle date a eu lieu la bataille decisive de Vertieres ?",
                "answers": ["Le 18 novembre 1803", "Le 1er janvier 1804", "Le 14 aout 1791", "Le 18 mai 1803"],
                "explanation": "La victoire de Vertieres, le 18 novembre 1803, ouvre la voie a l'independance.",
            },
            {
                "cat": "heros", "diff": "medium",
                "text": "Pourquoi Francois Capois est-il surnomme 'Capois-La-Mort' ?",
                "answers": [
                    "Pour son courage exceptionnel a la bataille de Vertieres",
                    "Pour avoir survecu a une epidemie mortelle",
                    "Pour son role dans la redaction de la constitution",
                    "Pour avoir vaincu Napoleon en duel",
                ],
                "explanation": "Demonte par un boulet a Vertieres, il se releve aussitot et repart a l'assaut.",
            },
            {
                "cat": "heros", "diff": "medium", "type": "true_false",
                "text": "A la bataille de Vertieres, meme des soldats francais auraient salue le courage de Capois-La-Mort.",
                "correct": True,
                "explanation": "L'anecdote, rapportee par plusieurs historiens, est restee celebre en Haiti.",
            },
            {
                "cat": "histoire", "diff": "easy",
                "text": "La bataille de Vertieres a marque la defaite de quelle armee ?",
                "answers": ["L'armee francaise de Napoleon Bonaparte", "L'armee espagnole", "L'armee anglaise", "L'armee americaine"],
                "explanation": "L'expedition envoyee par Napoleon Bonaparte est vaincue a Vertieres.",
            },
            {
                "cat": "geographie", "diff": "medium",
                "text": "Vertieres, lieu de la bataille decisive, se trouve pres de quelle ville ?",
                "answers": ["Cap-Haitien", "Port-au-Prince", "Jacmel", "Les Cayes"],
                "explanation": "Vertieres est situe aux portes du Cap-Haitien.",
            },
        ],
    },
    "artibonite": {
        "name": "L'acte d'independance",
        "description": "Gonaives, ou l'independance d'Haiti a ete proclamee le 1er janvier 1804.",
        "hero": "jean-jacques-dessalines",
        "questions": [
            {
                "cat": "histoire", "diff": "easy",
                "text": "Ou l'independance d'Haiti a-t-elle ete proclamee, le 1er janvier 1804 ?",
                "answers": ["Gonaives", "Port-au-Prince", "Cap-Haitien", "Jacmel"],
                "explanation": "Dessalines proclame l'independance a Gonaives, dans l'Artibonite.",
            },
            {
                "cat": "geographie", "diff": "easy",
                "text": "Gonaives est la principale ville de quel departement ?",
                "answers": ["Artibonite", "Nord", "Centre", "Ouest"],
                "explanation": "Gonaives est le chef-lieu du departement de l'Artibonite.",
            },
            {
                "cat": "heros", "diff": "easy",
                "text": "Qui a proclame l'independance d'Haiti et en est devenu le premier chef d'Etat ?",
                "answers": ["Jean-Jacques Dessalines", "Toussaint Louverture", "Henri Christophe", "Alexandre Petion"],
                "explanation": "Dessalines devient le premier chef d'Etat de la nation independante.",
            },
            {
                "cat": "histoire", "diff": "medium", "type": "true_false",
                "text": "Jean-Jacques Dessalines s'est proclame empereur d'Haiti sous le nom de Jacques Ier.",
                "correct": True,
                "explanation": "Des septembre 1804, Dessalines devient l'empereur Jacques Ier.",
            },
            {
                "cat": "heros", "diff": "hard",
                "text": "Comment Jean-Jacques Dessalines est-il mort, en 1806 ?",
                "answers": ["Assassine au Pont-Rouge", "Mort au combat", "Exile en France", "Mort de maladie"],
                "explanation": "Il est assassine lors d'une embuscade au Pont-Rouge, pres de Port-au-Prince.",
            },
            {
                "cat": "geographie", "diff": "medium",
                "text": "La riviere Artibonite, qui donne son nom au departement, est surtout associee a quelle activite agricole ?",
                "answers": ["La riziculture", "La culture du cafe", "L'elevage bovin", "La peche en haute mer"],
                "explanation": "La vallee de l'Artibonite est le grenier a riz d'Haiti.",
            },
        ],
    },
    "centre": {
        "name": "Hinche et les Cacos",
        "description": "Le departement du Centre et la resistance contre l'occupation americaine.",
        "hero": "charlemagne-peralte",
        "questions": [
            {
                "cat": "geographie", "diff": "easy",
                "text": "Quelle ville est la capitale du departement du Centre ?",
                "answers": ["Hinche", "Mirebalais", "Gonaives", "Jacmel"],
                "explanation": "Hinche est le chef-lieu du departement du Centre.",
            },
            {
                "cat": "histoire", "diff": "medium",
                "text": "Charlemagne Peralte a dirige la resistance armee contre quelle occupation etrangere ?",
                "answers": ["L'occupation americaine (1915-1934)", "L'occupation francaise", "L'occupation espagnole", "L'occupation anglaise"],
                "explanation": "Les Etats-Unis occupent Haiti de 1915 a 1934.",
            },
            {
                "cat": "heros", "diff": "medium",
                "text": "Comment appelait-on les combattants de la resistance dirigee par Charlemagne Peralte ?",
                "answers": ["Les Cacos", "Les Tontons Macoutes", "Les Marrons", "Les Zandolites"],
                "explanation": "Les Cacos menent la guerilla contre les troupes d'occupation americaines.",
            },
            {
                "cat": "heros", "diff": "medium", "type": "true_false",
                "text": "Charlemagne Peralte est ne a Hinche, dans le departement du Centre.",
                "correct": True,
                "explanation": "Peralte est originaire de Hinche, capitale du departement du Centre.",
            },
            {
                "cat": "histoire", "diff": "hard",
                "text": "En quelle annee Charlemagne Peralte a-t-il ete tue par les Marines americains ?",
                "answers": ["1919", "1915", "1934", "1804"],
                "explanation": "Il est trahi et assassine en 1919.",
            },
            {
                "cat": "histoire", "diff": "medium",
                "text": "En quelle annee l'occupation americaine d'Haiti a-t-elle pris fin ?",
                "answers": ["1934", "1915", "1919", "1804"],
                "explanation": "Les dernieres troupes americaines quittent Haiti en 1934.",
            },
        ],
    },
    "sud": {
        "name": "Sur les traces des Tainos",
        "description": "Les Cayes et l'heritage du peuple taino, premier habitant de l'ile.",
        "hero": "anacaona",
        "questions": [
            {
                "cat": "geographie", "diff": "easy",
                "text": "Quelle ville est la capitale du departement du Sud ?",
                "answers": ["Les Cayes", "Jeremie", "Jacmel", "Miragoane"],
                "explanation": "Les Cayes est le chef-lieu du departement du Sud.",
            },
            {
                "cat": "heros", "diff": "medium",
                "text": "Qui etait Anacaona ?",
                "answers": ["Une cacique (reine) taino", "Une reine francaise", "Une generale de l'armee indigene", "Une presidente d'Haiti"],
                "explanation": "Anacaona regnait sur le territoire de Xaragua avant la colonisation.",
            },
            {
                "cat": "histoire", "diff": "medium",
                "text": "Anacaona a resiste face a quelle puissance coloniale ?",
                "answers": ["L'Espagne", "La France", "L'Angleterre", "Les Pays-Bas"],
                "explanation": "Les Espagnols sont les premiers colonisateurs de l'ile d'Hispaniola.",
            },
            {
                "cat": "heros", "diff": "hard", "type": "true_false",
                "text": "Anacaona a ete executee par les autorites espagnoles au debut du 16e siecle.",
                "correct": True,
                "explanation": "Elle est executee vers 1503 sur ordre des colonisateurs espagnols.",
            },
            {
                "cat": "histoire", "diff": "easy",
                "text": "Comment s'appelait le peuple autochtone d'Haiti auquel appartenait Anacaona ?",
                "answers": ["Les Tainos", "Les Azteques", "Les Mayas", "Les Incas"],
                "explanation": "Les Tainos habitaient l'ile avant l'arrivee des Europeens en 1492.",
            },
            {
                "cat": "geographie", "diff": "medium",
                "text": "Comment s'appelait, en langue taino, l'ile aujourd'hui partagee entre Haiti et la Republique Dominicaine ?",
                "answers": ["Quisqueya", "Xaragua", "Cibao", "Boriken"],
                "explanation": "Quisqueya (ou Hispaniola en espagnol) designe l'ile entiere.",
            },
        ],
    },
    "sud-est": {
        "name": "Jacmel, ville d'art",
        "description": "Jacmel, son architecture coloniale et son carnaval, et le sacrifice de Sanite Belair.",
        "hero": "sanite-belair",
        "questions": [
            {
                "cat": "geographie", "diff": "easy",
                "text": "Quelle ville est la capitale du departement du Sud-Est, celebre pour son carnaval ?",
                "answers": ["Jacmel", "Les Cayes", "Miragoane", "Jeremie"],
                "explanation": "Jacmel est le chef-lieu du departement du Sud-Est.",
            },
            {
                "cat": "heros", "diff": "medium",
                "text": "Sanite Belair a combattu aux cotes de qui contre le retablissement de l'esclavage ?",
                "answers": ["Son mari, Charles Belair", "Toussaint Louverture seul", "Henri Christophe", "Alexandre Petion"],
                "explanation": "Sanite et Charles Belair combattent ensemble en 1802.",
            },
            {
                "cat": "heros", "diff": "medium", "type": "true_false",
                "text": "Sanite Belair a ete capturee et executee par les troupes francaises en 1802.",
                "correct": True,
                "explanation": "Elle est executee la meme annee que son mari.",
            },
            {
                "cat": "culture", "diff": "medium",
                "text": "Jacmel est notamment reconnue pour quel artisanat traditionnel ?",
                "answers": ["Les masques en papier mache", "La poterie", "La ferronnerie d'art", "La vannerie"],
                "explanation": "Les masques en papier mache de Jacmel sont celebres dans tout le pays.",
            },
            {
                "cat": "culture", "diff": "medium",
                "text": "Quel evenement culturel important Jacmel accueille-t-elle chaque annee ?",
                "answers": ["Le carnaval de Jacmel", "Le festival du riz", "La fete du cafe", "Le festival du vaudou"],
                "explanation": "Le carnaval de Jacmel est l'un des plus renommes d'Haiti.",
            },
            {
                "cat": "heros", "diff": "hard",
                "text": "Selon le recit historique, comment Sanite Belair aurait-elle fait face a son execution ?",
                "answers": ["En refusant d'avoir les yeux bandes", "En s'evadant", "En se rendant", "En negociant sa grace"],
                "explanation": "Le courage de Sanite Belair face a la mort est reste dans la memoire collective.",
            },
        ],
    },
    "grand-anse": {
        "name": "Jeremie, cite des poetes",
        "description": "Jeremie et l'heritage d'Alexandre Petion, premier president de la Republique.",
        "hero": "alexandre-petion",
        "questions": [
            {
                "cat": "geographie", "diff": "easy",
                "text": "Quelle ville est la capitale du departement de la Grand'Anse ?",
                "answers": ["Jeremie", "Les Cayes", "Miragoane", "Hinche"],
                "explanation": "Jeremie est le chef-lieu du departement de la Grand'Anse.",
            },
            {
                "cat": "culture", "diff": "medium",
                "text": "Jeremie est surnommee la 'cite des...' en raison du nombre d'ecrivains qui en sont originaires.",
                "answers": ["Poetes", "Rois", "Guerriers", "Musiciens"],
                "explanation": "Jeremie a vu naitre de nombreux ecrivains et poetes haitiens.",
            },
            {
                "cat": "heros", "diff": "medium",
                "text": "Alexandre Petion a ete le premier president de quelle partie d'Haiti, entre 1807 et 1818 ?",
                "answers": [
                    "La Republique d'Haiti (sud et ouest)",
                    "Le Royaume d'Haiti (nord)",
                    "La colonie francaise",
                    "L'Empire d'Haiti",
                ],
                "explanation": "Petion dirige la Republique du sud, pendant que Christophe regne au nord.",
            },
            {
                "cat": "histoire", "diff": "medium", "type": "true_false",
                "text": "Alexandre Petion a fourni des armes et un refuge a Simon Bolivar pour l'aider a liberer l'Amerique du Sud.",
                "correct": True,
                "explanation": "Bolivar sejourne en Haiti en 1815-1816 avec le soutien de Petion.",
            },
            {
                "cat": "civisme", "diff": "medium",
                "text": "Quelle politique agraire Alexandre Petion a-t-il mise en place envers les soldats et paysans ?",
                "answers": [
                    "La redistribution de terres",
                    "L'interdiction de posseder des terres",
                    "La collectivisation forcee",
                    "La location obligatoire aux anciens colons",
                ],
                "explanation": "Petion redistribue des terres, favorisant une paysannerie de petits proprietaires.",
            },
            {
                "cat": "histoire", "diff": "hard",
                "text": "En echange de l'aide d'Haiti, quelle promesse Simon Bolivar aurait-il faite a Petion ?",
                "answers": [
                    "Abolir l'esclavage dans les territoires liberes",
                    "Payer une dette de guerre",
                    "Ceder un territoire a Haiti",
                    "Reconnaitre Haiti aupres de l'Espagne",
                ],
                "explanation": "Bolivar promet d'abolir l'esclavage en echange du soutien haitien.",
            },
        ],
    },
    "nippes": {
        "name": "Miragoane, jeune departement",
        "description": "Les Nippes, le plus recent des dix departements d'Haiti.",
        "hero": "marie-jeanne-lamartiniere",
        "questions": [
            {
                "cat": "geographie", "diff": "easy",
                "text": "Quelle ville est le chef-lieu du departement des Nippes ?",
                "answers": ["Miragoane", "Anse-a-Veau", "Petit-Trou-de-Nippes", "Baradères"],
                "explanation": "Miragoane est le chef-lieu du departement des Nippes.",
            },
            {
                "cat": "geographie", "diff": "medium", "type": "true_false",
                "text": "Les Nippes est le plus ancien des dix departements d'Haiti.",
                "correct": False,
                "explanation": "Au contraire, les Nippes est le plus recent : il a ete cree en 2003.",
            },
            {
                "cat": "geographie", "diff": "medium",
                "text": "Avant sa creation en 2003, le territoire des Nippes faisait partie de quel departement ?",
                "answers": ["La Grand'Anse", "L'Ouest", "Le Sud", "L'Artibonite"],
                "explanation": "Les Nippes a ete detache de la Grand'Anse pour devenir le 10e departement.",
            },
            {
                "cat": "heros", "diff": "medium",
                "text": "Marie-Jeanne Lamartiniere s'est illustree lors de quelle bataille de la Revolution haitienne ?",
                "answers": ["La bataille de la Crete-a-Pierrot", "La bataille de Vertieres", "Le siege de Jacmel", "La bataille de Savannah"],
                "explanation": "Elle combat vaillamment lors du siege de la Crete-a-Pierrot en 1802.",
            },
            {
                "cat": "geographie", "diff": "easy",
                "text": "Combien de departements compte Haiti aujourd'hui ?",
                "answers": ["10", "8", "9", "12"],
                "explanation": "Haiti est divise en 10 departements depuis la creation des Nippes en 2003.",
            },
            {
                "cat": "heros", "diff": "medium",
                "text": "A la bataille de la Crete-a-Pierrot, Marie-Jeanne Lamartiniere combattait sous les ordres de quel general ?",
                "answers": ["Jean-Jacques Dessalines", "Toussaint Louverture", "Henri Christophe", "Alexandre Petion"],
                "explanation": "Dessalines commande la defense heroique du fort de la Crete-a-Pierrot.",
            },
        ],
    },
}

# Questions generales, non rattachees a un chapitre (utilisees notamment
# par le "Quiz rapide" de l'accueil).
EXTRA_QUESTIONS = [
    {
        "cat": "constitution", "diff": "medium",
        "text": "Quelle constitution haitienne est actuellement en vigueur ?",
        "answers": ["La Constitution de 1987", "La Constitution de 1805", "La Constitution de 1801", "La Constitution de 1918"],
        "explanation": "La Constitution de 1987, amendee depuis, regit aujourd'hui la Republique d'Haiti.",
    },
    {
        "cat": "constitution", "diff": "hard", "type": "true_false",
        "text": (
            "La Constitution de 1805, sous Dessalines, declarait que tous les "
            "Haitiens seraient designes sous la denomination generique de "
            "'Noirs', quelle que soit leur couleur de peau."
        ),
        "correct": True,
        "explanation": "L'article 14 de la Constitution imperiale de 1805 etablit cette egalite de denomination.",
    },
    {
        "cat": "constitution", "diff": "medium",
        "text": "Selon la Constitution de 1987, qui dirige le gouvernement aux cotes du president, chef de l'Etat ?",
        "answers": ["Le Premier ministre", "Le vice-president", "Le president de la Chambre", "Le doyen du Senat"],
        "explanation": "Haiti a un regime semi-presidentiel avec un president et un Premier ministre.",
    },
    {
        "cat": "constitution", "diff": "medium",
        "text": "Le pouvoir legislatif haitien est compose de deux chambres. Lesquelles ?",
        "answers": [
            "La Chambre des deputes et le Senat",
            "L'Assemblee nationale et le Conseil d'Etat",
            "La Chambre haute et la Chambre basse unique",
            "Le Congres et le Tribunal supreme",
        ],
        "explanation": "Le Parlement haitien est bicameral : Chambre des deputes et Senat.",
    },
    {
        "cat": "constitution", "diff": "hard",
        "text": "Qui a proclame la toute premiere constitution d'Haiti, en 1801, avant meme l'independance ?",
        "answers": ["Toussaint Louverture", "Jean-Jacques Dessalines", "Henri Christophe", "Alexandre Petion"],
        "explanation": "Toussaint Louverture promulgue une constitution des 1801, se nommant gouverneur a vie.",
    },
    {
        "cat": "civisme", "diff": "easy",
        "text": "Quelle est la devise nationale d'Haiti ?",
        "answers": ["L'Union fait la force", "Liberte, egalite, fraternite", "In God we trust", "Un seul peuple, une seule nation"],
        "explanation": "\"L'Union fait la force\" figure sur les armoiries et le drapeau d'Haiti.",
    },
    {
        "cat": "civisme", "diff": "medium",
        "text": "Comment s'appelle l'hymne national d'Haiti ?",
        "answers": ["La Dessalinienne", "La Marseillaise", "L'Haitienne", "Fiere Haiti Cherie"],
        "explanation": "La Dessalinienne est l'hymne national officiel d'Haiti depuis 1904.",
    },
    {
        "cat": "civisme", "diff": "hard",
        "text": "Qui a ecrit les paroles de l'hymne national haitien ?",
        "answers": ["Justin Lherisson", "Oswald Durand", "Felix Morisseau-Leroy", "Massillon Coicou"],
        "explanation": "Justin Lherisson ecrit les paroles, mises en musique par Nicolas Geffrard.",
    },
    {
        "cat": "civisme", "diff": "medium",
        "text": "Que trouve-t-on, avec un palmier, sur les armoiries d'Haiti ?",
        "answers": ["Deux canons et des drapeaux", "Deux epees et un bouclier", "Deux colombes", "Un soleil et une lune"],
        "explanation": "Les armoiries representent un palmier entoure de canons, de drapeaux et de boulets.",
    },
    {
        "cat": "civisme", "diff": "hard",
        "text": "Quel element coiffe le palmier sur les armoiries d'Haiti, symbole de liberte ?",
        "answers": ["Le bonnet phrygien", "Une couronne royale", "Un casque militaire", "Une etoile"],
        "explanation": "Le bonnet phrygien, symbole de liberte, surmonte le palmier des armoiries.",
    },
    {
        "cat": "culture", "diff": "easy",
        "text": "Quelles sont les deux langues officielles d'Haiti ?",
        "answers": ["Le francais et le creole haitien", "Le francais et l'espagnol", "L'anglais et le creole", "L'espagnol et le creole"],
        "explanation": "Le creole devient langue officielle aux cotes du francais avec la Constitution de 1987.",
    },
    {
        "cat": "culture", "diff": "medium",
        "text": "Quel plat traditionnel est mange par les Haitiens le 1er janvier, jour de l'independance ?",
        "answers": ["La soupe joumou", "Le griot", "Le riz collé aux pois", "Le tassot"],
        "explanation": "Cette soupe au giraumont, autrefois interdite aux esclaves, symbolise la liberte retrouvee.",
    },
    {
        "cat": "culture", "diff": "medium", "type": "true_false",
        "text": "La soupe joumou est reconnue par l'UNESCO comme patrimoine culturel immateriel de l'humanite.",
        "correct": True,
        "explanation": "L'UNESCO l'a inscrite sur cette liste en 2021.",
    },
    {
        "cat": "culture", "diff": "hard",
        "text": "Le konpa, genre musical embleme d'Haiti, a ete cree dans les annees 1950 par quel musicien ?",
        "answers": ["Nemours Jean-Baptiste", "Wyclef Jean", "Toto Bissainthe", "Michel Martelly"],
        "explanation": "Nemours Jean-Baptiste est considere comme le createur du konpa direct.",
    },
    {
        "cat": "culture", "diff": "medium",
        "text": "Quelle religion aux racines africaines est officiellement reconnue en Haiti depuis 2003 ?",
        "answers": ["Le vaudou", "Le bouddhisme", "L'hindouisme", "Le shintoisme"],
        "explanation": "Le vaudou haitien est reconnu comme religion a part entiere depuis 2003.",
    },
    {
        "cat": "culture", "diff": "hard",
        "text": "Le rara, genre musical et fete populaire, est traditionnellement pratique a quelle periode de l'annee ?",
        "answers": ["Pendant le Careme, avant Paques", "Pendant l'ete", "A Noel", "Uniquement en hiver"],
        "explanation": "Les bandes de rara defilent dans les rues durant le Careme.",
    },
    {
        "cat": "geographie", "diff": "easy",
        "text": "Avec quel pays Haiti partage-t-il l'ile d'Hispaniola ?",
        "answers": ["La Republique Dominicaine", "Cuba", "La Jamaique", "Porto Rico"],
        "explanation": "Haiti occupe le tiers ouest de l'ile, partagee avec la Republique Dominicaine.",
    },
    {
        "cat": "geographie", "diff": "hard",
        "text": "Quel est le plus haut sommet d'Haiti ?",
        "answers": ["Le Pic la Selle", "Le Morne Jean", "Le Pic Macaya", "La Citadelle"],
        "explanation": "Le Pic la Selle culmine a 2 680 metres, dans le massif de la Selle.",
    },
    {
        "cat": "geographie", "diff": "easy",
        "text": "Quelle est la monnaie officielle d'Haiti ?",
        "answers": ["La gourde", "Le peso", "Le dollar", "L'escudo"],
        "explanation": "La gourde (HTG) est la monnaie nationale d'Haiti.",
    },
    {
        "cat": "histoire", "diff": "medium",
        "text": "Haiti est le deuxieme pays des Ameriques a avoir obtenu son independance, apres :",
        "answers": ["Les Etats-Unis", "Le Canada", "Le Mexique", "Le Bresil"],
        "explanation": "Les Etats-Unis (1776) precedent Haiti (1804) parmi les nations independantes des Ameriques.",
    },
    {
        "cat": "histoire", "diff": "easy",
        "text": "En quelle annee Haiti a-t-il proclame son independance ?",
        "answers": ["1804", "1791", "1802", "1806"],
        "explanation": "L'independance est proclamee le 1er janvier 1804, aux Gonaives.",
    },
    {
        "cat": "histoire", "diff": "medium",
        "text": "Qui a proclame l'independance d'Haiti le 1er janvier 1804 ?",
        "answers": ["Jean-Jacques Dessalines", "Toussaint Louverture", "Henri Christophe", "Alexandre Petion"],
        "explanation": "Dessalines proclame l'independance et devient le premier chef d'Etat d'Haiti.",
    },
    {
        "cat": "histoire", "diff": "medium",
        "text": "Comment s'appelait Haiti sous la colonisation francaise ?",
        "answers": ["Saint-Domingue", "Hispaniola", "Quisqueya", "La Navidad"],
        "explanation": "La colonie francaise prospere portait le nom de Saint-Domingue.",
    },
    {
        "cat": "heros", "diff": "medium",
        "text": "Quel heros est considere comme le fondateur de la nation haitienne, ayant proclame l'independance en 1804 ?",
        "answers": ["Jean-Jacques Dessalines", "Toussaint Louverture", "Henri Christophe", "Alexandre Petion"],
        "explanation": "Dessalines est souvent designe comme le pere fondateur de la nation haitienne.",
    },
    {
        "cat": "heros", "diff": "hard",
        "text": "Quel general haitien a fait construire la Citadelle Laferriere pour se defendre d'un eventuel retour francais ?",
        "answers": ["Henri Christophe", "Alexandre Petion", "Jean-Jacques Dessalines", "Toussaint Louverture"],
        "explanation": "Henri Christophe, roi du Nord, fait construire la Citadelle apres l'independance.",
    },
    {
        "cat": "geographie", "diff": "medium",
        "text": "Combien de departements administratifs compte Haiti ?",
        "answers": ["10", "9", "12", "8"],
        "explanation": "Haiti est divise en 10 departements depuis 2003 (creation des Nippes).",
    },
    {
        "cat": "geographie", "diff": "easy",
        "text": "Quelle est la capitale d'Haiti ?",
        "answers": ["Port-au-Prince", "Cap-Haitien", "Jacmel", "Les Cayes"],
        "explanation": "Port-au-Prince, fondee en 1749, est la capitale et plus grande ville d'Haiti.",
    },
    {
        "cat": "civisme", "diff": "medium",
        "text": "Quelles sont les couleurs du drapeau haitien ?",
        "answers": ["Bleu et rouge", "Bleu, blanc et rouge", "Vert et rouge", "Noir et rouge"],
        "explanation": "Le bleu et le rouge, herites du drapeau francais depouille de son blanc, symbolisent l'union.",
    },
    {
        "cat": "civisme", "diff": "hard",
        "text": "Selon la tradition, ou le drapeau bicolore bleu et rouge a-t-il ete cree en 1803 ?",
        "answers": ["Au Congres de l'Arcahaie", "A Vertieres", "Aux Gonaives", "Au Cap-Haitien"],
        "explanation": "Au Congres de l'Arcahaie, Dessalines aurait dechire la bande blanche du drapeau francais.",
    },
    {
        "cat": "culture", "diff": "medium",
        "text": "Quel instrument en bambou ou en metal, embleme du rara et du carnaval haitien, sert de trompette ?",
        "answers": ["Le vaksin (vaccine)", "Le tambour djembe", "La guitare", "Le piano"],
        "explanation": "Le vaksin, ou vaccine, est une trompette rudimentaire au son caracteristique du rara.",
    },
]


class Command(BaseCommand):
    help = "Peuple la base avec les categories, heros, chapitres et questions de Defi Ayiti."

    def handle(self, *args, **options):
        categories = self._seed_categories()
        heroes = self._seed_heroes()
        question_count = 0
        level_count = 0

        for dept_slug, level_data in LEVELS.items():
            try:
                department = Department.objects.get(slug=dept_slug)
            except Department.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Departement '{dept_slug}' introuvable, chapitre ignore."))
                continue

            level, created = Level.objects.get_or_create(
                department=department,
                order=1,
                defaults={
                    "name": level_data["name"],
                    "description": level_data["description"],
                    "question_count": len(level_data["questions"]),
                    "unlocks_hero": heroes.get(level_data["hero"]),
                },
            )
            if created:
                level_count += 1

            question_count += self._seed_questions(
                level_data["questions"], categories, level=level, department=department
            )

        question_count += self._seed_questions(EXTRA_QUESTIONS, categories, level=None, department=None)

        self.stdout.write(self.style.SUCCESS(
            f"Contenu pret : {len(categories)} categories, {len(heroes)} heros, "
            f"{level_count} nouveaux chapitres, {question_count} nouvelles questions."
        ))

    def _seed_categories(self) -> dict:
        categories = {}
        for data in CATEGORIES:
            category, _ = Category.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                    "color": data["color"],
                    "order": data["order"],
                },
            )
            categories[data["slug"]] = category
        return categories

    def _seed_heroes(self) -> dict:
        heroes = {}
        for data in HEROES:
            hero, _ = Hero.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "biography": data["biography"],
                    "quote": data["quote"],
                    "rarity": data["rarity"],
                    "order": data["order"],
                },
            )
            heroes[data["slug"]] = hero
        return heroes

    def _seed_questions(self, question_list, categories, *, level, department) -> int:
        created_count = 0
        for q in question_list:
            category = categories[q["cat"]]
            question_type = q.get("type", "multiple_choice")

            question, created = Question.objects.get_or_create(
                text=q["text"],
                level=level,
                defaults={
                    "category": category,
                    "department": department,
                    "question_type": question_type,
                    "difficulty": q["diff"],
                    "explanation": q["explanation"],
                    "xp_reward": {"easy": 10, "medium": 15, "hard": 20}[q["diff"]],
                },
            )
            if not created:
                continue
            created_count += 1

            if question_type == "true_false":
                Answer.objects.create(question=question, text="Vrai", is_correct=q["correct"] is True, order=0)
                Answer.objects.create(question=question, text="Faux", is_correct=q["correct"] is False, order=1)
            else:
                # Le premier element de "answers" est toujours la bonne
                # reponse dans les donnees source (plus lisible a ecrire) ;
                # on melange l'ordre d'affichage pour ne pas toujours placer
                # la bonne reponse en premiere position.
                correct_text = q["answers"][0]
                shuffled = list(q["answers"])
                random.shuffle(shuffled)
                for i, answer_text in enumerate(shuffled):
                    Answer.objects.create(
                        question=question,
                        text=answer_text,
                        is_correct=(answer_text == correct_text),
                        order=i,
                    )
        return created_count
