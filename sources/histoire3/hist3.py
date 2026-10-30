"""Banque Histoire 3ème : 6 thèmes x 8 paires de questions.
Série A = questions 1-48, série B = 49-96 : la question n + 48 porte sur le même sujet que la question n.
Dans chaque question, la première réponse est la bonne."""
import json, os, random

OUT = "build"
os.makedirs(OUT, exist_ok=True)
HALF = 48

THEMES = {
    "pgm": ("Première Guerre mondiale", "8A5A2B"),
    "tot": ("Démocraties et totalitarismes", "6A4C93"),
    "sgm": ("Seconde Guerre mondiale et France occupée", "C0503A"),
    "mon": ("Le monde depuis 1945", "1F6FA8"),
    "rep": ("La République en France depuis 1944", "2E7D6B"),
    "nc": ("Nouvelle-Calédonie depuis 1940", "C77F0A"),
}

# (question A, answers A), (question B, answers B) ; first answer = right one
PAIRS = {
"pgm": [
  (("En quelle année commence la Première Guerre mondiale ?", ["1914", "1912", "1916", "1918"]),
   ("En quelle année se termine la Première Guerre mondiale ?", ["1918", "1914", "1917", "1920"])),
  (("Quelle date marque l'armistice de la Première Guerre mondiale ?", ["le 11 novembre 1918", "le 8 mai 1918", "le 14 juillet 1918", "le 28 juin 1919"]),
   ("Quel traité signé en 1919 impose la paix à l'Allemagne ?", ["le traité de Versailles", "le traité de Rome", "le traité de Maastricht", "le traité de Brest-Litovsk"])),
  (("Quelle bataille de 1916 oppose Français et Allemands pendant près de dix mois ?", ["Verdun", "la Marne", "Stalingrad", "Waterloo"]),
   ("Quelle grande offensive franco-britannique de 1916 est l'une des plus meurtrières de la guerre ?", ["la Somme", "Verdun", "Stalingrad", "El Alamein"])),
  (("Comment surnomme-t-on les soldats français de la Première Guerre mondiale ?", ["les poilus", "les grognards", "les maquisards", "les sans-culottes"]),
   ("Dans quoi vivent les soldats sur le front pendant la guerre de position ?", ["dans des tranchées", "dans des châteaux forts", "dans des abris antiatomiques", "dans des casernes en ville"])),
  (("Quel événement déclenche la Première Guerre mondiale en juin 1914 ?", ["l'attentat de Sarajevo", "l'invasion de la Pologne", "la révolution russe", "l'attaque de Pearl Harbor"]),
   ("Quelle alliance regroupe la France, le Royaume-Uni et la Russie en 1914 ?", ["la Triple-Entente", "la Triple-Alliance", "l'OTAN", "l'Axe"])),
  (("Quel génocide est commis par l'Empire ottoman pendant la Première Guerre mondiale ?", ["le génocide des Arméniens", "le génocide des Tutsi", "la Shoah", "le génocide cambodgien"]),
   ("En quelles années a lieu l'essentiel du génocide des Arméniens ?", ["1915-1916", "1939-1945", "1870-1871", "1994"])),
  (("Comment appelle-t-on une guerre qui mobilise toute l'économie et toute la société ?", ["une guerre totale", "une guerre froide", "une guerre éclair", "une guerre de mouvement"]),
   ("Quel rôle tiennent beaucoup de femmes à l'arrière pendant la guerre ?", ["elles travaillent dans les usines", "elles combattent au front", "elles obtiennent le droit de vote", "elles dirigent l'armée"])),
  (("Quelle révolution éclate en Russie en octobre 1917 ?", ["la révolution bolchevique", "la Révolution française", "la révolution industrielle", "la révolution des Œillets"]),
   ("Quel pays entre en guerre aux côtés de la France et du Royaume-Uni en 1917 ?", ["les États-Unis", "l'Allemagne", "l'Autriche-Hongrie", "l'Empire ottoman"])),
],
"tot": [
  (("Qui dirige l'URSS de la fin des années 1920 à 1953 ?", ["Staline", "Lénine", "Trotski", "Khrouchtchev"]),
   ("Qui dirige l'Allemagne nazie de 1933 à 1945 ?", ["Hitler", "Mussolini", "Franco", "Bismarck"])),
  (("Quel parti dirige Hitler ?", ["le parti nazi (NSDAP)", "le parti communiste", "le parti fasciste", "le Front populaire"]),
   ("Qui dirige l'Italie fasciste à partir de 1922 ?", ["Mussolini", "Hitler", "Franco", "Staline"])),
  (("Comment s'appellent les camps de travail forcé en URSS ?", ["le Goulag", "les kolkhozes", "les ghettos", "les soviets"]),
   ("Comment s'appellent les exploitations agricoles collectives en URSS ?", ["les kolkhozes", "le Goulag", "les soviets", "les plans quinquennaux"])),
  (("Quel événement déclenche la grande crise économique de 1929 ?", ["le krach de Wall Street", "la chute du mur de Berlin", "le choc pétrolier", "la guerre de Corée"]),
   ("Quelle alliance des partis de gauche gagne les élections en France en 1936 ?", ["le Front populaire", "le Cartel des gauches", "la Résistance", "la Triple-Entente"])),
  (("Quelles lois de 1935 retirent la citoyenneté allemande aux Juifs ?", ["les lois de Nuremberg", "les lois Jules Ferry", "les accords de Munich", "les lois de Vichy"]),
   ("Comment s'appelle le pogrom organisé par les nazis en novembre 1938 ?", ["la Nuit de cristal", "la Nuit des longs couteaux", "la rafle du Vel d'Hiv", "le Blitz"])),
  (("Quelles sont les caractéristiques d'un régime totalitaire ?", ["un parti unique et la terreur", "des élections libres", "la séparation des pouvoirs", "la liberté de la presse"]),
   ("Comment les régimes totalitaires embrigadent-ils la jeunesse ?", ["par des jeunesses du parti unique", "par des syndicats libres", "par des partis d'opposition", "par une presse libre"])),
  (("Quels accords de 1938 laissent Hitler annexer les Sudètes ?", ["les accords de Munich", "le pacte germano-soviétique", "le traité de Versailles", "la conférence de Yalta"]),
   ("Quel pacte Hitler et Staline signent-ils en août 1939 ?", ["le pacte germano-soviétique", "les accords de Munich", "le pacte de Varsovie", "l'Axe Rome-Berlin"])),
  (("Qu'obtiennent les ouvriers français en 1936 ?", ["les congés payés", "le droit de vote des femmes", "la Sécurité sociale", "la semaine de 35 heures"]),
   ("Comment Hitler arrive-t-il au pouvoir en janvier 1933 ?", ["il est nommé chancelier", "par un coup d'État militaire", "par une révolution armée", "il est élu président"])),
],
"sgm": [
  (("Quel événement déclenche la Seconde Guerre mondiale le 1er septembre 1939 ?", ["l'invasion de la Pologne", "l'attaque de Pearl Harbor", "l'attentat de Sarajevo", "le débarquement en Normandie"]),
   ("Quelle attaque japonaise fait entrer les États-Unis dans la guerre en décembre 1941 ?", ["Pearl Harbor", "Hiroshima", "Midway", "Stalingrad"])),
  (("Quelle bataille marque le tournant de la guerre sur le front de l'Est en 1942-1943 ?", ["Stalingrad", "Verdun", "Waterloo", "Dunkerque"]),
   ("Où a lieu le débarquement allié du 6 juin 1944 ?", ["en Normandie", "en Provence", "en Sicile", "à Dunkerque"])),
  (("Comment appelle-t-on le génocide des Juifs commis par les nazis ?", ["la Shoah", "le Goulag", "la Nuit de cristal", "l'apartheid"]),
   ("Quel est le plus grand centre de mise à mort nazi ?", ["Auschwitz-Birkenau", "Drancy", "Dachau", "Buchenwald"])),
  (("À quelle date l'Allemagne nazie capitule-t-elle ?", ["le 8 mai 1945", "le 11 novembre 1918", "le 6 juin 1944", "le 2 septembre 1945"]),
   ("Quelles villes japonaises sont détruites par des bombes atomiques en août 1945 ?", ["Hiroshima et Nagasaki", "Tokyo et Kyoto", "Osaka et Kobe", "Pearl Harbor et Midway"])),
  (("Qui lance l'appel du 18 juin 1940 depuis Londres ?", ["le général de Gaulle", "le maréchal Pétain", "Jean Moulin", "Winston Churchill"]),
   ("Qui dirige le régime de Vichy ?", ["le maréchal Pétain", "le général de Gaulle", "Jean Moulin", "Léon Blum"])),
  (("Qui unifie les mouvements de la Résistance intérieure au nom du général de Gaulle ?", ["Jean Moulin", "le maréchal Pétain", "Georges Clemenceau", "Léon Blum"]),
   ("Comment s'appelle l'organisme créé en 1943 qui réunit les mouvements de Résistance ?", ["le Conseil national de la Résistance", "la Milice", "le Front populaire", "l'ONU"])),
  (("Quelle rafle de juillet 1942 arrête plus de 13 000 Juifs à Paris ?", ["la rafle du Vel d'Hiv", "la Nuit de cristal", "le massacre d'Oradour-sur-Glane", "la libération de Paris"]),
   ("Comment appelle-t-on la politique de Vichy qui coopère avec l'Allemagne nazie ?", ["la collaboration", "la Résistance", "la décolonisation", "la cohabitation"])),
  (("Quel service oblige à partir de 1943 de jeunes Français à aller travailler en Allemagne ?", ["le Service du travail obligatoire", "la Milice", "le CNR", "les FFI"]),
   ("En quelle année les SS massacrent-ils les habitants d'Oradour-sur-Glane ?", ["1944", "1940", "1942", "1945"])),
],
"mon": [
  (("Quelle organisation internationale est créée en 1945 pour maintenir la paix ?", ["l'ONU", "la SDN", "l'OTAN", "l'Union européenne"]),
   ("Comment appelle-t-on l'affrontement indirect entre les États-Unis et l'URSS de 1947 à 1991 ?", ["la guerre froide", "la guerre totale", "la guerre éclair", "la guerre de Cent Ans"])),
  (("Quel mur est construit en 1961 ?", ["le mur de Berlin", "le mur de l'Atlantique", "la Grande Muraille", "la ligne Maginot"]),
   ("En quelle année le mur de Berlin tombe-t-il ?", ["1989", "1961", "1991", "1945"])),
  (("Quelle crise de 1962 fait craindre une guerre nucléaire ?", ["la crise de Cuba", "le blocus de Berlin", "la guerre du Vietnam", "la crise de 1929"]),
   ("Quelle alliance militaire regroupe les États-Unis et l'Europe de l'Ouest à partir de 1949 ?", ["l'OTAN", "le pacte de Varsovie", "l'ONU", "la CEE"])),
  (("Quel pays obtient son indépendance en 1947, notamment grâce à l'action de Gandhi ?", ["l'Inde", "le Vietnam", "l'Algérie", "la Chine"]),
   ("En quelle année l'Algérie devient-elle indépendante ?", ["1962", "1954", "1945", "1958"])),
  (("Quel traité crée la Communauté économique européenne (CEE) en 1957 ?", ["le traité de Rome", "le traité de Versailles", "le traité de Maastricht", "le traité de Lisbonne"]),
   ("Quel traité crée l'Union européenne en 1992 ?", ["le traité de Maastricht", "le traité de Rome", "le traité de Versailles", "les accords de Schengen"])),
  (("En quelle année l'URSS disparaît-elle ?", ["1991", "1989", "1945", "1953"]),
   ("Quelle monnaie commune est mise en circulation en 2002 ?", ["l'euro", "l'écu", "le dollar", "le franc"])),
  (("Que se passe-t-il le 11 septembre 2001 ?", ["des attentats à New York", "la chute du mur de Berlin", "la fin de l'URSS", "l'invasion du Koweït"]),
   ("Quel pays l'Irak envahit-il en 1990, ce qui déclenche la guerre du Golfe ?", ["le Koweït", "l'Iran", "l'Afghanistan", "Israël"])),
  (("Comment appelle-t-on le processus par lequel les colonies deviennent indépendantes ?", ["la décolonisation", "la mondialisation", "la colonisation", "la collaboration"]),
   ("Quelle conférence réunit en 1955 des pays nouvellement indépendants d'Afrique et d'Asie ?", ["la conférence de Bandung", "la conférence de Yalta", "la conférence de Potsdam", "la conférence de Munich"])),
],
"rep": [
  (("En quelle année les Françaises votent-elles pour la première fois ?", ["1945", "1848", "1936", "1968"]),
   ("Quelle institution est créée en 1945 pour protéger les Français contre la maladie et la vieillesse ?", ["la Sécurité sociale", "les congés payés", "le RMI", "l'ONU"])),
  (("En quelle année la Ve République est-elle fondée ?", ["1958", "1946", "1962", "1981"]),
   ("Qui est le premier président de la Ve République ?", ["Charles de Gaulle", "Georges Pompidou", "François Mitterrand", "René Coty"])),
  (("Depuis 1962, comment le président de la République est-il élu ?", ["au suffrage universel direct", "par le Parlement", "par le Sénat", "nommé par le Premier ministre"]),
   ("Quelle ministre fait adopter en 1975 la loi qui autorise l'IVG ?", ["Simone Veil", "Simone de Beauvoir", "Marie Curie", "Louise Weiss"])),
  (("Quel président socialiste est élu en 1981 ?", ["François Mitterrand", "Jacques Chirac", "Valéry Giscard d'Estaing", "Georges Pompidou"]),
   ("Comment appelle-t-on la situation où le président et le Premier ministre sont de camps politiques opposés ?", ["la cohabitation", "l'alternance", "la collaboration", "la décentralisation"])),
  (("Quelle peine est abolie en France en 1981 ?", ["la peine de mort", "la prison à vie", "le service militaire", "l'esclavage"]),
   ("En quelle année l'âge de la majorité passe-t-il à 18 ans en France ?", ["1974", "1968", "1981", "1958"])),
  (("Que se passe-t-il en France en mai-juin 1968 ?", ["révolte étudiante et grève générale", "la Libération", "la fin de la guerre d'Algérie", "l'élection de Mitterrand"]),
   ("Comment appelle-t-on la période de forte croissance économique de 1945 à 1975 ?", ["les Trente Glorieuses", "la Belle Époque", "les Années folles", "la Grande Dépression"])),
  (("Quelle République est fondée en 1946 ?", ["la IVe République", "la IIIe République", "la Ve République", "la Ire République"]),
   ("Quel régime tombe en 1958, emporté par la crise de la guerre d'Algérie ?", ["la IVe République", "la IIIe République", "le régime de Vichy", "la Ve République"])),
  (("Quel texte fondamental organise la Ve République ?", ["la Constitution de 1958", "la Déclaration de 1789", "le Code civil", "le traité de Rome"]),
   ("Qui dirige le Gouvernement provisoire de la République française en 1944-1946 ?", ["Charles de Gaulle", "le maréchal Pétain", "François Mitterrand", "Léon Blum"])),
],
"nc": [
  (("Quand la Nouvelle-Calédonie se rallie-t-elle à la France libre ?", ["en septembre 1940", "en juin 1944", "en mai 1945", "en septembre 1939"]),
   ("Quel pays installe une grande base militaire en Nouvelle-Calédonie à partir de 1942 ?", ["les États-Unis", "le Japon", "l'Allemagne", "le Royaume-Uni"])),
  (("Quelle unité de volontaires calédoniens et tahitiens combat en Afrique et en Europe ?", ["le Bataillon du Pacifique", "la Légion étrangère", "la Milice", "les Brigades internationales"]),
   ("Dans quelle bataille de 1942, en Libye, le Bataillon du Pacifique s'illustre-t-il ?", ["Bir Hakeim", "Verdun", "Stalingrad", "Pearl Harbor"])),
  (("Quel régime discriminatoire visant les Kanak est aboli en 1946 ?", ["le Code de l'indigénat", "l'apartheid", "le STO", "le Code noir"]),
   ("Quel statut la Nouvelle-Calédonie obtient-elle en 1946 ?", ["territoire d'outre-mer", "département d'outre-mer", "État indépendant", "protectorat"])),
  (("Quel parti, fondé en 1953, a pour devise « Deux couleurs, un seul peuple » ?", ["l'Union calédonienne", "le FLNKS", "le Front populaire", "le parti communiste"]),
   ("Quel mouvement indépendantiste est créé en 1984 ?", ["le FLNKS", "l'Union calédonienne", "le Front populaire", "le Bataillon du Pacifique"])),
  (("Quels accords mettent fin aux « Événements » en 1988 ?", ["les accords de Matignon", "l'accord de Nouméa", "les accords de Munich", "les accords d'Évian"]),
   ("Quels responsables se serrent la main lors des accords de Matignon ?", ["Jean-Marie Tjibaou et Jacques Lafleur", "de Gaulle et Michel Rocard", "Jean Moulin et Jacques Lafleur", "Mitterrand et de Gaulle"])),
  (("En quelle année l'accord de Nouméa est-il signé ?", ["1998", "1988", "1946", "2018"]),
   ("Comment appelle-t-on la période de violences en Nouvelle-Calédonie de 1984 à 1988 ?", ["les « Événements »", "la Révolution", "la guerre froide", "la Belle Époque"])),
  (("Combien de consultations sur l'accession à la pleine souveraineté ont lieu de 2018 à 2021 ?", ["3", "1", "2", "4"]),
   ("Quel est le résultat des consultations de 2018, 2020 et 2021 ?", ["le « non » l'emporte", "le « oui » l'emporte", "elles sont annulées", "il y a égalité"])),
  (("Quel métal est la grande richesse minière de la Nouvelle-Calédonie ?", ["le nickel", "l'or", "le cuivre", "l'uranium"]),
   ("Quel centre culturel kanak est inauguré à Nouméa en 1998 ?", ["le centre culturel Tjibaou", "le centre Pompidou", "le musée du quai Branly", "le musée du Louvre"])),
],
}

