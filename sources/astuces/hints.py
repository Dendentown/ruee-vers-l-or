"""Astuces (objet « lampe ») : une phrase par type de question, sans donner la réponse.
Produit hints.json : { niveau: { "n": astuce } } pour toutes les questions (séries A et B)."""
import json, re

# ---------------------------------------------------------------- 5ème : règles sur l'énoncé (séries A 1-250, B = n + 250)
R5 = [
 ("geo", r"construire un triangle", "Inégalité triangulaire : la plus grande longueur doit être plus petite que la somme des deux autres."),
 ("geo", r"isocèle", "Dans un triangle isocèle en C, les angles en A et en B sont égaux, et les trois angles font 180° en tout."),
 ("geo", r"rectangle en", "L'angle droit mesure 90° : les deux autres angles du triangle ont une somme de 90°."),
 ("geo", r"symétrique", "Le centre de symétrie est le milieu du segment qui relie un point à son symétrique."),
 ("geo", r"parallélogramme.*périmètre", "Dans un parallélogramme, les côtés opposés ont la même longueur : périmètre = 2 × (côté 1 + côté 2)."),
 ("geo", r"aire du parallélogramme", "Aire d'un parallélogramme = base × hauteur : prends la hauteur perpendiculaire à la base, pas le côté oblique."),
 ("geo", r"parallélogramme", "Dans un parallélogramme, les angles opposés sont égaux et deux angles consécutifs font 180° ensemble."),
 ("geo", r"aire du triangle", "Aire d'un triangle = base × hauteur ÷ 2, avec la hauteur perpendiculaire à la base."),
 ("geo", r"parallèles", "Avec deux droites parallèles coupées par une sécante, les angles alternes-internes et les angles correspondants sont égaux."),
 ("geo", r"angle", "La somme des trois angles d'un triangle est toujours égale à 180°."),
 ("rel", r"coordonnées", "On écrit (abscisse ; ordonnée) : on lit d'abord sur l'axe horizontal, puis sur l'axe vertical."),
 ("rel", r"abscisse", "Compte les graduations à partir de 0 : à gauche de 0, les abscisses sont négatives."),
 ("rel", r"indique le thermomètre", "Sous le 0, les températures sont négatives : compte les graduations à partir de 0."),
 ("rel", r"plus petit|plus grand", "Un nombre négatif est plus petit qu'un positif ; entre deux négatifs, le plus petit est le plus loin de zéro."),
 ("rel", r"distance entre", "Une distance est toujours positive : compte les unités qui séparent les deux points sur la droite graduée."),
 ("rel", r"calcul", "Soustraire un nombre, c'est ajouter son opposé ; avec deux signes différents, on fait la différence des distances à zéro."),
 ("rel", r"température|monte|remonte|descend|niveau|gagne|perd", "Monter ou gagner, c'est ajouter ; descendre ou perdre, c'est soustraire : imagine-toi sur une droite graduée."),
 ("fra", r"reste-t-il", "Ce qui reste = toutes les parts du gâteau moins les parts mangées."),
 ("fra", r"n'est pas colorée", "Compte les parts non colorées et le nombre total de parts égales."),
 ("fra", r"colorée", "Fraction colorée = nombre de parts colorées ÷ nombre total de parts égales."),
 ("fra", r"Quelle égalité", "Deux fractions sont égales quand elles colorent la même longueur de bande."),
 ("fra", r"abscisse", "Regarde en combien de parts égales l'unité est partagée, puis compte les parts jusqu'au point."),
 ("fra", r"fraction est égale", "On obtient une fraction égale en multipliant le numérateur et le dénominateur par le même nombre."),
 ("fra", r"simplifiée", "Divise le numérateur et le dénominateur par un même diviseur commun, le plus grand possible."),
 ("fra", r"calcul", "Pour additionner ou soustraire des fractions, mets-les d'abord au même dénominateur, puis calcule les numérateurs."),
 ("fra", r"Compare|signe faut-il", "Mets les deux fractions au même dénominateur pour les comparer, ou compare les longueurs colorées."),
 ("fra", r"minutes", "Une heure dure 60 minutes : un quart d'heure, c'est 15 minutes, un tiers d'heure, 20 minutes."),
 ("fra", r"trajet", "Regarde en combien de parts égales le trajet de 0 à 1 est partagé, puis compte jusqu'au point K."),
 ("fra", r"Combien|quart", "Pour prendre une fraction d'une quantité : divise par le dénominateur, puis multiplie par le numérateur."),
 ("pro", r"Quel tableau", "Un tableau est de proportionnalité si on passe d'une ligne à l'autre en multipliant toujours par le même nombre."),
 ("pro", r"coefficient|Par quel nombre", "Le coefficient s'obtient en divisant un nombre de la 2e ligne par le nombre qui est au-dessus."),
 ("pro", r"remplace", "Trouve par quel nombre on multiplie la 1re ligne pour obtenir la 2e, puis applique-le à la colonne du « ? »."),
 ("pro", r"Quel est le résultat \?", "10 %, c'est diviser par 10 ; 25 %, prendre le quart ; 50 %, prendre la moitié ; 20 %, deux fois 10 %."),
 ("pro", r"réduction|soldé|nouveau prix", "Calcule d'abord la réduction (le pourcentage du prix) ; nouveau prix = prix de départ − réduction."),
 ("pro", r"moyenne", "Moyenne = somme de toutes les valeurs ÷ nombre de valeurs."),
 ("pro", r"fréquence", "Fréquence = effectif de la valeur ÷ effectif total."),
 ("pro", r"vitesse", "À vitesse constante, la distance est proportionnelle à la durée : passe par la distance parcourue en 5 ou 10 minutes."),
 ("pro", r"diagramme|mois|livres", "Lis la hauteur de chaque barre sur l'axe vertical ; l'effectif total est la somme de toutes les barres."),
 ("pro", r"proportionnel|coûtent|Combien", "Calcule d'abord pour une seule unité (une personne, un objet), puis multiplie."),
 ("pba", r"L'événement .* est", "Un événement impossible a une probabilité de 0, un événement certain une probabilité de 1."),
 ("pba", r"L'événement", "Compte combien de faces du dé conviennent parmi les 6."),
 ("pba", r"plus de chances|plus souvent", "Ce qui revient le plus souvent (le plus de secteurs, le plus grand effectif) a le plus de chances de sortir."),
 ("pba", r"échelle", "Sur l'échelle : 0 = impossible, 1 = certain, et le milieu correspond à une chance sur deux."),
 ("pba", r"fréquence", "Fréquence = nombre de fois où le résultat est sorti ÷ nombre total de lancers."),
 ("pba", r"probabilité|Probabilité", "Probabilité = nombre de cas favorables ÷ nombre total de cas possibles (tous également probables)."),
]

