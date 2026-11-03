"""Banque Mathématiques 6ème (programme du cycle 3, attendus de 6e) :
6 thèmes x 8 types de questions x 8 jeux de valeurs.
Séries A, B, C, D = questions 1-96, 97-192, 193-288, 289-384 (n + 96k = même question, autres valeurs).
Toutes les bonnes réponses sont calculées ici. La première réponse de chaque liste est la bonne."""
import json, os, random, re
from fractions import Fraction as F
from math import isqrt

OUT = "build"
os.makedirs(OUT, exist_ok=True)
HALF = 96
TYPES = []


def qtype(theme, hint, params):
    def deco(fn):
        assert len(params) == 8 and len(set(map(repr, params))) == 8, (fn.__name__, params)
        TYPES.append((theme, fn, params, hint))
        return fn
    return deco


def m(s):
    return f"${s}$"


def nb(x):
    """French number in LaTeX math: thin spaces between thousands, decimal comma (terminating decimals only)."""
    x = F(x)
    dd = x.denominator
    for f_ in (2, 5):
        while dd % f_ == 0:
            dd //= f_
    if dd != 1:  # not a decimal number: written as a fraction
        return lf(x)
    neg = x < 0
    x = abs(x)
    ip, fp = divmod(x.numerator, x.denominator)
    s = f"{ip:,}".replace(",", "\\,")
    if fp:
        d = x - ip
        k = 0
        while d.denominator != 1:
            d *= 10; k += 1
            assert k < 12, x
        s += "{,}" + str(int(d)).rjust(k, "0")
    return ("-" if neg else "") + s


def lf(x):
    x = F(x)
    if x.denominator == 1:
        return nb(x)
    return ("-" if x < 0 else "") + rf"\dfrac{{{abs(x.numerator)}}}{{{x.denominator}}}"


def sgn(x):
    return "(" + ("+" if x > 0 else "") + nb(x) + ")"


def expr(pairs):
    out = ""
    for c, v in pairs:
        c = F(c)
        if c == 0:
            continue
        sign = "-" if c < 0 else ("+" if out else "")
        a = abs(c)
        body = v if (v and a == 1) else (lf(a) if a.denominator != 1 else str(a.numerator)) + v
        out += sign + body
    return out or "0"


def rt(n):
    r = isqrt(n)
    return str(r) if r * r == n else rf"\sqrt{{{n}}}"


def u(v, unit):
    return m(rf"{v}~\text{{{unit}}}")


def dur(h):
    """duration in hours (Fraction) -> '2 h 30 min'."""
    mins = F(h) * 60
    assert mins.denominator == 1, h
    mins = int(mins)
    H, M = divmod(mins, 60)
    return (f"{H} h" if H else "") + (" " if H and M else "") + (f"{M} min" if M else "")


def pt(p):
    return rf"({nb(p[0])}\,;\,{nb(p[1])})"


# ============================================================ NOMBRES ENTIERS ET DÉCIMAUX
def D(s):
    """'1 208,53' -> Fraction"""
    return F(s.replace(" ", "").replace(",", "."))


def ds(s):
    """'1 208,53' -> LaTeX"""
    return s.replace(",", "{,}").replace(" ", "\\,")


RANKS = {"milliers": 3, "centaines": 2, "dizaines": 1, "unités": 0, "dixièmes": -1, "centièmes": -2, "millièmes": -3}


@qtype("num", "Les rangs après la virgule : dixièmes, puis centièmes, puis millièmes.",
       [("345,672", "centièmes"), ("1 208,53", "dizaines"), ("67,094", "millièmes"), ("5 431,8", "centaines"),
        ("902,375", "dixièmes"), ("18 064,2", "milliers"), ("3,509", "centièmes"), ("74,16", "unités")])
def _(p):
    s, rank = p
    ip, _, fp = s.replace(" ", "").partition(",")
    k = RANKS[rank]
    dg = ip[-1 - k] if k >= 0 else fp[-k - 1]
    others = [c for c in dict.fromkeys(ip + fp) if c != dg]
    return (rf"Dans le nombre ${ds(s)}$, quel est le chiffre des {rank} ?", m(dg), [m(c) for c in others])


@qtype("num", "Diviser par 10, 100, 1 000 : la virgule se déplace de 1, 2 ou 3 rangs vers la gauche.",
       [(347, 100), (52, 10), (8, 100), (1205, 1000), (63, 1000), (9, 10), (4507, 100), (36, 100)])
def _(p):
    a, b = p
    x = F(a, b)
    return (rf"Quelle est l'écriture décimale de $\dfrac{{{a}}}{{{b}}}$ ?", m(nb(x)), [m(nb(x * 10)), m(nb(x / 10)), m(nb(x * 100))])


@qtype("num", "Compare d'abord les parties entières, puis les chiffres des dixièmes, des centièmes…",
       [(("3,5", "3,45", "3,405", "3,054"), "grand"), (("12,09", "12,1", "12,089", "12,01"), "petit"),
        (("0,7", "0,69", "0,075", "0,701"), "grand"), (("5,03", "5,3", "5,003", "5,29"), "petit"),
        (("2,25", "2,5", "2,205", "2,052"), "grand"), (("8,9", "8,89", "8,099", "8,91"), "petit"),
        (("10,1", "10,01", "10,11", "10,011"), "grand"), (("0,4", "0,39", "0,401", "0,0499"), "petit")])