Q = {}
for ti, th in enumerate(THEMES):
    assert len(PAIRS[th]) == 8, th
    for k, (a, b) in enumerate(PAIRS[th]):
        n = ti * 8 + k + 1
        for nn, (st, opts) in ((n, a), (n + HALF, b)):
            assert len(opts) == 4 and len(set(opts)) == 4, (nn, opts)
            Q[nn] = (th, st, opts)
assert len(Q) == 2 * HALF


import re
def tex_esc(t):
    t = re.sub(r"\b(I|II|III|IV|V|XX)(re|e)\b", lambda m_: m_.group(1) + r"\textsuperscript{" + m_.group(2) + "}", t)
    return (t.replace("&", r"\&").replace("%", r"\%").replace("#", r"\#")
            .replace("« ", "«~").replace(" »", "~»").replace(" ?", "~?").replace(" :", "~:"))


def size_for(opts):
    L = max(len(o) for o in opts)  # one size for the four answers of a question
    return r"\Large" if L <= 22 else r"\large" if L <= 37 else r"\normalsize"


KEY = []
tex = [r"""\documentclass{article}
\usepackage[paperwidth=16cm,paperheight=14cm,margin=0cm]{geometry}
\usepackage[utf8]{inputenc}\usepackage[T1]{fontenc}
\usepackage{mathpazo}\usepackage{amsmath,amssymb}
\usepackage[most]{tcolorbox}
\pagestyle{empty}\setlength{\parindent}{0pt}
"""]
for th, (lab, col) in THEMES.items():
    tex.append(rf"\definecolor{{c{th}}}{{HTML}}{{{col}}}")