stm = json.load(open("/home/claude/stmts5.json"))
TH5 = {"Géométrie": "geo", "Nombres relatifs": "rel", "Fractions": "fra", "Proportionnalité / statistiques": "pro", "Probabilités": "pba"}
H = {"5e": {}, "capes": {}, "tle": {}, "h3": {}}
missing = []
for n, th, en, op in stm:
    t = TH5.get(th) or next((v for k, v in TH5.items() if th.startswith(k[:5])), None)
    hint = next((h for tt, rx, h in R5 if tt == t and re.search(rx, en)), None)
    if not hint:
        missing.append((n, th, en))
        continue
    H["5e"][n] = hint
    H["5e"][n + 250] = hint
assert not missing, missing[:10]

# ---------------------------------------------------------------- CAPES : 50 types (thème ti, type k) -> questions ti*20 + 2k + 1, +2 ; série B = n + 100
CAPES = [
 "Écris l'expression sous la forme exp(n·ln(1 + a/n)) et utilise ln(1 + u) ≈ u quand u tend vers 0.",
 "Dérive le produit : (uv)' = u'v + uv', avec u = e^(ax) et v = cos(bx), puis remplace x par 0.",
 "Intègre par parties en dérivant ln x et en intégrant la puissance de x.",
 "Série géométrique : la somme des qⁿ pour n ≥ 0 vaut 1/(1 − q) quand |q| < 1.",
 "Décompose en éléments simples : 1/(n(n+k)) = (1/k)·(1/n − 1/(n+k)), puis repère le télescopage.",
 "Utilise les équivalents en 0 : e^u − 1 ≈ u et sin u ≈ u.",
 "Développement limité : ln(1 + u) = u − u²/2 + o(u²), avec u = ax.",
 "La limite ℓ d'une suite arithmético-géométrique vérifie ℓ = aℓ + b.",
 "Règle de d'Alembert : calcule la limite du quotient de deux coefficients consécutifs.",
 "Les solutions de y' + ay = 0 sont de la forme y = C·e^(−ax) ; trouve C avec la condition initiale.",
 "Algorithme d'Euclide : remplace le couple (a, b) par (b, reste de a par b) jusqu'à un reste nul.",
 "Cherche la plus petite puissance de 2 qui vaut 1 modulo le diviseur, puis découpe l'exposant.",
 "Décompose le nombre en facteurs premiers p^a·q^b·… : le nombre de diviseurs est (a+1)(b+1)….",
 "Le chiffre des unités des puissances est périodique : trouve la période, puis le reste de l'exposant.",
 "Relations coefficients-racines : x₁ + x₂ = S, x₁x₂ = P, et x₁² + x₂² = S² − 2P.",
 "Indicatrice d'Euler : φ(n) = n × produit des (1 − 1/p) sur les diviseurs premiers p de n.",
 "Cherche un entier k tel que a × k ≡ 1 modulo le nombre premier (essaie les petites valeurs ou Bézout).",
 "Formule du binôme : le coefficient de x^k dans (1 + ax)^n vaut C(n, k)·a^k.",
 "Somme des carrés : 1² + 2² + … + n² = n(n+1)(2n+1)/6.",
 "Le reste est de degré 1, R = aX + b : il prend les mêmes valeurs que le polynôme aux racines du diviseur.",
 "Pour une matrice 2×2, det = ad − bc.",
 "Développe le déterminant 3×3 selon une ligne ou une colonne contenant des zéros.",
 "Calcule d'abord A², puis additionne ses coefficients diagonaux.",
 "Repère les lignes proportionnelles : le rang est le nombre de lignes vraiment indépendantes.",
 "Les valeurs propres sont les racines de det(A − λI) = 0 ; leur somme vaut la trace.",
 "Théorème du rang : dim ker f = dimension de l'espace de départ − rang de la matrice.",
 "Pour une matrice 2×2 inversible, échange a et d, change le signe de b et c, puis divise par le déterminant.",
 "Calcule A², A³… : un schéma apparaît pour le coefficient en haut à droite.",
 "Une matrice symétrique est déterminée par sa diagonale et ce qui est au-dessus : compte ces coefficients.",
 "Deux vecteurs sont orthogonaux quand leur produit scalaire x·x' + y·y' + z·z' est nul.",
 "Loi binomiale : P(X = k) = C(n, k)·p^k·(1 − p)^(n − k).",
 "Loi binomiale : V(X) = n·p·(1 − p).",
 "Loi géométrique de paramètre p : E(X) = 1/p.",
 "Loi de Poisson de paramètre λ : P(X = k) = e^(−λ)·λ^k / k!.",
 "Loi exponentielle de paramètre λ : P(X > t) = e^(−λt).",
 "Formule de Bayes : P(M | T) = P(M)·P(T | M) / P(T), avec P(T) par les probabilités totales.",
 "Loi uniforme sur [a, b] : V(X) = (b − a)²/12.",
 "V(aX + b) = a²·V(X) : la constante b ne change pas la variance.",
 "Anagrammes avec lettres répétées : n! divisé par le produit des factorielles des répétitions.",
 "Bienaymé-Tchebychev : P(|X − E(X)| ≥ a) ≤ V(X)/a².",
 "Le module d'une puissance est la puissance du module : |z^n| = |z|^n.",
 "Écris le nombre sous forme exponentielle r·e^(iθ) : l'argument de z^n est nθ, ramené dans ]−π, π].",
 "Les racines n-ièmes de l'unité sont les racines de Xⁿ − 1 : utilise les relations coefficients-racines.",
 "Distance d'un point au plan ax + by + cz = d : |ax₀ + by₀ + cz₀ − d| / √(a² + b² + c²).",
 "Distance d'un point à la droite ax + by + c = 0 : |ax₀ + by₀ + c| / √(a² + b²).",
 "Produit vectoriel : (y·z' − z·y', z·x' − x·z', x·y' − y·x').",
 "Aire du triangle ABC = |det(AB, AC)| / 2.",
 "Pour z ↦ az + b, le rapport est |a| et l'angle est un argument de a.",
 "La composée de deux réflexions d'axes sécants en O est une rotation de centre O d'angle le double de l'angle des axes.",
 "Mets l'équation sous la forme (x − a)² + (y − b)² = r² en complétant les carrés.",
]
for ti in range(5):
    for k in range(10):
        for j in range(2):
            n = ti * 20 + k * 2 + j + 1
            H["capes"][n] = H["capes"][n + 100] = CAPES[ti * 10 + k]

