"""Banque Mathématiques 4ème (programme du cycle 4, repères de 4e) :
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


# ============================================================ RELATIFS ET FRACTIONS
@qtype("rel", "Compte les facteurs négatifs : un nombre pair de signes « − » donne un produit positif.",
       [(-2, 3, -4), (5, -2, 3), (-1, -6, -2), (4, -3, -2), (-5, -2, -3), (3, -4, 5), (-7, 2, -1), (2, -5, -3)])
def _(p):
    a, b, c = p
    r = a * b * c
    return (rf"Que vaut ${sgn(a)}\times{sgn(b)}\times{sgn(c)}$ ?",
            m(nb(r)), [m(nb(-r)), m(nb(a + b + c)), m(nb(a * b - c)), m(nb(abs(r) + 1))])


@qtype("rel", "Le quotient de deux nombres de même signe est positif, de signes contraires il est négatif.",
       [(-36, 4), (42, -6), (-56, -8), (45, -9), (-63, 7), (-48, -6), (72, -8), (-35, 5)])
def _(p):
    a, b = p
    q = a // b
    assert q * b == a
    return (rf"Que vaut ${sgn(a)}\div{sgn(b)}$ ?", m(nb(q)), [m(nb(-q)), m(nb(q + 1)), m(nb(2 * q)), m(nb(q - 1))])


@qtype("rel", "La multiplication passe avant la soustraction : calcule d'abord le produit.",
       [(5, 3, -2), (7, 4, -3), (-2, 5, -4), (10, 2, -6), (-3, 6, -2), (-6, 4, -5), (9, 2, -7), (1, 8, -3)])
def _(p):
    a, b, c = p
    return (rf"Que vaut ${nb(a)}-{b}\times({nb(c)})$ ?",
            m(nb(a - b * c)), [m(nb((a - b) * c)), m(nb(a + b * c)), m(nb(-(a - b * c))), m(nb(a - b - c))])


@qtype("rel", "Mets les deux fractions au même dénominateur avant d'additionner les numérateurs.",
       [(1, 3, 1, 4), (2, 5, 1, 2), (3, 4, 1, 6), (1, 6, 2, 9), (5, 8, 1, 6), (2, 3, 3, 7), (3, 10, 2, 15), (1, 4, 5, 6)])
def _(p):
    a, b, c, d = p
    return (rf"Que vaut $\dfrac{{{a}}}{{{b}}}+\dfrac{{{c}}}{{{d}}}$ ?",
            m(lf(F(a, b) + F(c, d))), [m(lf(F(a + c, b + d))), m(lf(F(a * c, b * d))), m(lf(F(a + c, b * d))), m(lf(F(a + c, max(b, d))))])


def fr(x):
    """a fraction in a calculation, between parentheses when negative."""
    return rf"\left({lf(x)}\right)" if x < 0 else lf(x)


@qtype("rel", "Multiplie les numérateurs entre eux et les dénominateurs entre eux, puis simplifie.",
       [(2, 3, 9, 4), (-3, 5, 10, 9), (4, 7, -21, 8), (-5, 6, -3, 10), (7, 12, 8, 21), (-2, 9, 3, -4), (5, 4, -8, 15), (3, 8, -4, 9)])
def _(p):
    a, b, c, d = p
    x, y = F(a, b), F(c, d)
    return (rf"Que vaut ${fr(x)}\times{fr(y)}$ ?", m(lf(x * y)), [m(lf(x / y)), m(lf(-x * y)), m(lf(F(a + c, b + d) if b + d else 1)), m(lf(x * y * 2))])


@qtype("rel", "Diviser par une fraction, c'est multiplier par son inverse.",
       [(2, 3, 4, 5), (3, 4, 9, 8), (-5, 6, 10, 3), (7, 10, -21, 5), (4, 9, 2, 15), (-3, 7, -6, 14), (5, 8, 15, 4), (9, 10, 3, 5)])
def _(p):
    a, b, c, d = p
    x, y = F(a, b), F(c, d)
    return (rf"Que vaut ${fr(x)}\div{fr(y)}$ ?", m(lf(x / y)), [m(lf(x * y)), m(lf(y / x)), m(lf(-x / y)), m(lf(x / y + 1))])


@qtype("rel", "L'inverse de x est le nombre qui, multiplié par x, donne 1.",
       [F(3, 4), F(-2, 5), F(7), F(1, 6), F(-4), F(5, 3), F(-7, 2), F(2, 9)])
def _(x):
    return (rf"Quel est l'inverse de ${lf(x)}$ ?", m(lf(1 / x)), [m(lf(-x)), m(lf(-1 / x)), m(lf(x)), m(lf(1 / x + 1))])


@qtype("rel", "Mets les deux fractions au même dénominateur ; le résultat peut être négatif.",
       [(1, 4, 2, 3), (3, 5, 7, 10), (5, 6, 1, 4), (2, 7, 1, 2), (1, 3, 5, 6), (7, 8, 5, 6), (2, 9, 1, 3), (3, 4, 9, 10)])
def _(p):
    a, b, c, d = p
    r = F(a, b) - F(c, d)
    return (rf"Que vaut $\dfrac{{{a}}}{{{b}}}-\dfrac{{{c}}}{{{d}}}$ ?",
            m(lf(r)), [m(lf(-r)), m(lf(F(a - c, b * d))), m(lf(F(a - c, abs(b - d)))), m(lf(F(a + c, b * d)))])


# ============================================================ PUISSANCES ET RACINES CARRÉES
@qtype("pui", "aⁿ, c'est a multiplié par lui-même n fois ; attention au signe pour un nombre négatif.",
       [(2, 5), (3, 4), (-2, 3), (5, 3), (-3, 2), (2, 7), (10, 4), (4, 3)])
def _(p):
    a, n = p
    base = f"({a})" if a < 0 else str(a)
    return (rf"Que vaut ${base}^{{{n}}}$ ?", m(nb(a ** n)), [m(nb(a * n)), m(nb(a ** (n - 1))), m(nb(-(a ** n))), m(nb(n ** abs(a)))])


@qtype("pui", "10ᵃ × 10ᵇ = 10ᵃ⁺ᵇ : on additionne les exposants.",
       [(3, 4), (5, -2), (-3, -4), (6, 2), (-5, 8), (2, -7), (4, 4), (-1, 6)])
def _(p):
    a, b = p
    return (rf"Écrire $10^{{{a}}}\times10^{{{b}}}$ sous la forme d'une seule puissance de $10$.",
            m(f"10^{{{a + b}}}"), [m(f"10^{{{a * b}}}"), m(f"10^{{{a - b}}}"), m(f"100^{{{a + b}}}"), m(f"20^{{{a + b}}}")])


@qtype("pui", "10⁻ⁿ = 1 / 10ⁿ : c'est un nombre positif, avec le chiffre 1 au n-ième rang après la virgule.",
       [2, 3, 1, 4, 5, 6, 7, 8])
def _(n):
    return (rf"Quelle est l'écriture décimale de $10^{{-{n}}}$ ?",
            m(nb(F(1, 10 ** n))), [m(nb(-(10 ** n))), m(nb(F(1, 10 ** (n + 1)))), m(nb(F(1, 10 ** (n - 1))) if n > 1 else "10"), m(nb(-10 * n))])


@qtype("pui", "En notation scientifique, le premier facteur est compris entre 1 et 10 (10 exclu).",
       [("3\\,400\\,000", "3{,}4", "34", 6), ("0{,}00052", "5{,}2", "52", -4), ("72\\,000", "7{,}2", "72", 4),
        ("0{,}08", "8", "80", -2), ("605\\,000\\,000", "6{,}05", "60{,}5", 8), ("0{,}0031", "3{,}1", "31", -3),
        ("41\\,000", "4{,}1", "41", 4), ("0{,}000907", "9{,}07", "90{,}7", -4)])
def _(p):
    s, mm, m10, e = p
    t = lambda a, k: m(rf"{a}\times10^{{{k}}}")
    return (rf"Quelle est la notation scientifique de ${s}$ ?", t(mm, e), [t(mm, e + 1), t(m10, e), t(mm, -e), t(mm, e - 1)])


@qtype("pui", "Dans −aⁿ, la puissance passe avant le signe « − » : −aⁿ = −(aⁿ).",
       [(3, 2), (2, 4), (5, 2), (6, 2), (3, 4), (10, 2), (7, 2), (2, 6)])
def _(p):
    a, n = p
    return (rf"Que vaut $-{a}^{{{n}}}$ ?", m(nb(-(a ** n))), [m(nb(a ** n)), m(nb(-a * n)), m(nb(a * n)), m(nb(-(a ** n) + 1))])


@qtype("pui", "10ᵃ ÷ 10ᵇ = 10ᵃ⁻ᵇ : on soustrait les exposants.",
       [(7, 3), (5, 8), (-2, 4), (6, -3), (9, 2), (3, -5), (-4, -6), (8, 5)])
def _(p):
    a, b = p
    return (rf"Écrire $\dfrac{{10^{{{a}}}}}{{10^{{{b}}}}}$ sous la forme d'une seule puissance de $10$.",
            m(f"10^{{{a - b}}}"), [m(f"10^{{{a + b}}}"), m(f"10^{{{b - a}}}"), m(f"10^{{{a * b}}}"), m(f"1^{{{a - b}}}")])


@qtype("pui", "√a est le nombre positif dont le carré vaut a.",
       [49, 144, 81, 121, 169, 225, 400, 64])
def _(N):
    r = isqrt(N)
    return (rf"Que vaut $\sqrt{{{N}}}$ ?", m(nb(r)), [m(nb(N // 2)), m(nb(2 * r)), m(nb(r + 1)), m(nb(N))])


@qtype("pui", "Cherche les deux carrés parfaits consécutifs qui encadrent le nombre sous la racine.",
       [20, 50, 70, 90, 30, 110, 150, 200])
def _(N):
    r = isqrt(N)
    e = lambda a, b: m(rf"{a}\text{{ et }}{b}")
    return (rf"Entre quels nombres entiers consécutifs se trouve $\sqrt{{{N}}}$ ?",
            e(r, r + 1), [e(r - 1, r), e(r + 1, r + 2), e(N // 2, N // 2 + 1)])


# ============================================================ CALCUL LITTÉRAL ET ÉQUATIONS
@qtype("lit", "k(a + b) = k × a + k × b : multiplie chaque terme de la parenthèse par k.",
       [(3, 2, 5), (-2, 4, -3), (5, 1, -4), (-3, -2, 7), (4, 3, -1), (-5, 2, 3), (6, -1, 2), (7, 2, -3)])
def _(p):
    k, a, b = p
    E = lambda c1, c0: expr([(c1, "x"), (c0, "")])
    return (rf"Développer ${k}({E(a, b)})$." if k > 0 else rf"Développer $-{-k}({E(a, b)})$.",
            m(E(k * a, k * b)), [m(E(k * a, b)), m(E(a, k * b)), m(E(k * a, -k * b)), m(E(k + a, k * b))])


@qtype("lit", "(x + a)(x + b) : chaque terme de la 1re parenthèse multiplie chaque terme de la 2e.",
       [(2, 3), (4, -1), (-3, 5), (-2, -6), (1, 7), (5, -4), (-1, -8), (3, 6)])
def _(p):
    a, b = p
    E = lambda *c: expr([(c[0], "x^2"), (c[1], "x"), (c[2], "")])
    P = lambda v: expr([(1, "x"), (v, "")])
    return (rf"Développer et réduire $({P(a)})({P(b)})$.",
            m(E(1, a + b, a * b)), [m(E(1, 0, a * b)), m(E(1, a * b, a + b)), m(E(1, a + b, a + b)), m(E(2, a + b, a * b))])


@qtype("lit", "Regroupe les termes en x d'un côté et les nombres de l'autre.",
       [(5, 3, -2, 7), (4, -6, 3, 2), (-2, 5, 6, -9), (7, 1, -7, 4), (3, -8, -5, 1), (-4, 2, 9, -6), (6, 7, -1, -3), (2, -4, 2, 9)])
def _(p):
    a, b, c, d = p
    E = lambda c1, c0: expr([(c1, "x"), (c0, "")])
    return (rf"Réduire l'expression ${expr([(a, 'x'), (b, ''), (c, 'x'), (d, '')])}$.",
            m(E(a + c, b + d)), [m(E(a + b + c + d, 0)), m(E(a - c, b + d)), m(E(a + c, b - d)), m(E(a + c + 1, b + d))])


@qtype("lit", "Cherche le plus grand facteur commun aux deux termes, puis mets-le devant la parenthèse.",
       [(3, 2, 5), (4, 3, -1), (5, 1, 4), (7, 2, -3), (6, 1, -2), (2, 5, 3), (9, 1, 2), (8, 3, 5)])
def _(p):
    k, a, b = p
    E = lambda c1, c0: expr([(c1, "x"), (c0, "")])
    return (rf"Factoriser ${E(k * a, k * b)}$.",
            m(f"{k}({E(a, b)})"), [m(f"{k}({E(a, k * b)})"), m(f"{k}({E(k * a, b)})"), m(f"{k * a}({E(1, b)})"), m(f"{k}x({E(a, b)})")])


@qtype("lit", "Remplace x par sa valeur entre parenthèses, puis respecte les priorités : la puissance d'abord.",
       [(3, -2, 1, -2), (2, 5, -3, -1), (1, -4, 6, 3), (-1, 3, 2, 2), (4, 1, -5, -3), (2, -3, 0, -4), (-2, -1, 7, 3), (1, 6, -2, -5)])
def _(p):
    a, b, c, x = p
    v = a * x * x + b * x + c
    return (rf"Que vaut ${expr([(a, 'x^2'), (b, 'x'), (c, '')])}$ pour $x={nb(x)}$ ?",
            m(nb(v)), [m(nb(-a * x * x + b * x + c)), m(nb(a * 2 * x + b * x + c)), m(nb(-v)), m(nb(v + 1))])


@qtype("lit", "Isole x : enlève d'abord le nombre ajouté, puis divise par le coefficient de x.",
       [(3, 5, 20), (4, -7, 21), (2, 9, -3), (5, -3, 27), (6, 4, -20), (7, 2, 30), (-3, 8, -7), (8, 3, 9)])
def _(p):
    a, b, c = p
    X = lambda v: m("x=" + lf(v))
    return (rf"Quelle est la solution de l'équation ${expr([(a, 'x'), (b, '')])}={nb(c)}$ ?",
            X(F(c - b, a)), [X(F(c + b, a)), X(F(c - b) - a), X(F(a, c - b) if c != b else 1), X(F(c, a) - b)])


@qtype("lit", "Regroupe les x dans un membre et les nombres dans l'autre, puis divise.",
       [(5, 3, 2, 12), (7, -4, 3, 8), (2, 9, 5, -3), (6, 1, -2, 17), (4, -5, 9, 10), (3, 8, -1, -4), (8, 2, 3, -13), (-2, 7, 4, -5)])
def _(p):
    a, b, c, d = p
    X = lambda v: m("x=" + lf(v))
    E = lambda c1, c0: expr([(c1, "x"), (c0, "")])
    return (rf"Quelle est la solution de l'équation ${E(a, b)}={E(c, d)}$ ?",
            X(F(d - b, a - c)), [X(F(d + b, a - c)), X(F(d - b, a + c)), X(F(b - d, a - c)), X(F(d - b, a - c) + 1)])


@qtype("lit", "Appelle x le nombre cherché, écris l'équation, puis résous-la.",
       [(3, 5, 26), (2, -7, 15), (4, 3, 27), (3, -8, 16), (2, 9, 35), (4, -6, 30), (3, 11, 2), (2, -5, -13)])
def _(p):
    k, b, r = p
    W = {2: "Le double", 3: "Le triple", 4: "Le quadruple"}[k]
    op = f"augmenté de {b}" if b > 0 else f"diminué de {-b}"
    x = F(r - b, k)
    assert x.denominator == 1
    return (rf"{W} d'un nombre, {op}, est égal à ${nb(r)}$. Quel est ce nombre ?",
            m(nb(x)), [m(nb(r - b)), m(lf(F(r + b, k))), m(lf(F(r, k))), m(nb(x + 1))])


# ============================================================ GÉOMÉTRIE
@qtype("geo", "Pythagore : le carré de l'hypoténuse est égal à la somme des carrés des deux autres côtés.",
       [(3, 4), (6, 8), (5, 12), (9, 12), (8, 15), (7, 24), (12, 16), (2, 3)])
def _(p):
    a, b = p
    return (rf"Le triangle $ABC$ est rectangle en $A$, avec $AB={a}$ cm et $AC={b}$ cm. Combien mesure $BC$ ?",
            u(rt(a * a + b * b), "cm"), [u(a + b, "cm"), u(rt(abs(b * b - a * a)), "cm"), u(nb(a * a + b * b), "cm"), u(rt(a * a + b * b + 1), "cm")])


@qtype("geo", "Pythagore : un côté de l'angle droit au carré = hypoténuse au carré − l'autre côté au carré.",
       [(10, 6), (13, 5), (25, 7), (17, 8), (20, 12), (29, 21), (5, 3), (6, 4)])
def _(p):
    c, a = p
    return (rf"Le triangle $ABC$ est rectangle en $A$, avec $BC={c}$ cm et $AB={a}$ cm. Combien mesure $AC$ ?",
            u(rt(c * c - a * a), "cm"), [u(c - a, "cm"), u(rt(c * c + a * a), "cm"), u(nb(c * c - a * a), "cm"), u(rt(c * c - a * a + 2), "cm")])


@qtype("geo", "Réciproque de Pythagore : compare le carré du plus grand côté à la somme des carrés des deux autres.",
       [(6, 8, 10), (5, 7, 9), (9, 40, 41), (4, 6, 7), (12, 35, 37), (8, 9, 12), (20, 21, 29), (7, 10, 12)])
def _(p):
    a, b, c = p
    ok = a * a + b * b == c * c
    return (rf"Un triangle a des côtés de ${a}$ cm, ${b}$ cm et ${c}$ cm. Est-il rectangle ?",
            "oui" if ok else "non", ["non" if ok else "oui", "on ne peut pas savoir", "s'il est isocèle"])


@qtype("geo", "Thalès : AM / AB = AN / AC = MN / BC quand (MN) et (BC) sont parallèles.",
       [(3, 6, 4), (2, 5, 3), (4, 10, 6), (5, 8, 10), (6, 9, 4), (3, 12, 5), (7, 14, 9), (4, 6, 8)])
def _(p):
    am, ab, an = p
    ac = F(an * ab, am)
    return (rf"Dans le triangle $ABC$, $M$ est sur $[AB]$, $N$ est sur $[AC]$ et les droites $(MN)$ et $(BC)$ sont parallèles. "
            rf"$AM={am}$ cm, $AB={ab}$ cm et $AN={an}$ cm. Combien mesure $AC$ ?",
            u(nb(ac), "cm"), [u(nb(F(an * am, ab)), "cm"), u(nb(an + ab - am), "cm"), u(nb(F(am * ab, an)), "cm"), u(nb(ac + 1), "cm")])


@qtype("geo", "Dans un triangle rectangle, cos(angle) = côté adjacent ÷ hypoténuse.",
       [(5, 3), (10, 8), (13, 5), (17, 15), (25, 7), (4, 2), (8, 6), (9, 4)])
def _(p):
    h, a = p
    return (rf"Le triangle $ABC$ est rectangle en $A$, avec $BC={h}$ cm et $AB={a}$ cm. Que vaut $\cos\widehat{{ABC}}$ ?",
            m(lf(F(a, h))), [m(lf(F(h, a))), m(lf(F(h - a, h))), m(lf(F(a, h - a)) if h - a != a else lf(F(a, h + a))), m(lf(F(a, h) + F(1, 10)))])


@qtype("geo", "Côté adjacent = hypoténuse × cos(angle).",
       [(10, F(6, 10)), (8, F(5, 10)), (20, F(35, 100)), (12, F(25, 100)), (15, F(8, 10)), (5, F(9, 10)), (40, F(45, 100)), (16, F(625, 1000))])
def _(p):
    h, c = p
    c_ = nb(c)
    return (rf"Le triangle $ABC$ est rectangle en $A$, avec $BC={h}$ cm et $\cos\widehat{{ABC}}={c_}$. Combien mesure $AB$ ?",
            u(nb(h * c), "cm"), [u(nb(h * (1 - c)), "cm"), u(nb(h * c / 2), "cm"), u(nb(h * c + 1), "cm"), u(nb(h * c * 2), "cm")])


@qtype("geo", "La translation qui transforme A en B déplace chaque point du même déplacement que de A à B.",
       [((1, 2), (4, 3), (0, -1)), ((-2, 1), (1, 5), (3, -2)), ((0, 0), (2, -3), (-1, 4)), ((3, -1), (1, 2), (5, 0)),
        ((-1, -2), (2, -1), (-3, 2)), ((2, 4), (-1, 1), (0, -2)), ((1, -3), (5, -1), (-2, -4)), ((-3, 2), (-1, -2), (4, 1))])
def _(p):
    A, B, C = p
    dx, dy = B[0] - A[0], B[1] - A[1]
    return (rf"Dans un repère, $A{pt(A)}$, $B{pt(B)}$ et $C{pt(C)}$. Quelles sont les coordonnées de l'image de $C$ par la translation qui transforme $A$ en $B$ ?",
            m(pt((C[0] + dx, C[1] + dy))), [m(pt((C[0] - dx, C[1] - dy))), m(pt((C[0] + dy, C[1] + dx))), m(pt((B[0] + C[0], B[1] + C[1]))), m(pt((C[0] + dx, C[1] - dy)))])


@qtype("geo", "Quand les longueurs sont multipliées par k, les aires sont multipliées par k².",
       [F(2), F(3), F(5), F(4), F(3, 2), F(10), F(1, 2), F(5, 2)])
def _(k):
    verb = "agrandie" if k > 1 else "réduite"
    return (rf"Une figure est {verb} à l'échelle ${nb(k)}$ (les longueurs sont multipliées par ${nb(k)}$). Par combien son aire est-elle multipliée ?",
            m(nb(k * k)), [m(nb(k)), m(nb(2 * k)), m(nb(k ** 3)), m(nb(k * k + 1))])


# ============================================================ PROPORTIONNALITÉ, STATISTIQUES, PROBABILITÉS
@qtype("don", "Dans un tableau de proportionnalité, on passe d'une ligne à l'autre en multipliant par le même nombre (ou produit en croix).",
       [(4, 10, 6), (3, 7, 12), (5, 8, 15), (6, 9, 14), (8, 6, 12), (2, 13, 5), (12, 30, 8), (7, 21, 4)])
def _(p):
    a, b, c = p
    T = rf"\begin{{array}}{{|c|c|}}\hline {a} & {c}\\\hline {b} & ?\\\hline\end{{array}}"
    return (rf"Ce tableau est un tableau de proportionnalité : ${T}$. Quel nombre remplace « ? » ?",
            m(nb(F(b * c, a))), [m(nb(b + c - a)), m(lf(F(a * c, b))), m(nb(b * c)), m(nb(F(b * c, a) + 1))])


@qtype("don", "Prendre p % d'un nombre, c'est le multiplier par p puis diviser par 100.",
       [(15, 80), (30, 250), (12, 50), (45, 200), (8, 350), (75, 64), (5, 460), (60, 35)])
def _(p):
    pc, N = p
    r = F(pc * N, 100)
    return (rf"Que vaut ${pc}\,\%$ de ${N}$ ?", m(nb(r)), [m(nb(N - r)), m(nb(F(pc * N, 10))), m(nb(r + pc)), m(nb(F(N, pc) if F(N, pc).denominator in (1, 2, 4, 5, 10) else r * 2))])


@qtype("don", "Pourcentage = partie ÷ total × 100.",
       [(25, 10), (20, 7), (50, 18), (40, 30), (30, 21), (80, 20), (200, 46), (16, 14)])
def _(p):
    N, k = p
    r = F(100 * k, N)
    pc = lambda v: m(rf"{nb(v)}\,\%")
    return (rf"Dans une classe de ${N}$ élèves, ${k}$ sont demi-pensionnaires. Quel pourcentage des élèves cela représente-t-il ?" if N <= 50 else
            rf"Sur ${N}$ élèves du collège, ${k}$ viennent en bus. Quel pourcentage des élèves cela représente-t-il ?",
            pc(r), [pc(k), pc(100 - r), pc(F(k, N) * 10), pc(r + 5)])


@qtype("don", "Moyenne = somme des valeurs ÷ nombre de valeurs.",
       [(12, 15, 9, 14), (8, 11, 17), (5, 9, 14, 16), (13, 7, 10, 18, 17), (20, 14, 11), (6, 15, 9, 12, 8), (3, 7, 11, 15), (16, 19, 10, 13)])
def _(v):
    mean = F(sum(v), len(v))
    return (rf"Quelle est la moyenne de la série ${'\\ ;\\ '.join(map(str, v))}$ ?",
            m(nb(mean)), [m(nb(sum(v))), m(nb(mean + 1)), m(nb(F(max(v) + min(v), 2)) if F(max(v) + min(v), 2) != mean else nb(mean - 1)), m(nb(max(v)))])


def median(v):
    s = sorted(v); n = len(s)
    return F(s[n // 2]) if n % 2 else F(s[n // 2 - 1] + s[n // 2], 2)


@qtype("don", "Range d'abord les valeurs dans l'ordre croissant : la médiane partage la série en deux groupes de même effectif.",
       [(4, 9, 2, 7, 5), (12, 3, 8, 15, 10, 6), (7, 1, 9, 3, 11), (14, 8, 10, 6), (5, 13, 2, 8, 17, 4, 11), (20, 15, 18, 12), (3, 3, 6, 10, 1), (9, 5, 16, 11, 14, 2)])
def _(v):
    md = median(v)
    mid = F(v[len(v) // 2]) if len(v) % 2 else F(v[len(v) // 2 - 1] + v[len(v) // 2], 2)
    return (rf"Quelle est la médiane de la série ${'\\ ;\\ '.join(map(str, v))}$ ?",
            m(nb(md)), [m(nb(mid)), m(nb(F(sum(v), len(v)))), m(nb(F(len(v) + 1, 2))), m(nb(md + 1))])


@qtype("don", "Étendue = plus grande valeur − plus petite valeur.",
       [(12, 5, 18, 9), (7, 15, 3, 11, 6), (20, 14, 25, 8), (4, 10, 2, 9, 13), (16, 26, 11, 19), (3, 8, 1, 15, 6), (30, 18, 27, 21), (9, 17, 6, 22, 10)])
def _(v):
    e = max(v) - min(v)
    return (rf"Quelle est l'étendue de la série ${'\\ ;\\ '.join(map(str, v))}$ ?",
            m(nb(e)), [m(nb(max(v))), m(nb(max(v) + min(v))), m(nb(F(sum(v), len(v)))), m(nb(e + 1))])


@qtype("don", "Probabilité = nombre de cas favorables ÷ nombre total de cas (tous également probables).",
       [(3, 5, 2, 1), (4, 1, 5, 0), (6, 3, 3, 2), (2, 7, 1, 1), (5, 5, 10, 2), (8, 2, 6, 0), (1, 4, 7, 2), (9, 3, 4, 1)])
def _(p):
    r, b, v, j = p
    N, k = r + b + v, (r, b, v)[j]
    col = ("rouge", "bleue", "verte")[j]
    bo = lambda c, w: f"${c}$ boule{'s' if c > 1 else ''} {w}{'s' if c > 1 else ''}"
    return (rf"Un sac contient {bo(r, 'rouge')}, {bo(b, 'bleue')} et {bo(v, 'verte')}. On tire une boule au hasard. Quelle est la probabilité de tirer une boule {col} ?",
            m(lf(F(k, N))), [m(lf(F(k, N - k))), m(lf(F(N - k, N))), m(lf(F(1, 3))), m(lf(F(1, k)) if k > 1 else lf(F(k, N + 1))), m(lf(F(k, N + 1))), m(lf(min(F(1), F(2 * k, N))))])


@qtype("don", "La probabilité de l'événement contraire de A vaut 1 − P(A).",
       [(F(3, 10), True), (F(65, 100), True), (F(2, 7), False), (F(8, 100), True), (F(5, 12), False), (F(42, 100), True), (F(1, 9), False), (F(875, 1000), True)])
def _(p):
    q, d = p
    show = (lambda x: nb(x)) if d else (lambda x: lf(x))
    return (rf"La probabilité qu'un événement $A$ se réalise est ${show(q)}$. Quelle est la probabilité de l'événement contraire de $A$ ?",
            m(show(1 - q)), [m(show(q)), m(show(abs(F(1, 2) - q)) if q != F(1, 4) else show(F(3, 4) - q)), m(show(1 - q / 2)), m(show((1 - q) / 2))])


# ============================================================ GRANDEURS ET MESURES
@qtype("gra", "Vitesse moyenne = distance ÷ durée (convertis la durée en heures).",
       [(150, F(2)), (240, F(3)), (90, F(3, 2)), (45, F(1, 2)), (210, F(5, 2)), (12, F(1, 4)), (275, F(5, 2)), (52, F(4, 5))])
def _(p):
    d, t = p
    v = F(d) / t
    kmh = lambda x: m(rf"{nb(x)}~\text{{km/h}}")
    return (rf"Un véhicule parcourt ${d}$ km en {dur(t)}. Quelle est sa vitesse moyenne ?",
            kmh(v), [kmh(d * t), kmh(F(d, int(t * 60))) if F(d, int(t * 60)).denominator in (1, 2, 4, 5, 10, 20, 25) else kmh(v * 2), kmh(v + 10), kmh(v / 2)])


@qtype("gra", "Distance = vitesse × durée, avec la durée exprimée en heures.",
       [(20, 30), (15, 48), (60, 45), (90, 20), (24, 15), (80, 90), (36, 25), (72, 35)])
def _(p):
    v, t = p
    dist = F(v * t, 60)
    km = lambda x: m(rf"{nb(x)}~\text{{km}}")
    return (rf"Un cycliste roule à la vitesse constante de ${v}$ km/h pendant ${t}$ min. Quelle distance parcourt-il ?" if v <= 40 else
            rf"Une voiture roule à la vitesse constante de ${v}$ km/h pendant ${t}$ min. Quelle distance parcourt-elle ?",
            km(dist), [km(v * t), km(F(v * t, 100)), km(dist * 2), km(dist + 5)])


@qtype("gra", "Durée = distance ÷ vitesse ; 0,5 h = 30 min, 0,25 h = 15 min.",
       [(240, 80), (150, 60), (45, 90), (350, 100), (120, 80), (25, 20), (400, 120), (70, 105)])
def _(p):
    d, v = p
    t = F(d, v)
    wrong = int(t) + F(round(float(t - int(t)) * 100), 60)  # 2,5 h read as 2 h 50 min
    alts = [dur(wrong) if wrong != t and (wrong * 60).denominator == 1 else dur(t + F(1, 6)), dur(t + F(1, 2)), dur(t - F(1, 4)) if t > F(1, 4) else dur(t + F(1, 4)), dur(t * 2)]
    return (rf"Un train parcourt ${d}$ km à la vitesse moyenne de ${v}$ km/h. Combien de temps dure le trajet ?", dur(t), alts)


@qtype("gra", "1 km/h = 1 000 m en 3 600 s : pour passer des km/h aux m/s, on divise par 3,6.",
       [36, 72, 90, 54, 18, 108, 45, 126])
def _(v):
    ms = lambda x: m(rf"{nb(x)}~\text{{m/s}}")
    return (rf"Un véhicule roule à ${v}$ km/h. Quelle est sa vitesse en mètres par seconde ?",
            ms(F(v * 10, 36)), [ms(F(v * 36, 10)), ms(F(v, 60)), ms(v * 1000), ms(F(v * 10, 36) + 5)])


@qtype("gra", "Volume d'une pyramide = aire de la base × hauteur ÷ 3.",
       [(12, 5), (30, 4), (18, 10), (9, 7), (24, 6), (15, 9), (36, 2), (21, 10)])
def _(p):
    B, h = p
    cm3 = lambda x: m(rf"{nb(x)}~\text{{cm}}^3")
    return (rf"Une pyramide a une base d'aire ${B}$ cm$^2$ et une hauteur de ${h}$ cm. Quel est son volume ?",
            cm3(F(B * h, 3)), [cm3(B * h), cm3(F(B * h, 2)), cm3(B + h), cm3(F(B * h, 3) + 3)])


@qtype("gra", "Volume d'un cône = π × r² × h ÷ 3 (valeur exacte en fonction de π).",
       [(3, 4), (2, 6), (5, 3), (6, 2), (4, 9), (3, 10), (1, 12), (6, 5)])
def _(p):
    r, h = p
    P = lambda k: m(rf"{nb(k)}\pi~\text{{cm}}^3")
    return (rf"Un cône de révolution a un rayon de base de ${r}$ cm et une hauteur de ${h}$ cm. Quel est son volume exact ?",
            P(F(r * r * h, 3)), [P(r * r * h), P(F(r * h, 3) if F(r * h, 3) != F(r * r * h, 3) else 2 * r * h), P(F(4 * r * r * h, 3)), P(F(r * r * h, 3) + 1)])


@qtype("gra", "1 L = 1 dm³ = 1 000 cm³ et 1 m³ = 1 000 L.",
       [(F(3, 2), "L", "cm^3", 1000), (750, "cm^3", "L", F(1, 1000)), (4, "L", "cm^3", 1000), (250, "cm^3", "L", F(1, 1000)),
        (F(2, 10), "L", "cm^3", 1000), (3, "m^3", "L", 1000), (12, "L", "dm^3", 1), (5000, "cm^3", "L", F(1, 1000))])
def _(p):
    x, a, b, f = p
    U = lambda s: rf"\text{{{s[:-2]}}}^3" if s.endswith("^3") else rf"\text{{{s}}}"
    V = lambda v: m(rf"{nb(v)}~{U(b)}")
    r = F(x) * f
    return (rf"Compléter : ${nb(x)}~{U(a)}=\;?\;{U(b)}$",
            V(r), [V(r * 10) if f != 1 else V(1000 * r), V(r / 10) if f != 1 else V(r / 1000), V(r * 100) if f != 1 else V(100 * r), V(r / 100) if f != 1 else V(r * 10)])


@qtype("gra", "1 m² = 100 dm² = 10 000 cm² : en aire, on multiplie par 100 à chaque changement d'unité.",
       [(3, "m", "cm"), (F(5, 2), "dm", "cm"), (45000, "cm", "m"), (F(6, 5), "km", "m"), (F(8, 10), "m", "dm"), (600, "mm", "cm"), (9, "m", "dm"), (5, "cm", "mm")])
def _(p):
    x, a, b = p
    order = ["km", "hm", "dam", "m", "dm", "cm", "mm"]
    k = order.index(b) - order.index(a)
    r = F(x) * F(100) ** k
    A = lambda s: rf"\text{{{s}}}^2"
    V = lambda v: m(rf"{nb(v)}~{A(b)}")
    lin = F(x) * F(10) ** k
    return (rf"Compléter : ${nb(x)}~{A(a)}=\;?\;{A(b)}$", V(r), [V(lin), V(F(x) * F(1000) ** k), V(r * 10), V(r / 10), V(r * 100), V(r / 100)])


# ============================================================ BUILD
THEMES = {"rel": ("Relatifs et fractions", "1F6FA8"), "pui": ("Puissances et racines carrées", "6A4C93"),
          "lit": ("Calcul littéral et équations", "2E7D6B"), "geo": ("Géométrie", "C0503A"),
          "don": ("Proportionnalité, statistiques, probabilités", "C77F0A"), "gra": ("Grandeurs et mesures", "8A5A2B")}
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
    assert len({Q[n + si * HALF][2] for si in range(4)}) == 4, n

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
                    rf"{{\Large\bfseries\color{{c{th}}}{'abcd'[i]})}}\quad{{\Large {shown[i]}}}\end{{tcolorbox}}")
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
open(f"{OUT}/quatrieme.tex", "w", encoding="utf-8").write("\n".join(tex))
json.dump([[n, th, g, h] for n, th, g, _, h in KEY], open(f"{OUT}/questions.json", "w"))
json.dump([t[3] for t in TYPES], open(f"{OUT}/hints.json", "w"), ensure_ascii=False, indent=0)
with open(f"{OUT}/corrige.txt", "w", encoding="utf-8") as f:
    for n, th, g, a, h in KEY:
        f.write(f"Q{n if n <= HALF else str((n - 1) % HALF + 1) + ' ' + 'ABCD'[(n - 1) // HALF]} ({THEMES[th][0]}) : {g}) {a}\n")
print(len(KEY), "questions ; fallback:", FALLBACK)