tex.append(r"\begin{document}")
for n in sorted(Q):
    th, st, opts = Q[n]
    rng = random.Random(n * 13 + 7)
    perm = [0, 1, 2, 3]
    rng.shuffle(perm)
    shown = [opts[i] for i in perm]
    good = "abcd"[perm.index(0)]
    KEY.append([n, th, good, opts[0]])
    lab = THEMES[th][0]
    num = n if n <= HALF else f"{n - HALF} B"
    ob = lambda i: (rf"\begin{{tcolorbox}}[enhanced,nobeforeafter,width=7.1cm,height=2.1cm,valign=center,colback=c{th}!6,colframe=c{th},arc=2.5mm,boxrule=0.9pt,left=3mm,right=2mm]"
                    rf"\begin{{tabular}}{{@{{}}l@{{\hspace{{2.5mm}}}}p{{5.6cm}}@{{}}}}{{\Large\bfseries\color{{c{th}}}{'abcd'[i]})}} & {size_for(shown)}\raggedright {tex_esc(shown[i])}\end{{tabular}}\end{{tcolorbox}}")
    tex.append(rf"""\begin{{tcolorbox}}[enhanced,width=16cm,height=14cm,colback=white,colframe=c{th},boxrule=2pt,arc=0mm,
left=6mm,right=6mm,top=0mm,bottom=4mm,sharp corners,
overlay={{\fill[c{th}] (frame.north west) rectangle ([yshift=-1.25cm]frame.north east);
\node[anchor=west,text=white,font=\sffamily\bfseries\LARGE] at ([xshift=5mm,yshift=-0.62cm]frame.north west) {{Question {num}}};
\node[anchor=east,text=white,font=\sffamily\itshape\large] at ([xshift=-5mm,yshift=-0.62cm]frame.north east) {{{lab}}};}}]
\vspace*{{1.75cm}}
\begin{{minipage}}[t][6.9cm][c]{{\linewidth}}\LARGE\centering
\begin{{minipage}}{{0.95\linewidth}}\raggedright\linespread{{1.25}}\selectfont {tex_esc(st)}\end{{minipage}}
\end{{minipage}}

\vfill
{ob(0)}\hfill{ob(1)}\par\vspace{{2.5mm}}
{ob(2)}\hfill{ob(3)}
\end{{tcolorbox}}
\newpage""")
tex.append(r"\end{document}")
open(f"{OUT}/hist3.tex", "w", encoding="utf-8").write("\n".join(tex))
json.dump([[n, th, g] for n, th, g, _ in KEY], open(f"{OUT}/questions.json", "w"))
with open(f"{OUT}/corrige.txt", "w", encoding="utf-8") as f:
    for n, th, g, a in KEY:
        f.write(f"Q{n if n <= HALF else str(n - HALF) + ' B'} ({THEMES[th][0]}) : {g}) {a}\n")
print(len(KEY), "questions")