# ---------------------------------------------------------------- Terminale : 48 types (thème ti, type k) -> questions ti*16 + 2k + 1, +2 ; série B = n + 96
TLE = [
 # suites
 "Suite arithmétique : uₙ = u₀ + n × r.",
 "Somme des termes d'une suite géométrique : 1 + q + … + qⁿ = (q^(n+1) − 1)/(q − 1).",
 "Factorise par le terme de plus haut degré en haut et en bas : seuls les coefficients de n² comptent.",
 "La limite ℓ vérifie ℓ = a·ℓ + b : résous cette équation.",
 "Calcule u₁, u₂, u₃… : un schéma apparaît, lié aux carrés parfaits.",
 "(−1)ⁿ reste entre −1 et 1 : divise en haut et en bas par n.",
 "Pour une suite géométrique, on passe de u₃ à u₅ en multipliant deux fois par la raison.",
 "Calcule les puissances successives jusqu'à dépasser le nombre demandé (ou utilise ln).",
 # fonctions
 "Dérivée de (ax + b)³ : 3a(ax + b)².",
 "Dérivée d'un quotient : (u/v)' = (u'v − uv')/v².",
 "Tangente en a : y = f'(a)(x − a) + f(a).",
 "Une asymptote verticale apparaît là où le dénominateur s'annule.",
 "Un point d'inflexion est là où la dérivée seconde s'annule en changeant de signe.",
 "Étudie les variations de x³ − 3x : son maximum local vaut 2 et son minimum local −2.",
 "Dérive f, cherche où f'(x) = 0 sur ]0 ; +∞[, puis calcule f en ce point.",
 "Dérivée de √u : u'/(2√u).",
 # exponentielle et logarithme
 "Propriétés : e^a × e^b = e^(a+b) et e^a / e^b = e^(a−b).",
 "ln(X) = 0 exactement quand X = 1.",
 "ln(aᵏ) = k·ln(a) : écris le nombre comme une puissance de la base.",
 "Dérivée d'un produit : (x·e^(ax))' = e^(ax) + a·x·e^(ax).",
 "Divise en haut et en bas par eˣ : x²/eˣ tend vers 0 (croissances comparées).",
 "Dérivée de ln(u) : u'/u.",
 "Passe au logarithme : qⁿ < s équivaut à n > ln(s)/ln(q), car ln(q) < 0.",
 "e^X = a équivaut à X = ln(a) : résous ensuite l'équation du premier degré.",
 # intégrales et équations différentielles
 "Une primitive de xᵏ est x^(k+1)/(k+1).",
 "Une primitive de e^(ax) est e^(ax)/a.",
 "Une primitive de 1/x est ln x, et ln(e) = 1.",
 "Les primitives de e^(ax) sont e^(ax)/a + C : trouve C avec la valeur en 0.",
 "Valeur moyenne de f sur [a ; b] : (1/(b − a)) × l'intégrale de f de a à b.",
 "La solution constante de y' = ay + b vérifie 0 = ay + b.",
 "Les solutions de y' = ay sont y = C·e^(ax) ; trouve C avec f(0).",
 "Intégration par parties : une primitive de x·eˣ est (x − 1)eˣ.",
 # géométrie dans l'espace
 "Produit scalaire en repère orthonormé : xx' + yy' + zz'.",
 "Norme : √(x² + y² + z²).",
 "Deux vecteurs sont orthogonaux quand leur produit scalaire est nul.",
 "Un plan de vecteur normal (a ; b ; c) a une équation ax + by + cz + d = 0 : trouve d avec le point A.",
 "Remplace t par des valeurs entières dans la représentation paramétrique.",
 "Colinéaires : il existe k tel que u = k·v ; trouve k avec une coordonnée connue.",
 "Distance AB = √((x_B − x_A)² + (y_B − y_A)² + (z_B − z_A)²).",
 "Remplace x, y et z de la droite dans l'équation du plan, puis trouve t.",
 # probabilités et dénombrement
 "Loi binomiale de paramètre 1/2 : P(X = k) = C(n, k) / 2ⁿ.",
 "Espérance d'une loi binomiale : E(X) = n × p.",
 "Variance d'une loi binomiale : V(X) = n × p × (1 − p).",
 "P(A ∩ B) = P(A) × P_A(B).",
 "Probabilités totales : P(B) = P(A)·P_A(B) + P(Ā)·P_Ā(B).",
 "Choisir k éléments parmi n sans ordre : C(n, k) = n! / (k!(n − k)!).",
 "Avec répétitions et ordre, chaque caractère a n choix : nᵏ codes.",
 "Passe par l'événement contraire : P(X ≥ 1) = 1 − P(X = 0) = 1 − (1 − p)ⁿ.",
]
for ti in range(6):
    for k in range(8):
        for j in range(2):
            n = ti * 16 + k * 2 + j + 1
            H["tle"][n] = H["tle"][n + 96] = TLE[ti * 8 + k]