def _(p):
    v, w = p
    best = (max if w == "grand" else min)(v, key=D)
    return (rf"Quel est le plus {w} de ces quatre nombres : ${'\\ ;\\ '.join(ds(x) for x in v)}$ ?",
            m(ds(best)), [m(ds(x)) for x in v if x != best])


def rnd10(x):
    return F((x * 10 * 2 + 1) // 2, 10)


@qtype("num", "Pour arrondir au dixième, regarde le chiffre des centièmes : 5 ou plus, on arrondit au-dessus.",
       ["12,46", "7,83", "0,95", "23,149", "5,05", "9,98", "3,333", "14,75"])
def _(s):
    x = D(s)
    r = rnd10(x)
    tr = F(int(x * 10), 10)
    alt = [tr if tr != r else r + F(1, 10), F((x * 2 + 1) // 2), F((x * 100 * 2 + 1) // 2, 100), r - F(1, 10) if r - F(1, 10) != tr else r + F(2, 10)]
    return (rf"Quel est l'arrondi au dixième de ${ds(s)}$ ?", m(nb(r)), [m(nb(a)) for a in alt])


@qtype("num", "Multiplier par 10, 100, 1 000 : la virgule se déplace de 1, 2 ou 3 rangs vers la droite.",
       [("3,45", 100), ("0,72", 10), ("5,3", 1000), ("0,068", 100), ("12,5", 10), ("0,4", 1000), ("7,09", 100), ("0,015", 1000)])
def _(p):
    s, f = p
    r = D(s) * f
    return (rf"Que vaut ${ds(s)}\times{nb(f)}$ ?", m(nb(r)), [m(nb(r * 10)), m(nb(r / 10)), m(nb(r * 100) if f != 10 else nb(r / 100))])


@qtype("num", "Diviser par 10, 100, 1 000 : la virgule se déplace vers la gauche ; ajoute des zéros si besoin.",
       [("52", 100), ("7,5", 10), ("340", 1000), ("6", 100), ("12,8", 10), ("905", 1000), ("4,2", 100), ("73", 10)])
def _(p):
    s, f = p
    r = D(s) / f
    return (rf"Que vaut ${ds(s)}\div{nb(f)}$ ?", m(nb(r)), [m(nb(r * 10)), m(nb(r / 10)), m(nb(D(s) * f))])


@qtype("num", "Écris d'abord la classe des millions, puis celle des milliers, puis celle des unités, avec 3 chiffres par classe.",
       [("deux millions trois cent mille quarante", 2300040, [2300400, 230040, 2030040]),
        ("quinze mille six cent huit", 15608, [15680, 156008, 1568]),
        ("trois cent quatre mille deux cents", 304200, [34200, 300402, 304020]),
        ("sept millions vingt mille cinq", 7020005, [720005, 7200005, 7020050]),
        ("quatre-vingt-dix mille trois cent un", 90301, [90031, 9301, 900301]),
        ("six cent mille soixante-dix", 600070, [60070, 6000070, 600700]),
        ("un million deux cent cinquante mille", 1250000, [1025000, 125000, 1205000]),
        ("quarante-huit mille neuf cents", 48900, [48090, 4890, 489000])])
def _(p):
    w, n, dis = p
    return (rf"Comment s'écrit en chiffres le nombre « {w} » ?", m(nb(n)), [m(nb(x)) for x in dis])


@qtype("num", "Ajoute un chiffre après les deux nombres pour en trouver un entre les deux : entre 2,3 et 2,4, il y a 2,35.",
       [("2,3", "2,4", "2,35", ["2,5", "2,29", "2,04"]), ("7", "7,1", "7,05", ["7,15", "6,9", "7,2"]),
        ("0,5", "0,6", "0,58", ["0,61", "0,49", "0,065"]), ("12,09", "12,1", "12,095", ["12,9", "12,11", "12,08"]),
        ("3", "3,01", "3,005", ["3,1", "3,015", "2,99"]), ("9,9", "10", "9,95", ["10,5", "9,09", "9,85"]),
        ("1,4", "1,5", "1,42", ["1,52", "1,04", "1,39"]), ("0,1", "0,2", "0,15", ["0,25", "0,015", "0,21"])])
def _(p):
    a, b, ans, dis = p
    assert D(a) < D(ans) < D(b) and all(not (D(a) < D(x) < D(b)) for x in dis)
    return (rf"Quel nombre est compris entre ${ds(a)}$ et ${ds(b)}$ ?", m(ds(ans)), [m(ds(x)) for x in dis])


# ============================================================ CALCULS
@qtype("cal", "Aligne les virgules les unes sous les autres avant d'additionner.",
       [("12,5", "7,85"), ("3,07", "14,6"), ("0,95", "2,4"), ("25,3", "4,75"), ("8,6", "9,48"), ("100,5", "0,75"), ("6,08", "3,9"), ("45", "2,35")])
def _(p):
    a, b = p
    s = D(a) + D(b)
    return (rf"Que vaut ${ds(a)}+{ds(b)}$ ?", m(nb(s)), [m(nb(s + F(1, 10))), m(nb(s - 1)), m(nb(s + 1)), m(nb(s + F(9, 10)))])


@qtype("cal", "Aligne les virgules ; complète avec des zéros pour avoir autant de chiffres après la virgule.",
       [("20", "6,35"), ("15,4", "8,75"), ("7,02", "3,5"), ("100", "45,8"), ("9,3", "2,47"), ("50,5", "12,75"), ("4", "0,85"), ("13,06", "5,9")])
def _(p):
    a, b = p
    d = D(a) - D(b)
    return (rf"Que vaut ${ds(a)}-{ds(b)}$ ?", m(nb(d)), [m(nb(d + 1)), m(nb(d - F(1, 10))), m(nb(d + F(1, 10))), m(nb(d - 1))])


@qtype("cal", "Multiplie sans les virgules, puis place autant de chiffres après la virgule qu'il y en a dans les deux facteurs.",
       [("2,5", "1,2"), ("0,4", "0,3"), ("3,6", "5"), ("1,5", "1,5"), ("0,25", "8"), ("4,2", "0,5"), ("12", "0,75"), ("0,6", "0,07")])
def _(p):
    a, b = p
    r = D(a) * D(b)
    return (rf"Que vaut ${ds(a)}\times{ds(b)}$ ?", m(nb(r)), [m(nb(r * 10)), m(nb(r / 10)), m(nb(D(a) + D(b))), m(nb(r * 100))])


@qtype("cal", "Dans une division euclidienne, le reste est toujours plus petit que le diviseur.",
       [(157, 12), (100, 7), (245, 9), (83, 6), (500, 13), (91, 4), (365, 7), (1000, 24)])
def _(p):
    a, b = p
    q, r = divmod(a, b)
    QR = lambda x, y: m(rf"q={x}\text{{ et }}r={y}")
    return (rf"Dans la division euclidienne de ${nb(a)}$ par ${b}$, quels sont le quotient $q$ et le reste $r$ ?",
            QR(q, r), [QR(q - 1, r + b), QR(q + 1, r), QR(q, r + 1), QR(r, q)])


@qtype("cal", "Un multiple de k est un nombre qui s'obtient en multipliant k par un nombre entier.",
       [(9, 117, [119, 109, 129]), (7, 91, [97, 87, 101]), (6, 84, [86, 64, 76]), (8, 96, [98, 86, 106]),
        (12, 132, [122, 142, 126]), (4, 236, [238, 226, 242]), (11, 143, [133, 153, 141]), (15, 165, [155, 175, 160])])
def _(p):
    k, a, dis = p
    assert a % k == 0 and all(x % k for x in dis)
    return (rf"Lequel de ces nombres est un multiple de ${k}$ ?", m(nb(a)), [m(nb(x)) for x in dis])


@qtype("cal", "Divisible par 2 : chiffre des unités pair ; par 5 : 0 ou 5 ; par 10 : 0 ; par 3 ou 9 : somme des chiffres divisible par 3 ou 9.",
       [(3, 342, [341, 346, 349]), (9, 4527, [4528, 4537, 4625]), (5, 1235, [1253, 1532, 1352]), (2, 3578, [3587, 5783, 7835]),
        (10, 4560, [4506, 5046, 6045]), (3, 1113, [1114, 1141, 1411]), (9, 819, [829, 812, 821]), (5, 2790, [2709, 2097, 7902])])
def _(p):
    k, a, dis = p
    assert a % k == 0 and all(x % k for x in dis)
    return (rf"Lequel de ces nombres est divisible par ${k}$ ?", m(nb(a)), [m(nb(x)) for x in dis])


@qtype("cal", "On calcule d'abord entre parenthèses, puis les multiplications et divisions, puis les additions et soustractions.",
       [("5+3\\times4", 17, [32, 20, 12]), ("20-4\\times3", 8, [48, 12, 17]), ("(7+5)\\times2", 24, [17, 14, 19]),
        ("18\\div3+6", 12, [2, 9, 27]), ("30-(8+2)", 20, [24, 40, 38]), ("4\\times(10-7)", 12, [33, 47, 30]),
        ("2+6\\times5-1", 31, [39, 40, 29]), ("(15-3)\\div4", 3, [14, 12, 9])])
def _(p):
    e, v, dis = p
    assert eval(e.replace("\\times", "*").replace("\\div", "/")) == v
    return (rf"Que vaut ${e}$ ?", m(nb(v)), [m(nb(x)) for x in dis])


@qtype("cal", "Pose la division et continue après la virgule en ajoutant des zéros au dividende.",
       [(7, 4), (9, 8), (15, 6), (3, 5), (21, 4), (13, 8), (1, 4), (34, 5)])
def _(a_b):
    a, b = a_b
    x = F(a, b)
    q, r = divmod(a, b)
    return (rf"Que vaut ${a}\div{b}$ ?", m(nb(x)), [m(rf"{q}{{,}}{r}") if F(f"{q}.{r}") != x else m(nb(x + 1)), m(nb(F(b, a))), m(nb(x * 10)), m(nb(x + F(1, 10)))])


# ============================================================ FRACTIONS
def rf_(a, b):
    return rf"\dfrac{{{a}}}{{{b}}}"


@qtype("fra", "Pour prendre a/b d'une quantité : divise-la par b, puis multiplie par a.",
       [(3, 4, 20), (2, 5, 35), (5, 6, 42), (3, 8, 40), (2, 3, 27), (7, 10, 60), (4, 9, 36), (3, 5, 45)])
def _(p):
    a, b, N = p
    r = F(a * N, b)
    return (rf"Combien vaut ${rf_(a, b)}$ de ${N}$ ?", m(nb(r)), [m(nb(F(N, b))), m(nb(a * N)), m(nb(N - r)), m(nb(r + 1))])


@qtype("fra", "On obtient une fraction égale en multipliant le numérateur et le dénominateur par le même nombre.",
       [(2, 3, 12), (3, 4, 20), (5, 6, 18), (1, 7, 21), (4, 5, 30), (3, 8, 24), (7, 9, 27), (2, 11, 44)])
def _(p):
    a, b, c = p
    x = a * c // b
    return (rf"Compléter : ${rf_(a, b)}=\dfrac{{?}}{{{c}}}$", m(nb(x)), [m(nb(a + c - b)), m(nb(a * c)), m(nb(c // b)), m(nb(x + 1))])


@qtype("fra", "a/b, c'est a ÷ b : pose la division.",
       [(3, 4), (1, 2), (7, 5), (1, 8), (9, 20), (3, 25), (11, 4), (13, 10)])
def _(p):
    a, b = p
    x = F(a, b)
    return (rf"Quelle est l'écriture décimale de ${rf_(a, b)}$ ?", m(nb(x)), [m(rf"{a}{{,}}{b}"), m(nb(F(b, a))), m(nb(x * 10)), m(nb(x / 10))])


@qtype("fra", "Une fraction est plus grande que 1 quand son numérateur est plus grand que son dénominateur.",
       [((7, 5), [(5, 7), (3, 4), (4, 4)]), ((9, 8), [(8, 9), (1, 2), (6, 6)]), ((11, 6), [(6, 11), (5, 6), (3, 3)]),
        ((5, 3), [(3, 5), (2, 3), (7, 7)]), ((13, 12), [(12, 13), (1, 3), (9, 9)]), ((8, 7), [(7, 8), (2, 5), (5, 5)]),
        ((10, 9), [(9, 10), (4, 7), (2, 2)]), ((15, 4), [(4, 15), (3, 8), (8, 8)])])
def _(p):
    a, dis = p
    return ("Laquelle de ces fractions est plus grande que $1$ ?", m(rf_(*a)), [m(rf_(*d)) for d in dis])


@qtype("fra", "Le nombre qui, multiplié par b, donne a, est le quotient a/b.",
       [(3, 7), (5, 4), (2, 9), (8, 3), (1, 6), (7, 10), (4, 11), (9, 5)])
def _(p):
    a, b = p
    return (rf"Quel nombre, multiplié par ${b}$, donne ${a}$ ?", m(rf_(a, b)), [m(rf_(b, a)), m(nb(a * b)), m(nb(a + b) if a - b == 0 else nb(abs(a - b)))])


@qtype("fra", "Avec le même dénominateur, on additionne les numérateurs et on garde le dénominateur.",
       [(2, 3, 7), (4, 3, 9), (1, 6, 10), (5, 2, 11), (3, 4, 8), (2, 9, 13), (7, 5, 15), (6, 1, 12)])
def _(p):
    a, c, b = p
    return (rf"Que vaut ${rf_(a, b)}+{rf_(c, b)}$ ?", m(rf_(a + c, b)), [m(rf_(a + c, 2 * b)), m(rf_(a * c, b)), m(rf_(a + c, b * b))])


@qtype("fra", "Compte les parts qui restent sur le nombre total de parts égales.",
       [(8, 3), (6, 1), (10, 7), (12, 5), (5, 2), (9, 4), (4, 3), (7, 2)])
def _(p):
    n, k = p
    pp = "la part" if k == 1 else f"${k}$ parts"
    return (rf"Un gâteau est coupé en ${n}$ parts égales. On mange {pp}. Quelle fraction du gâteau reste-t-il ?",
            m(rf_(n - k, n)), [m(rf_(k, n)), m(rf_(n - k, k)) if n - k != k else m(rf_(n, k)), m(rf_(k, n - k)) if n - k != k else m(rf_(n, n - k + 1))])


@qtype("fra", "Cherche combien de fois le dénominateur tient dans le numérateur.",
       [(17, 5), (23, 4), (9, 2), (13, 6), (50, 7), (25, 3), (11, 10), (62, 9)])
def _(p):
    a, b = p
    q = a // b
    e = lambda x, y: m(rf"{x}\text{{ et }}{y}")
    return (rf"Entre quels nombres entiers consécutifs se trouve ${rf_(a, b)}$ ?", e(q, q + 1), [e(q - 1, q), e(q + 1, q + 2), e(q + 2, q + 3)])


# ============================================================ GÉOMÉTRIE
@qtype("geo", "Aigu : moins de 90° ; droit : 90° ; obtus : entre 90° et 180° ; plat : 180°.",
       [135, 42, 90, 180, 89, 91, 160, 15])
def _(a):
    nat = "aigu" if a < 90 else "droit" if a == 90 else "obtus" if a < 180 else "plat"
    return (rf"Un angle mesure ${a}^\circ$. Quelle est sa nature ?", nat, [x for x in ["aigu", "droit", "obtus", "plat"] if x != nat])


@qtype("geo", "Un angle droit mesure 90° : les deux angles ensemble font 90°.",
       [35, 28, 72, 45, 61, 13, 50, 84])
def _(a):
    d = lambda x: m(rf"{x}^\circ")
    return (rf"L'angle droit $\widehat{{xOy}}$ est partagé par la demi-droite $[Oz)$ en deux angles. $\widehat{{xOz}}={a}^\circ$. Combien mesure $\widehat{{zOy}}$ ?",
            d(90 - a), [d(180 - a), d(a) if a != 45 else d(90), d(90 + a), d(100 - a)])


@qtype("geo", "Un angle plat mesure 180° : les deux angles ensemble font 180°.",
       [120, 65, 38, 145, 100, 77, 152, 49])
def _(a):
    d = lambda x: m(rf"{x}^\circ")
    return (rf"Les points $A$, $O$ et $B$ sont alignés dans cet ordre et $\widehat{{AOC}}={a}^\circ$. Combien mesure $\widehat{{COB}}$ ?",
            d(180 - a), [d(abs(90 - a)), d(a), d(360 - a)])


@qtype("geo", "Un axe de symétrie partage la figure en deux parties qui se superposent par pliage.",
       [("un carré", "4"), ("un rectangle qui n'est pas un carré", "2"), ("un triangle équilatéral", "3"), ("un losange qui n'est pas un carré", "2"),
        ("un triangle isocèle qui n'est pas équilatéral", "1"), ("un triangle quelconque", "0"), ("un hexagone régulier", "6"), ("un cercle", "une infinité")])
def _(p):
    f, n = p
    pool = [x for x in ["4", "2", "1", "3", "0", "une infinité", "6"] if x != n]
    return (rf"Combien d'axes de symétrie possède {f} ?", n, pool[:3])


@qtype("geo", "Le diamètre est le double du rayon ; le rayon est la moitié du diamètre.",
       [("diamètre", 9), ("rayon", 6), ("diamètre", 15), ("rayon", F(7, 2)), ("diamètre", 20), ("rayon", 8), ("diamètre", 7), ("rayon", F(25, 2))])
def _(p):
    w, v = p
    other, r = ("rayon", F(v) / 2) if w == "diamètre" else ("diamètre", F(v) * 2)
    alt = F(v) * 2 if w == "diamètre" else F(v) / 2
    return (rf"Un cercle a un {w} de ${nb(v)}$ cm. Quelle est la longueur de son {other} ?",
            u(nb(r), "cm"), [u(nb(alt), "cm"), u(nb(v), "cm"), u(nb(F(v) + 2), "cm")])


@qtype("geo", "Deux droites perpendiculaires à une même droite sont parallèles ; si deux droites sont parallèles, toute perpendiculaire à l'une est perpendiculaire à l'autre.",
       [("d_1", "d_2", "d", "perp", "perp"), ("a", "b", "c", "par", "perp"), ("u", "v", "w", "par", "par"), ("e", "f", "g", "perp", "par"),
        ("m", "n", "p", "perp", "perp"), ("x", "y", "z", "par", "par"), ("r", "s", "t", "par", "perp"), ("k", "\\ell", "h", "perp", "par")])
def _(p):
    a, b, c, r1, r2 = p
    W = {"perp": "perpendiculaire", "par": "parallèle"}
    ans = "parallèles" if r1 == r2 else "perpendiculaires"
    return (rf"La droite $({a})$ est {W[r1]} à $({c})$ et la droite $({b})$ est {W[r2]} à $({c})$. Que peut-on dire des droites $({a})$ et $({b})$ ?",
            ans, ["perpendiculaires" if ans == "parallèles" else "parallèles", "sécantes, non perpendiculaires", "on ne peut pas savoir"])


@qtype("geo", "Isocèle : deux côtés égaux ; équilatéral : trois côtés égaux ; rectangle : un angle droit.",
       [("des côtés de $5$ cm, $5$ cm et $7$ cm", "isocèle"), ("trois côtés de $6$ cm", "équilatéral"), ("un angle de $90^\\circ$", "rectangle"),
        ("des côtés de $4$ cm, $6$ cm et $7$ cm, et aucun angle droit", "quelconque"), ("deux côtés de $8$ cm et un troisième de $3$ cm", "isocèle"),
        ("un angle droit et deux côtés de l'angle droit de même longueur", "isocèle rectangle"), ("des côtés de $9$ cm, $9$ cm et $9$ cm", "équilatéral"),
        ("des côtés de $3$ cm, $5$ cm et $6$ cm, et aucun angle droit", "quelconque")])
def _(p):
    d, nat = p
    pool = [x for x in ["isocèle", "équilatéral", "rectangle", "quelconque", "isocèle rectangle"] if x != nat]
    return (rf"Un triangle a {d}. Quelle est sa nature ?", nat, pool)


@qtype("geo", "Carré : 4 angles droits et 4 côtés égaux ; rectangle : 4 angles droits ; losange : 4 côtés égaux.",
       [("quatre angles droits et quatre côtés de même longueur", "un carré"), ("quatre angles droits", "un rectangle"),
        ("quatre côtés de même longueur", "un losange"), ("quatre côtés de même longueur et un angle droit", "un carré"),
        ("des diagonales de même longueur qui se coupent en leur milieu", "un rectangle"),
        ("des diagonales perpendiculaires qui se coupent en leur milieu", "un losange"),
        ("des diagonales de même longueur, perpendiculaires, qui se coupent en leur milieu", "un carré"),
        ("ses côtés opposés de même longueur et quatre angles droits", "un rectangle")])
def _(p):
    d, nat = p
    pool = [x for x in ["un carré", "un rectangle", "un losange", "un triangle"] if x != nat]
    return (rf"Un quadrilatère a {d}. Quelle est sa nature la plus précise ?", nat, pool)


# ============================================================ GRANDEURS ET MESURES
@qtype("mes", "Périmètre d'un rectangle = 2 × (longueur + largeur).",
       [(8, 5), (12, 7), (F(13, 2), 4), (15, 9), (11, F(5, 2)), (7, 3), (20, 11), (F(19, 2), 6)])
def _(p):
    L, l = p
    return (rf"Un rectangle a une longueur de ${nb(L)}$ cm et une largeur de ${nb(l)}$ cm. Quel est son périmètre ?",
            u(nb(2 * (L + l)), "cm"), [u(nb(L * l), "cm"), u(nb(L + l), "cm"), u(nb(2 * L + l), "cm"), u(nb(L + 2 * l), "cm")])


@qtype("mes", "Aire d'un rectangle = longueur × largeur.",
       [(8, 5), (12, 7), (F(13, 2), 4), (15, 9), (11, F(5, 2)), (7, 3), (20, 11), (F(19, 2), 6)])
def _(p):
    L, l = p
    a2 = lambda x: m(rf"{nb(x)}~\text{{cm}}^2")
    return (rf"Un rectangle a une longueur de ${nb(L)}$ cm et une largeur de ${nb(l)}$ cm. Quelle est son aire ?",
            a2(L * l), [a2(2 * (L + l)), a2(L + l), a2(F(L * l, 2)), a2(2 * L * l)])


@qtype("mes", "Un triangle rectangle est la moitié d'un rectangle : aire = côté × côté ÷ 2 (côtés de l'angle droit).",
       [(6, 4), (10, 7), (8, 5), (12, 9), (5, 3), (14, 6), (9, 8), (7, 4)])
def _(p):
    a, b = p
    a2 = lambda x: m(rf"{nb(x)}~\text{{cm}}^2")
    return (rf"Un triangle est rectangle ; les deux côtés de l'angle droit mesurent ${a}$ cm et ${b}$ cm. Quelle est son aire ?",
            a2(F(a * b, 2)), [a2(a * b), a2(a + b), a2(2 * (a + b))])


ORD_L = ["km", "hm", "dam", "m", "dm", "cm", "mm"]
ORD_M = ["kg", "hg", "dag", "g", "dg", "cg", "mg"]


@qtype("mes", "km, hm, dam, m, dm, cm, mm : on multiplie par 10 à chaque rang vers la droite.",
       [(F(7, 2), "m", "cm"), (1250, "m", "km"), (42, "mm", "cm"), (F(4, 5), "km", "m"), (65, "cm", "m"), (7, "dm", "mm"), (F(23, 10), "m", "mm"), (5000, "mm", "m")])
def _(p):
    x, a, b = p
    r = F(x) * F(10) ** (ORD_L.index(b) - ORD_L.index(a))
    V = lambda v: u(nb(v), b)
    return (rf"Compléter : ${nb(x)}~\text{{{a}}}=\;?\;\text{{{b}}}$", V(r), [V(r * 10), V(r / 10), V(r * 100) if r * 100 != F(x) else V(r / 100)])


@qtype("mes", "kg, hg, dag, g, dg, cg, mg : on multiplie par 10 à chaque rang vers la droite (1 kg = 1 000 g).",
       [(F(5, 2), "kg", "g"), (750, "g", "kg"), (45, "g", "mg"), (3500, "g", "kg"), (F(3, 10), "kg", "g"), (8, "g", "cg"), (250, "mg", "g"), (F(81, 20), "kg", "g")])
def _(p):
    x, a, b = p
    r = F(x) * F(10) ** (ORD_M.index(b) - ORD_M.index(a))
    V = lambda v: u(nb(v), b)
    return (rf"Compléter : ${nb(x)}~\text{{{a}}}=\;?\;\text{{{b}}}$", V(r), [V(r * 10), V(r / 10), V(r * 100) if r * 100 != F(x) else V(r / 100)])


@qtype("mes", "1 h = 60 min : multiplie le nombre d'heures par 60, puis ajoute les minutes.",
       [(1, 45), (2, 30), (3, 15), (1, 5), (4, 20), (2, 50), (5, 0), (3, 40)])
def _(p):
    h, mi = p
    t = f"{h} h" + (f" {mi} min" if mi else "")
    return (rf"Combien de minutes y a-t-il dans {t} ?", u(60 * h + mi, "min"), [u(100 * h + mi, "min"), u(h + mi, "min"), u(60 * h - mi if mi else 60 * h + 30, "min")])


@qtype("mes", "Périmètre d'un cercle = π × diamètre ; avec π ≈ 3,14.",
       [10, 4, 20, 6, 8, 15, 30, F(5, 2)])
def _(d):
    P = F(d) * F(314, 100)
    return (rf"En prenant $\pi\approx3{{,}}14$, quel est le périmètre d'un cercle de diamètre ${nb(d)}$ cm ?",
            u(nb(P), "cm"), [u(nb(P / 2), "cm"), u(nb(P * 2), "cm"), u(nb(F(d) * d * F(314, 400)), "cm"), u(nb(F(d) * 3), "cm")])


@qtype("mes", "Volume d'un pavé droit = longueur × largeur × hauteur.",
       [(5, 4, 3), (10, 2, 6), (8, 5, 2), (7, 3, 4), (F(5, 2), 4, 10), (6, 6, 6), (12, 5, F(3, 2)), (9, 2, 3)])
def _(p):
    L, l, h = p
    v3 = lambda x: m(rf"{nb(x)}~\text{{cm}}^3")
    return (rf"Un pavé droit mesure ${nb(L)}$ cm de longueur, ${nb(l)}$ cm de largeur et ${nb(h)}$ cm de hauteur. Quel est son volume ?",
            v3(L * l * h), [v3(L + l + h), v3(L * l), v3(2 * (L * l + l * h + L * h)), v3(F(L * l * h, 2))])


# ============================================================ PROPORTIONNALITÉ ET DONNÉES
@qtype("pro", "Calcule d'abord pour une personne, puis multiplie (ou utilise un multiple).",
       [(4, 300, 6), (5, 250, 2), (3, 180, 9), (8, 400, 6), (2, 150, 7), (6, 90, 4), (10, 750, 4), (4, 120, 10)])
def _(p):
    a, g, b = p
    r = F(g * b, a)
    gr = lambda x: u(nb(x), "g")
    return (rf"Pour ${a}$ personnes, il faut ${g}$ g de farine. Combien en faut-il pour ${b}$ personnes ?",
            gr(r), [gr(g + b - a), gr(g * b), gr(F(g, a))])


@qtype("pro", "Prix d'un objet = prix total ÷ nombre d'objets.",
       [(5, 1250), (4, 1100), (3, 450), (6, 840), (8, 1600), (12, 900), (7, 2450), (9, 1080)])
def _(p):
    n, P = p
    f = lambda x: u(nb(x), "F")
    return (rf"${n}$ cahiers coûtent ${nb(P)}$ F. Combien coûte un cahier ?", f(F(P, n)), [f(P - n), f(F(P, n) * 2), f(F(P, n) + n)])


@qtype("pro", "50 %, c'est la moitié ; 25 %, le quart ; 10 %, diviser par 10 ; 75 %, les trois quarts.",
       [(50, 84), (25, 120), (10, 350), (20, 45), (75, 40), (50, 1300), (25, 48), (10, 72)])
def _(p):
    pc, N = p
    r = F(pc * N, 100)
    return (rf"Que vaut ${pc}\,\%$ de ${nb(N)}$ ?", m(nb(r)), [m(nb(N - r)), m(nb(F(N, pc)) if F(N, pc).denominator in (1, 2, 4, 5) else nb(r * 2)), m(nb(r + 10)), m(nb(r / 10)), m(nb(pc))])


@qtype("pro", "À l'échelle 1/100, 1 cm sur le plan représente 100 cm, c'est-à-dire 1 m en réalité.",
       [(100, 5), (1000, 3), (200, 4), (50, 8), (10000, 2), (250, 4), (2000, 7), (100, F(25, 2))])
def _(p):
    s, c = p
    real = F(c) * s / 100
    mm = lambda x: u(nb(x), "m")
    return (rf"Sur un plan à l'échelle $\dfrac{{1}}{{{nb(s)}}}$, une longueur mesure ${nb(c)}$ cm. Quelle est la longueur réelle ?",
            mm(real), [mm(F(c) * s), mm(real / 10), mm(real * 10)])


@qtype("pro", "Le coefficient de proportionnalité s'obtient en divisant un nombre de la 2e ligne par le nombre au-dessus.",
       [(3, (2, 3, 5)), (4, (1, 5, 7)), (6, (2, 4, 9)), (F(5, 2), (2, 4, 6)), (7, (3, 5, 10)), (F(3, 2), (2, 6, 8)), (9, (1, 2, 4)), (12, (2, 3, 5))])
def _(p):
    k, xs = p
    T = r"\begin{array}{|c|c|c|}\hline " + " & ".join(map(str, xs)) + r"\\\hline " + " & ".join(nb(k * x) for x in xs) + r"\\\hline\end{array}"
    return (rf"Ce tableau est un tableau de proportionnalité : ${T}$. Par quel nombre multiplie-t-on la 1re ligne pour obtenir la 2e ?",
            m(nb(k)), [m(nb(k + 1)), m(lf(1 / F(k))), m(nb(k * xs[0]))])


@qtype("pro", "L'effectif total est la somme de tous les effectifs.",
       [(8, 12, 5), (14, 9, 6), (7, 7, 11, 3), (20, 15, 8), (5, 9, 4, 6), (13, 2, 10), (11, 16, 6, 2), (9, 18, 7)])
def _(v):
    modes = ["à pied", "en bus", "à vélo", "en voiture"]
    txt = ", ".join(f"${c}$ {mo}" for c, mo in zip(v[:-1], modes)) + f" et ${v[-1]}$ {modes[len(v) - 1]}"
    return (rf"Dans une classe, les élèves viennent au collège ainsi : {txt}. Combien y a-t-il d'élèves dans la classe ?",
            m(nb(sum(v))), [m(nb(sum(v) + 1)), m(nb(max(v))), m(nb(sum(v) - min(v))), m(nb(sum(v) - 1))])


@qtype("pro", "Vérifie si l'on passe de la 1re ligne à la 2e en multipliant toujours par le même nombre.",
       [(2, 5, 6, 15), (3, 4, 9, 16), (4, 10, 10, 25), (5, 7, 15, 20), (6, 9, 8, 12), (2, 8, 5, 18), (10, 15, 4, 6), (3, 9, 7, 20)])
def _(p):
    x1, x2, y1, y2 = p
    ok = x1 * y2 == x2 * y1
    T = rf"\begin{{array}}{{|c|c|}}\hline {x1} & {x2}\\\hline {y1} & {y2}\\\hline\end{{array}}"
    return (rf"Ce tableau est-il un tableau de proportionnalité ? ${T}$", "oui" if ok else "non",
            ["non" if ok else "oui", "on ne peut pas savoir", "il manque une colonne"])


@qtype("pro", "Calcule d'abord le volume rempli en 1 minute, puis multiplie.",
       [(12, 3, 5), (25, 5, 8), (18, 6, 10), (9, 2, 7), (40, 8, 3), (14, 4, 6), (30, 10, 4), (7, 2, 10)])
def _(p):
    V, t, s = p
    r = F(V * s, t)
    L = lambda x: u(nb(x), "L")
    return (rf"Un robinet remplit ${V}$ L en ${t}$ min. Quel volume remplit-il en ${s}$ min, au même débit ?",
            L(r), [L(V + s - t), L(V * s), L(F(V, t))])


# ============================================================ BUILD
THEMES = {"num": ("Nombres entiers et décimaux", "1F6FA8"), "cal": ("Calculs", "6A4C93"),
          "fra": ("Fractions", "2E7D6B"), "geo": ("Géométrie", "C0503A"),
          "mes": ("Grandeurs et mesures", "8A5A2B"), "pro": ("Proportionnalité et données", "C77F0A")}
ORDER = list(THEMES)
PER = 8
Q, HINT = {}, {}
FALLBACK = []
for th in ORDER:
    assert len([t for t in TYPES if t[0] == th]) == PER, th
for ti, th in enumerate(ORDER):
    types = [t for t in TYPES if t[0] == th]
    for k, (_, fn, params, hint) in enumerate(types):
        for j in range(2):
            nA = ti * 2 * PER + k * 2 + j + 1
            for si, L_ in enumerate("ABCD"):
                n = nA + si * HALF
                st, ans, dis = fn(params[2 * si + j])
                opts = [ans]
                for d in dis:
                    if d not in opts:
                        opts.append(d)
                    if len(opts) == 4:
                        break
                if len(opts) < 4:
                    mm = re.fullmatch(r"\$(-?\d+)\$", ans)
                    if mm:
                        for dlt in (1, -1, 2, -2, 3):
                            c = m(str(int(mm.group(1)) + dlt))
                            if c not in opts:
                                opts.append(c); FALLBACK.append(n)
                            if len(opts) == 4:
                                break
                assert len(opts) == 4, (n, ans, dis)
                Q[n] = (th, L_, st, opts)
                HINT[n] = TYPES.index((th, fn, params, hint))
for n in range(1, HALF + 1):
    assert len({(Q[n + si * HALF][2], tuple(sorted(Q[n + si * HALF][3]))) for si in range(4)}) == 4, n

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
    th, serie, st, opts = Q[n]
    st = st.replace(" ?", "~?").replace(" :", "~:").replace("« ", "«~").replace(" »", "~»").replace("%", r"\%").replace(r"\\%", r"\%")
    st = st.replace(r"\,\%", r"\,\%")
    rng = random.Random(n * 17 + 4)
    perm = [0, 1, 2, 3]
    rng.shuffle(perm)
    shown = [opts[i] for i in perm]
    good = "abcd"[perm.index(0)]
    KEY.append([n, th, good, opts[0], HINT[n]])
    lab = THEMES[th][0]
    num = n if n <= HALF else f"{(n - 1) % HALF + 1} {'ABCD'[(n - 1) // HALF]}"
    shown = [o.replace("%", r"\%").replace(r"\\%", r"\%") for o in shown]
    ob = lambda i: (rf"\begin{{tcolorbox}}[enhanced,nobeforeafter,width=7.1cm,height=2.1cm,valign=center,colback=c{th}!6,colframe=c{th},arc=2.5mm,boxrule=0.9pt,left=3mm]"
                    rf"{{\Large\bfseries\color{{c{th}}}{'abcd'[i]})}}\quad\begin{{minipage}}[c]{{5.6cm}}\raggedright{'\\Large' if len(shown[i]) < 26 else '\\large'} {shown[i]}\end{{minipage}}\end{{tcolorbox}}")
    tex.append(rf"""\begin{{tcolorbox}}[enhanced,width=16cm,height=14cm,colback=white,colframe=c{th},boxrule=2pt,arc=0mm,
left=6mm,right=6mm,top=0mm,bottom=4mm,sharp corners,
overlay={{\fill[c{th}] (frame.north west) rectangle ([yshift=-1.25cm]frame.north east);
\node[anchor=west,text=white,font=\sffamily\bfseries\LARGE] at ([xshift=5mm,yshift=-0.62cm]frame.north west) {{Question {num}}};
\node[anchor=east,text=white,font=\sffamily\itshape\large] at ([xshift=-5mm,yshift=-0.62cm]frame.north east) {{{lab}}};}}]
\vspace*{{1.75cm}}
\begin{{minipage}}[t][6.9cm][c]{{\linewidth}}{'\\LARGE' if len(st) < 150 else '\\Large'}\centering
\begin{{minipage}}{{0.95\linewidth}}\raggedright\linespread{{1.25}}\selectfont {st}\end{{minipage}}
\end{{minipage}}

\vfill
{ob(0)}\hfill{ob(1)}\par\vspace{{2.5mm}}
{ob(2)}\hfill{ob(3)}
\end{{tcolorbox}}
\newpage""")
tex.append(r"\end{document}")
open(f"{OUT}/sixieme.tex", "w", encoding="utf-8").write("\n".join(tex))
json.dump([[n, th, g, h] for n, th, g, _, h in KEY], open(f"{OUT}/questions.json", "w"))
json.dump([t[3] for t in TYPES], open(f"{OUT}/hints.json", "w"), ensure_ascii=False, indent=0)
with open(f"{OUT}/corrige.txt", "w", encoding="utf-8") as f:
    for n, th, g, a, h in KEY:
        f.write(f"Q{n if n <= HALF else str((n - 1) % HALF + 1) + ' ' + 'ABCD'[(n - 1) // HALF]} ({THEMES[th][0]}) : {g}) {a}\n")
print(len(KEY), "questions ; fallback:", FALLBACK)