# ---------------------------------------------------------------- Histoire 3ème : une astuce par question (série A 1-48, série B 49-96)
HIST_A = [
 # Première Guerre mondiale
 "L'été de l'attentat de Sarajevo.", "Elle se termine par l'armistice signé à Rethondes.",
 "Une bataille symbole de la guerre d'usure, près de la Meuse.", "Un surnom lié à leurs barbes et moustaches.",
 "Tout commence dans la capitale de la Bosnie.", "Un peuple chrétien de l'Empire ottoman, en Anatolie.",
 "Toute la nation travaille pour le front : soldats, usines, finances, propagande.", "Lénine et les bolcheviks prennent le pouvoir.",
 # Démocraties et totalitarismes
 "Il succède à Lénine et impose la terreur stalinienne.", "Son nom complet est le Parti national-socialiste.",
 "Un acronyme russe, rendu célèbre par Soljenitsyne.", "Elle commence à la Bourse de New York, en octobre.",
 "Elles portent le nom de la ville des grands congrès nazis.", "Le contraire d'une démocratie : un seul parti, un seul chef.",
 "La France et le Royaume-Uni y cèdent à Hitler en 1938.", "Des acquis sociaux du gouvernement de Léon Blum.",
 # Seconde Guerre mondiale
 "L'Allemagne attaque son voisin de l'Est.", "La ville porte le nom du dirigeant de l'URSS.",
 "Un mot hébreu qui signifie « catastrophe ».", "C'est aujourd'hui un jour férié en France, au printemps.",
 "Il refuse l'armistice et parle à la radio de la BBC.", "Il rassemble la Résistance avant d'être arrêté en 1943.",
 "Le nom vient d'un vélodrome parisien.", "Il est créé par Vichy sous la pression de l'occupant.",
 # Le monde depuis 1945
 "Elle remplace la SDN après la guerre.", "Il coupe une ville allemande en deux.",
 "Une île des Caraïbes, des missiles soviétiques.", "Le pays de la non-violence et de la « Marche du sel ».",
 "Signé dans la capitale italienne.", "Deux ans après la chute du mur de Berlin.",
 "New York et Washington sont frappées par des avions détournés.", "Le contraire de la colonisation.",
 # La République en France depuis 1944
 "L'année de la fin de la guerre en Europe.", "L'année du retour au pouvoir du général de Gaulle.",
 "Ce sont les citoyens eux-mêmes qui votent pour le président.", "Il reste président quatorze ans.",
 "Robert Badinter défend cette loi.", "Des étudiants dans la rue et des usines en grève.",
 "Elle succède au Gouvernement provisoire et dure jusqu'en 1958.", "Elle est adoptée par référendum en septembre.",
 # Nouvelle-Calédonie depuis 1940
 "Quelques mois après l'appel du 18 juin.", "Des volontaires du Pacifique, calédoniens et tahitiens.",
 "Ce régime imposait des règles spéciales aux Kanak.", "Un parti qui réunit Kanak et Européens dans les années 1950.",
 "Ils sont signés à Paris, à l'hôtel de Matignon, résidence du Premier ministre.", "Dix ans après les accords de Matignon.",
 "Elles ont lieu environ tous les deux ans, de 2018 à 2021.", "Un métal extrait des mines à ciel ouvert, exporté dans le monde entier.",
]
HIST_B = [
 "La guerre dure plus de quatre ans.", "Il est signé dans la galerie des Glaces.",
 "Une offensive sur un fleuve de Picardie.", "Des fossés creusés dans la terre, protégés par des barbelés.",
 "Une « entente » entre trois pays.", "Il commence au printemps 1915.",
 "Les « munitionnettes » fabriquent les obus.", "Le pays du président Wilson.",
 # Démocraties et totalitarismes
 "Il fonde le Troisième Reich.", "Le Duce, à Rome.",
 "Des fermes collectives imposées aux paysans.", "Léon Blum en est le chef de gouvernement.",
 "Des vitrines brisées dans toute l'Allemagne.", "Les Jeunesses hitlériennes, par exemple.",
 "Un accord surprise entre deux ennemis idéologiques.", "Le président Hindenburg le nomme.",
 # Seconde Guerre mondiale
 "Une base navale américaine à Hawaï.", "Les plages d'Omaha Beach et d'Utah Beach.",
 "Un camp en Pologne occupée, symbole de la Shoah.", "Les deux premières bombes atomiques de l'histoire.",
 "Le maréchal vainqueur de Verdun.", "Le sigle de cet organisme est CNR.",
 "Le contraire de la Résistance.", "Quelques jours après le débarquement en Normandie.",
 # Le monde depuis 1945
 "Deux blocs qui s'opposent sans guerre directe entre eux.", "L'année du bicentenaire de la Révolution française.",
 "Un sigle anglais : NATO.", "Après huit ans de guerre et les accords d'Évian.",
 "Le traité porte le nom d'une ville des Pays-Bas.", "Les billets et les pièces arrivent le 1er janvier.",
 "Un petit émirat pétrolier du golfe Persique.", "Une ville d'Indonésie.",
 # La République en France depuis 1944
 "Une idée du programme du CNR.", "Le chef de la France libre devient président.",
 "Une ministre de la Santé, ancienne déportée.", "Deux camps doivent gouverner ensemble.",
 "Valéry Giscard d'Estaing vient d'être élu.", "Une période de croissance de trente ans.",
 "La guerre d'Algérie provoque la crise de mai 1958.", "Le chef de la France libre, revenu à Paris.",
 # Nouvelle-Calédonie depuis 1940
 "Des centaines de milliers de soldats arrivent dans le Pacifique.", "Une bataille dans le désert libyen, en 1942.",
 "La Nouvelle-Calédonie cesse alors d'être une colonie.", "Un front de mouvements indépendantistes kanak.",
 "Un leader indépendantiste kanak et un leader loyaliste.", "Une période de fortes tensions et de violences.",
 "Le résultat est le même aux trois consultations.", "Il porte le nom du leader kanak signataire des accords de Matignon.",
]
assert len(HIST_A) == 48 and len(HIST_B) == 48
for i in range(48):
    H["h3"][i + 1] = HIST_A[i]
    H["h3"][i + 49] = HIST_B[i]

for k, n in (("5e", 500), ("capes", 200), ("tle", 192), ("h3", 96)):
    assert sorted(H[k]) == list(range(1, n + 1)), k
json.dump(H, open("/home/claude/hints/hints.json", "w"), ensure_ascii=False)
print({k: len(v) for k, v in H.items()}, {k: len(set(v.values())) for k, v in H.items()})
