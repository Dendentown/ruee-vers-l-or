"""Banque Terminale (spécialité mathématiques) : 6 thèmes x 8 types de questions x 4 jeux de valeurs.
Série A = questions 1-96, série B = 97-192 (n + 96 = même question, autres valeurs).
Toutes les bonnes réponses sont calculées ici."""
import json, os, random, re, sys
from fractions import Fraction as F
from math import comb, factorial
sys.path.insert(0, os.path.dirname(__file__))
from helpers import lf, m, sq

OUT = "build"
os.makedirs(OUT, exist_ok=True)
HALF = 96
TYPES = []


def qtype(theme, params):
    def deco(fn):
        TYPES.append((theme, fn, params))
        return fn
    return deco


def expr(pairs):
    """'2x-y+3z+1' from [(2,'x'),(-1,'y'),(3,'z'),(1,'')]; zero terms skipped."""
    out = ""
    for c, v in pairs:
        c = F(c)
        if c == 0:
            continue
        sign = "-" if c < 0 else ("+" if out else "")
        a = abs(c)
        if v and a == 1:
            body = v
        else:
            body = (lf(a, False) if a.denominator != 1 else str(a.numerator)) + v
        out += sign + body
    return out or "0"


def dec(x):
    """Fraction -> decimal string with a French comma (terminating decimals only)."""
    x = F(x)
    s = f"{float(x):.6f}".rstrip("0").rstrip(".")
    return s.replace(".", "{,}")


def ee(k):
    """e^k in LaTeX."""
    return "1" if k == 0 else "e" if k == 1 else f"e^{{{k}}}"


def ce(c, k):
    """c * e^k."""
    c = F(c)
    if c == 0:
        return "0"
    if k == 0:
        return lf(c)
    if c == 1:
        return ee(k)
    if c == -1:
        return "-" + ee(k)
    return lf(c) + ee(k)


def pt(p):
    return "(" + ";".join(str(v) for v in p) + ")"


def vec(p):
    return r"\begin{pmatrix}" + r"\\".join(str(v) for v in p) + r"\end{pmatrix}"


# ============================================================ SUITES
@qtype("sui", [(3, 2, 10), (5, -3, 8), (-4, 5, 12), (7, 4, 15)])
def _(p):
    a, r, k = p
    return (rf"$(u_n)$ est la suite arithmétique de premier terme $u_0={a}$ et de raison ${r}$. Que vaut $u_{{{k}}}$ ?",
            m(a + k * r), [m(a + (k - 1) * r), m(a + (k + 1) * r), m(k * r), m(a * r ** 2)])


@qtype("sui", [(2, 5), (3, 4), (2, 7), (3, 5)])
def _(p):
    q, n = p
    return (rf"Que vaut la somme $1+{q}+{q}^2+\dots+{q}^{{{n}}}$ ?",
            m((q ** (n + 1) - 1) // (q - 1)), [m(q ** (n + 1)), m((q ** n - 1) // (q - 1)), m(q ** (n + 1) - 1), m(q ** n)])


@qtype("sui", [(3, 1, 2, 5), (4, -2, 7, 1), (5, 3, 2, -1), (6, 1, 4, 3)])
def _(p):
    a, b, c, d = p
    num, den = expr([(a, "n^2"), (b, "")]), expr([(c, "n^2"), (d, "n")])
    return (rf"Que vaut $\displaystyle\lim_{{n\to+\infty}}\frac{{{num}}}{{{den}}}$ ?",
            m(lf(F(a, c))), [m(r"+\infty"), m("0"), m(lf(F(c, a))), m(lf(F(a, d)))])


@qtype("sui", [(F(1, 2), 3), (F(1, 3), 4), (F(2, 3), 2), (F(3, 4), 1)])
def _(p):
    q, c = p
    return (rf"La suite définie par $u_0=0$ et $u_{{n+1}}={lf(q, False)}\,u_n+{c}$ converge. Quelle est sa limite ?",
            m(lf(F(c) / (1 - q))), [m(lf(F(c) / (1 + q))), m(c), m(r"+\infty"), m(lf(F(c) * q))])


@qtype("sui", [(1, 5), (3, 6), (2, 7), (0, 9)])
def _(p):
    a, k = p
    return (rf"On pose $u_0={a}$ et, pour tout entier $n$, $u_{{n+1}}=u_n+2n+1$. Que vaut $u_{{{k}}}$ ?",
            m(a + k * k), [m(a + (k + 1) ** 2), m(a + 2 * k + 1), m(a + k * k - 1), m(k * k + 2 * k)])


@qtype("sui", [(2, 3), (5, 2), (3, 7), (4, 5)])
def _(p):
    a, b = p
    return (rf"Que vaut $\displaystyle\lim_{{n\to+\infty}}\frac{{{a}n+(-1)^n}}{{{b}n+1}}$ ?",
            m(lf(F(a, b))), [m(lf(F(b, a))), m("0"), m(r"+\infty"), m(r"\text{elle n'existe pas}")])


@qtype("sui", [(2, 5), (3, 2), (-2, 3), (F(1, 2), 8)])
def _(p):
    q, x = p
    return (rf"$(u_n)$ est une suite géométrique de raison ${lf(q, False)}$ telle que $u_3={x}$. Que vaut $u_5$ ?",
            m(lf(x * F(q) ** 2)), [m(lf(x * F(q))), m(lf(x * F(q) ** 3)), m(lf(x + 2 * F(q))), m(lf(x * 2 * F(q)))])


@qtype("sui", [(2, 1000), (3, 500), (2, 5000), (3, 2000)])
def _(p):
    q, N = p
    n = 0
    while q ** n <= N:
        n += 1
    return (rf"Quel est le plus petit entier naturel $n$ tel que ${q}^n>{N}$ ?",
            m(n), [m(n - 1), m(n + 1), m(n + 2), m(n - 2)])


# ============================================================ FONCTIONS
@qtype("fon", [(2, 1), (3, -2), (-1, 2), (4, 1)])
def _(p):
    a, b = p
    return (rf"Soit $f(x)=({expr([(a, 'x'), (b, '')])})^3$. Que vaut $f'(0)$ ?",
            m(3 * a * b * b), [m(3 * b * b), m(a * b ** 3), m(3 * a * b), m(b ** 3)])


@qtype("fon", [(1, 2, 1, 1), (2, 1, 1, 3), (3, -1, 2, 1), (1, 4, 2, 3)])
def _(p):
    a, b, c, d = p
    return (rf"Soit $f(x)=\dfrac{{{expr([(a, 'x'), (b, '')])}}}{{{expr([(c, 'x'), (d, '')])}}}$. Que vaut $f'(0)$ ?",
            m(lf(F(a * d - b * c, d * d))), [m(lf(F(b * c - a * d, d * d))), m(lf(F(a, c))), m(lf(F(a * d + b * c, d * d))), m(lf(F(a * d - b * c, d)))])


@qtype("fon", [(1, 2, 1), (-2, 3, 2), (3, -1, -1), (0, 5, 3)])
def _(p):
    pp, q, a = p
    s, c = 2 * a + pp, q - a * a
    f = expr([(1, "x^2"), (pp, "x"), (q, "")])
    y = lambda s_, c_: "y=" + expr([(s_, "x"), (c_, "")])
    return (rf"Quelle est l'équation de la tangente à la courbe de $f(x)={f}$ au point d'abscisse ${a}$ ?",
            m(y(s, c)), [m(y(s, q)), m(y(a + pp, c)), m(y(s, -c) if c else y(s, 1)), m(y(s, c + 1))])


@qtype("fon", [(2, 1, 3), (3, -1, -2), (1, 4, 5), (-2, 3, 1)])
def _(p):
    a, b, c = p
    return (rf"La courbe de $f(x)=\dfrac{{{expr([(a, 'x'), (b, '')])}}}{{{expr([(1, 'x'), (-c, '')])}}}$ admet une asymptote verticale. Laquelle ?",
            m(f"x={c}"), [m(f"x={-c}"), m(f"y={a}"), m(f"x={lf(F(-b, a), False)}"), m(f"y={c}")])


@qtype("fon", [(3, 1), (-6, 2), (2, -1), (-3, 5)])
def _(p):
    a, b = p
    f = expr([(1, "x^3"), (a, "x^2"), (b, "x")])
    return (rf"La courbe de $f(x)={f}$ admet un point d'inflexion. Quelle est son abscisse ?",
            m(lf(F(-a, 3))), [m(lf(F(a, 3))), m(lf(F(-a, 2))), m(lf(F(-a, 6))), m(lf(F(-2 * a, 3)))])


@qtype("fon", [1, 3, -1, -5])
def _(k):
    n = 3 if abs(k) < 2 else 1
    return (rf"Combien de solutions réelles l'équation $x^3-3x={k}$ admet-elle ?",
            m(n), [m(v) for v in (0, 1, 2, 3) if v != n])


@qtype("fon", [4, 9, 25, 16])
def _(a):
    r = int(a ** .5)
    return (rf"Quel est le minimum de la fonction $f(x)=x+\dfrac{{{a}}}{{x}}$ sur $]0;+\infty[$ ?",
            m(2 * r), [m(r), m(a), m(a + 1), m(2 * a)])


@qtype("fon", [(2, 1, 4), (3, 1, 5), (1, 3, 1), (4, 0, 1)])
def _(p):
    a, b, c = p
    r = int((a * c + b) ** .5)
    return (rf"Soit $f(x)=\sqrt{{{expr([(a, 'x'), (b, '')])}}}$. Que vaut $f'({c})$ ?",
            m(lf(F(a, 2 * r))), [m(lf(F(1, 2 * r))), m(lf(F(a, r))), m(lf(F(a, 2))), m(lf(F(a, 2 * r * r))), m(lf(F(2 * r, a))), m(lf(F(a, 2 * r) + 1))])


# ============================================================ EXPONENTIELLE ET LOGARITHME
@qtype("exl", [(2, 3, 1), (5, -2, 1), (1, 4, 3), (3, 3, 2)])
def _(p):
    a, b, c = p
    return (rf"Simplifier $\dfrac{{{ee(a)}\times {ee(b)}}}{{{ee(c)}}}$.",
            m(ee(a + b - c)), [m(ee(a * b - c)), m(ee(a + b + c)), m(ee(a - b + c)), m(ee(a + b))])


@qtype("exl", [(2, 3), (3, -2), (5, 1), (4, -7)])
def _(p):
    a, b = p
    return (rf"Quelle est la solution de l'équation $\ln({expr([(a, 'x'), (b, '')])})=0$ ?",
            m(lf(F(1 - b, a))), [m(lf(F(-b, a))), m(lf(F(1 + b, a))), m(rf"\dfrac{{e{'-' if b > 0 else '+'}{abs(b)}}}{{{a}}}"), m(lf(F(1 - b, a) + 1))])


@qtype("exl", [(2, 3, 2), (3, 4, 2), (2, 5, 1), (5, 3, 1)])
def _(p):
    b, mm, k = p
    L = lambda c: ("" if c == 1 else str(c)) + rf"\ln {b}"
    return (rf"Simplifier $\ln {b ** mm}-{'' if k == 1 else k}\ln {b}$.",
            m(L(mm - k)), [m(L(mm + k)), m(L(mm * k)), m(L(mm - k + 1)), m(rf"\ln {b ** mm - k * b}")])


@qtype("exl", [1, 2, -1, 3])
def _(a):
    return (rf"Soit $f(x)=x\,e^{{{'' if a == 1 else '-' if a == -1 else a}x}}$. Que vaut $f'(1)$ ?",
            m(ce(1 + a, a)), [m(ce(1, a)), m(ce(a, a)), m(ce(1 - a, a)), m(ce(1 + a, a + 1))])


@qtype("exl", [(2, 3), (5, 2), (3, 4), (7, 5)])
def _(p):
    a, b = p
    return (rf"Que vaut $\displaystyle\lim_{{x\to+\infty}}\frac{{{a}e^x+x^2}}{{{b}e^x+1}}$ ?",
            m(lf(F(a, b))), [m("0"), m(r"+\infty"), m(lf(F(b, a))), m(str(a))])


@qtype("exl", [(1, 1), (2, 3), (3, 1), (1, 4)])
def _(p):
    a, b = p
    return (rf"Soit $f(x)=\ln({expr([(a, 'x^2'), (b, '')])})$. Que vaut $f'(1)$ ?",
            m(lf(F(2 * a, a + b))), [m(lf(F(1, a + b))), m(str(2 * a)), m(lf(F(a, a + b))), m(lf(F(2, a + b)) if a != 1 else lf(F(2 * a + 1, a + b)))])


@qtype("exl", [(F(9, 10), F(1, 2)), (F(8, 10), F(1, 10)), (F(95, 100), F(1, 2)), (F(7, 10), F(1, 100))])
def _(p):
    q, s = p
    n = 0
    while q ** n >= s:
        n += 1
    return (rf"Quel est le plus petit entier naturel $n$ tel que ${dec(q)}^n<{dec(s)}$ ?",
            m(n), [m(n - 1), m(n + 1), m(n + 2), m(n - 2)])


@qtype("exl", [(2, 1, 3), (3, -2, 5), (1, 4, 2), (2, -1, 7)])
def _(p):
    k, b, a = p
    num = rf"\ln {a}" + (f"-{b}" if b > 0 else f"+{-b}")
    alt = rf"\ln {a}" + (f"+{b}" if b > 0 else f"-{-b}")
    fr = lambda t: t if k == 1 else rf"\dfrac{{{t}}}{{{k}}}"
    return (rf"Quelle est la solution de l'équation $e^{{{expr([(k, 'x'), (b, '')])}}}={a}$ ?",
            m(fr(num)), [m(fr(alt)), m(fr(rf"\ln {a}") + (f"-{b}" if b > 0 else f"+{-b}")), m(rf"e^{{{a}}}" if k == 1 else rf"\dfrac{{e^{{{a}}}}}{{{k}}}"), m(fr(rf"\ln {a}"))])


# ============================================================ INTEGRALES ET EQUATIONS DIFFERENTIELLES
@qtype("int", [(2, 2), (3, 1), (1, 3), (2, 3)])
def _(p):
    a, k = p
    xk = "x" if k == 1 else f"x^{{{k}}}"
    return (rf"Que vaut $\displaystyle\int_0^{{{a}}} {xk}\,\mathrm{{d}}x$ ?",
            m(lf(F(a ** (k + 1), k + 1))), [m(a ** (k + 1)), m(lf(F(a ** k, k)) if k > 1 else lf(F(a * a, 1))), m(k * a ** (k - 1)), m(lf(F(a ** (k + 1), k + 2)))])


@qtype("int", [2, 3, 1, 4])
def _(a):
    ea = "e" if a == 1 else f"e^{{{a}}}"
    return (rf"Que vaut $\displaystyle\int_0^{{1}} e^{{{'' if a == 1 else a}x}}\,\mathrm{{d}}x$ ?",
            m(rf"{ea}-1" if a == 1 else rf"\dfrac{{{ea}-1}}{{{a}}}"), [m(rf"{ea}-1" if a != 1 else rf"{ea}+1"), m(rf"{'' if a == 1 else a}({ea}-1)" if a != 1 else "e"), m(rf"\dfrac{{{ea}}}{{{a}}}" if a != 1 else rf"\dfrac{{e-1}}{{2}}"), m(rf"{a}{ea}" if a != 1 else "1")])


@qtype("int", [(2, 1), (3, 2), (1, 3), (4, 1)])
def _(p):
    a, b = p
    E = lambda c1, c0: expr([(c1, "e"), (c0, "")])
    return (rf"Que vaut $\displaystyle\int_1^{{e}} \left(\frac{{{a}}}{{x}}+{b}\right)\mathrm{{d}}x$ ?",
            m(E(b, a - b)), [m(E(b, a)), m(E(a, b)), m(E(a + b, 0)), m(E(b, a + b))])


@qtype("int", [(2, 1), (3, 0), (-1, 2), (4, 1)])
def _(p):
    a, c = p
    def Fx(k, c0):
        e = rf"e^{{{'-' if a == -1 else a}x}}"
        lead = e if k == 1 else ("-" + e) if k == -1 else rf"{lf(k, False)}\,{e}"
        return "F(x)=" + lead + ("" if c0 == 0 else ("+" if c0 > 0 else "-") + lf(abs(c0), False))
    k = F(1, a)
    return (rf"Quelle est la primitive $F$ de $f(x)=e^{{{'-' if a == -1 else a}x}}$ sur $\mathbb{{R}}$ telle que $F(0)={c}$ ?",
            m(Fx(k, c - k)), [m(Fx(k, F(c))), m(Fx(F(a), c - a)), m(Fx(k, c + k)), m(Fx(-k, c + k))])


@qtype("int", [3, 6, 2, 1])
def _(a):
    return (rf"Quelle est la valeur moyenne de la fonction $x\mapsto x^2$ sur l'intervalle $[0;{a}]$ ?",
            m(lf(F(a * a, 3))), [m(lf(F(a * a, 2))), m(lf(F(a ** 3, 3))), m(a * a), m(lf(F(a, 3))), m(lf(F(a * a, 6))), m(lf(F(2 * a * a, 3)))])


@qtype("int", [(2, 6), (3, -1), (-1, 4), (5, 10)])
def _(p):
    a, b = p
    rhs = expr([(a, "y"), (b, "")])
    return (rf"Quelle est la solution constante de l'équation différentielle $y'={rhs}$ ?",
            m("y=" + lf(F(-b, a))), [m("y=" + lf(F(b, a))), m("y=" + lf(F(-a, b))), m(f"y={b}"), m("y=0")])


@qtype("int", [(2, 3), (-1, 5), (3, 1), (1, 4)])
def _(p):
    a, c = p
    return (rf"$f$ est la solution de $y'={expr([(a, 'y')])}$ telle que $f(0)={c}$. Que vaut $f(1)$ ?",
            m(ce(c, a)), [m(ce(c, -a)), m(ce(a, c)), m(expr([(c, '')]) + "+" + ee(a)), m(ce(c + 1, a))])


@qtype("int", [1, 2, 3, 4])
def _(a):
    v = lambda c, k, d: expr([(c, ee(k) if k else "")]) if d == 0 else (ce(c, k) + ("+" if d > 0 else "-") + str(abs(d)) if c else str(d))
    ans = "1" if a == 1 else ce(a - 1, a) + "+1"
    return (rf"Que vaut $\displaystyle\int_0^{{{a}}} x\,e^{{x}}\,\mathrm{{d}}x$ ?",
            m(ans), [m(ce(a, a)), m(ce(a - 1, a) if a > 1 else "0"), m(ce(a + 1, a) + "-1"), m(ce(a - 1, a) + "-1" if a > 1 else "e-1")])


# ============================================================ GEOMETRIE DANS L'ESPACE
@qtype("esp", [((1, 2, -1), (3, 0, 2)), ((2, -1, 4), (1, 3, 1)), ((-2, 1, 3), (4, 2, -1)), ((3, 1, -2), (2, -5, 1))])
def _(p):
    u, v = p
    d = sum(a * b for a, b in zip(u, v))
    return (rf"Dans un repère orthonormé, que vaut le produit scalaire $\vec u\cdot\vec v$ pour $\vec u{vec(u)}$ et $\vec v{vec(v)}$ ?",
            m(d), [m(d + 2), m(-d) if d else m(1), m(sum(u) * sum(v)), m(sum(a + b for a, b in zip(u, v)))])


@qtype("esp", [(1, 2, 2), (2, 3, 6), (1, 1, 1), (2, -1, 2)])
def _(u):
    n2 = sum(a * a for a in u)
    return (rf"Dans un repère orthonormé, quelle est la norme du vecteur $\vec u{vec(u)}$ ?",
            m(sq(n2)), [m(n2), m(sum(abs(a) for a in u)), m(sq(n2 + 1)), m(sq(sum(u) ** 2) if sum(u) ** 2 != n2 else sq(n2 + 3)), m(sq(4 * n2)), m(sq(n2 + 2))])


@qtype("esp", [(2, 1, -3), (1, 2, 3), (4, -1, 1), (3, 3, -6)])
def _(p):
    a, b, c = p
    return (rf"Pour quelle valeur de $m$ les vecteurs $\vec u{vec((1, 'm', 2))}$ et $\vec v{vec((a, b, c))}$ sont-ils orthogonaux ?",
            m("m=" + lf(F(-(a + 2 * c), b))), [m("m=" + lf(F(a + 2 * c, b))), m("m=" + lf(F(-(a + c), b))), m("m=" + lf(F(-(a + 2 * c), b) + 1)), m("m=0")])


@qtype("esp", [((1, 2, -1), (1, 0, 2)), ((2, -1, 3), (0, 1, 1)), ((1, 1, 1), (2, -1, 3)), ((3, 0, -2), (1, 4, 1))])
def _(p):
    n, A = p
    d = -sum(a * b for a, b in zip(n, A))
    P = lambda nn, dd: expr([(nn[0], "x"), (nn[1], "y"), (nn[2], "z"), (dd, "")]) + "=0"
    return (rf"Quelle est une équation du plan passant par $A{pt(A)}$ et de vecteur normal $\vec n{vec(n)}$ ?",
            m(P(n, d)), [m(P(n, -d) if d else P(n, 1)), m(P(n, d + 1)), m(P(A, -sum(a * b for a, b in zip(n, A))) if any(A) else P(n, 2))])


@qtype("esp", [((1, -1, 3), (2, 1, -1), 2), ((0, 2, 1), (1, -1, 3), -1), ((2, 0, -1), (-1, 2, 1), 3), ((-1, 1, 2), (3, 1, -2), 1)])
def _(p):
    P0, u, t = p
    pnt = tuple(a + t * b for a, b in zip(P0, u))
    sys_ = r"\left\{\begin{array}{l}" + r"\\".join(f"{c}={expr([(a, ''), (b, 't')])}" for c, a, b in zip("xyz", P0, u)) + r"\end{array}\right."
    near = [tuple(v + (1 if i == j else 0) for j, v in enumerate(pnt)) for i in range(3)]
    return (rf"Lequel de ces points appartient à la droite de représentation paramétrique ${sys_}$ ($t\in\mathbb{{R}}$) ?",
            m(pt(pnt)), [m(pt(q)) for q in near])


@qtype("esp", [(2, (1, 3, 3)), (3, (2, -1, 1)), (-2, (1, 4, 2)), (4, (1, 2, -1))])
def _(p):
    k, v = p
    u = (k * v[0], "m", k * v[2])
    return (rf"Pour quelle valeur de $m$ les vecteurs $\vec u{vec(u)}$ et $\vec v{vec(v)}$ sont-ils colinéaires ?",
            m(f"m={k * v[1]}"), [m("m=" + lf(F(v[1], k))), m(f"m={k + v[1]}"), m(f"m={-k * v[1]}")])


@qtype("esp", [((1, 2, 3), (3, 3, 5)), ((0, -1, 2), (2, 1, 3)), ((2, 0, 1), (5, 4, 1)), ((-1, 1, 0), (1, 2, 2))])
def _(p):
    A, B = p
    d2 = sum((a - b) ** 2 for a, b in zip(A, B))
    return (rf"Dans un repère orthonormé, quelle est la distance entre $A{pt(A)}$ et $B{pt(B)}$ ?",
            m(sq(d2)), [m(d2), m(sum(abs(a - b) for a, b in zip(A, B))), m(sq(d2 + 2)), m(sq(sum(abs(a - b) for a, b in zip(A, B)) ** 2))])


@qtype("esp", [(8, (1, 1, 0), (1, 2, 0)), (5, (0, 1, 2), (1, 0, 1)), (3, (2, -1, 0), (1, 1, -1)), (10, (1, 2, 3), (2, 1, 1))])
def _(p):
    d, P0, u = p
    t = F(d - sum(P0), sum(u))
    assert t.denominator == 1
    t = int(t)
    at = lambda s: pt(tuple(a + s * b for a, b in zip(P0, u)))
    sys_ = r"\left\{\begin{array}{l}" + r"\\".join(f"{c}={expr([(a, ''), (b, 't')])}" for c, a, b in zip("xyz", P0, u)) + r"\end{array}\right."
    return (rf"Quel est le point d'intersection de la droite ${sys_}$ ($t\in\mathbb{{R}}$) et du plan $x+y+z={d}$ ?",
            m(at(t)), [m(at(t + 1)), m(at(t - 1)), m(pt(P0)) if t else m(at(2)), m(at(-t))])


# ============================================================ PROBABILITES ET DENOMBREMENT
@qtype("prb", [(4, 2), (5, 1), (6, 3), (5, 2)])
def _(p):
    n, k = p
    return (rf"$X$ suit la loi binomiale $\mathcal{{B}}\left({n};\frac12\right)$. Que vaut $P(X={k})$ ?",
            m(lf(F(comb(n, k), 2 ** n))), [m(lf(F(1, 2 ** n))), m(lf(F(k, n))), m(lf(F(comb(n, k), 2 ** k))), m(lf(F(1, 2 ** k)))])


@qtype("prb", [(20, F(1, 4)), (30, F(1, 3)), (12, F(1, 6)), (40, F(3, 8))])
def _(p):
    n, q = p
    return (rf"$X$ suit la loi binomiale $\mathcal{{B}}\left({n};{lf(q, False)}\right)$. Quelle est son espérance $E(X)$ ?",
            m(lf(n * q)), [m(lf(n * q * (1 - q))), m(lf(n * (1 - q))), m(lf(q)), m(lf(n * q + 1))])


@qtype("prb", [(10, F(1, 2)), (20, F(1, 4)), (18, F(1, 3)), (16, F(3, 4))])
def _(p):
    n, q = p
    return (rf"$X$ suit la loi binomiale $\mathcal{{B}}\left({n};{lf(q, False)}\right)$. Quelle est sa variance $V(X)$ ?",
            m(lf(n * q * (1 - q))), [m(lf(n * q)), m(lf(n * q * q)), m(lf(n * (1 - q) ** 2)), m(lf(n * q * (1 - q) + 1)), m(lf(n * q * (1 - q) / 2))])


@qtype("prb", [(F(4, 10), F(3, 10)), (F(6, 10), F(5, 10)), (F(7, 10), F(2, 10)), (F(25, 100), F(8, 10))])
def _(p):
    a, b = p
    return (rf"On a $P(A)={dec(a)}$ et $P_A(B)={dec(b)}$. Que vaut $P(A\cap B)$ ?",
            m(dec(a * b)), [m(dec(a + b)) if a + b <= 1 else m(dec(a + b - 1)), m(dec(a * (1 - b))), m(dec(b - a)) if b > a else m(dec(a - b)), m(dec(b)), m(dec(a)), m(dec(1 - a * b))])


@qtype("prb", [(F(3, 10), F(5, 10), F(2, 10)), (F(6, 10), F(4, 10), F(1, 10)), (F(5, 10), F(8, 10), F(4, 10)), (F(2, 10), F(9, 10), F(3, 10))])
def _(p):
    a, b, c = p
    return (rf"On a $P(A)={dec(a)}$, $P_A(B)={dec(b)}$ et $P_{{\overline{{A}}}}(B)={dec(c)}$. Que vaut $P(B)$ ?",
            m(dec(a * b + (1 - a) * c)), [m(dec(a * b)), m(dec(b + c)) if b + c <= 1 else m(dec(b * c)), m(dec(a * b + a * c)), m(dec((b + c) / 2)), m(dec((1 - a) * c)), m(dec(a + c * (1 - a)))])


@qtype("prb", [(5, 2), (6, 3), (8, 2), (7, 3)])
def _(p):
    n, k = p
    return (rf"Combien y a-t-il de façons de choisir {k} élèves parmi {n} (sans tenir compte de l'ordre) ?",
            m(comb(n, k)), [m(factorial(n) // factorial(n - k)), m(n ** k), m(n * k), m(comb(n, k) + n)])


@qtype("prb", [(3, 4), (2, 5), (4, 3), (5, 2)])
def _(p):
    n, k = p
    return (rf"Combien de codes de {k} caractères peut-on former avec un alphabet de {n} symboles (répétitions autorisées) ?",
            m(n ** k), [m(k ** n), m(n * k), m(comb(n + k - 1, k)), m(factorial(n) // factorial(n - k) if n >= k else factorial(k))])


@qtype("prb", [(3, F(1, 2)), (2, F(1, 3)), (4, F(1, 2)), (3, F(1, 4))])
def _(p):
    n, q = p
    return (rf"$X$ suit la loi binomiale $\mathcal{{B}}\left({n};{lf(q, False)}\right)$. Que vaut $P(X\geq 1)$ ?",
            m(lf(1 - (1 - q) ** n)), [m(lf((1 - q) ** n)), m(lf(q ** n)), m(lf(n * q)), m(lf(1 - q ** n)), m(lf(1 - q)), m(lf(1 - (1 - q) ** (n - 1)))])


# ============================================================ BUILD
THEMES = {"sui": ("Suites", "1F6FA8"), "fon": ("Fonctions", "6A4C93"), "exl": ("Exponentielle et logarithme", "2E7D6B"),
          "int": ("Intégrales et équations différentielles", "C77F0A"), "esp": ("Géométrie dans l'espace", "C0503A"),
          "prb": ("Probabilités et dénombrement", "8A5A2B")}
ORDER = list(THEMES)
PER = 8

Q = {}
FALLBACK = []
for th in ORDER:
    assert len([t for t in TYPES if t[0] == th]) == PER, th
for ti, th in enumerate(ORDER):
    types = [t for t in TYPES if t[0] == th]
    for k, (_, fn, params) in enumerate(types):
        assert len(params) == 4
        for j in range(2):
            nA = ti * 2 * PER + k * 2 + j + 1
            for serie, idx, n in (("A", j, nA), ("B", 2 + j, nA + HALF)):
                st, ans, dis = fn(params[idx])
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
                                opts.append(c)
                            if len(opts) == 4:
                                break
                if len(opts) < 4 and "=" not in ans and "text" not in ans:
                    c = ans.strip("$")
                    for cand in ([c[1:]] if c.startswith("-") else ["-" + c]) + [c + "+1", "2" + c if c[0] in "\\e" else c + "+2"]:
                        if m(cand) not in opts and len(opts) < 4:
                            opts.append(m(cand)); FALLBACK.append((n, cand))
                assert len(opts) == 4, (n, ans, dis)
                Q[n] = (th, serie, st, opts)
for n in range(1, HALF + 1):
    assert Q[n][2] != Q[n + HALF][2], n

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
    st = st.replace(" ?", "~?").replace(" :", "~:")
    rng = random.Random(n * 11 + 5)
    perm = [0, 1, 2, 3]
    rng.shuffle(perm)
    shown = [opts[i] for i in perm]
    good = "abcd"[perm.index(0)]
    KEY.append([n, th, good, opts[0]])
    lab = THEMES[th][0]
    num = n if n <= HALF else f"{n - HALF} B"
    ob = lambda i: (rf"\begin{{tcolorbox}}[enhanced,nobeforeafter,width=7.1cm,height=2.1cm,valign=center,colback=c{th}!6,colframe=c{th},arc=2.5mm,boxrule=0.9pt,left=3mm]"
                    rf"{{\Large\bfseries\color{{c{th}}}{'abcd'[i]})}}\quad{{\Large {shown[i]}}}\end{{tcolorbox}}")
    tex.append(rf"""\begin{{tcolorbox}}[enhanced,width=16cm,height=14cm,colback=white,colframe=c{th},boxrule=2pt,arc=0mm,
left=6mm,right=6mm,top=0mm,bottom=4mm,sharp corners,
overlay={{\fill[c{th}] (frame.north west) rectangle ([yshift=-1.25cm]frame.north east);
\node[anchor=west,text=white,font=\sffamily\bfseries\LARGE] at ([xshift=5mm,yshift=-0.62cm]frame.north west) {{Question {num}}};
\node[anchor=east,text=white,font=\sffamily\itshape\large] at ([xshift=-5mm,yshift=-0.62cm]frame.north east) {{{lab}}};}}]
\vspace*{{1.75cm}}
\begin{{minipage}}[t][6.9cm][c]{{\linewidth}}{'\\LARGE' if len(st) < 120 else '\\Large'}\centering
\begin{{minipage}}{{0.95\linewidth}}\raggedright\linespread{{1.25}}\selectfont {st}\end{{minipage}}
\end{{minipage}}

\vfill
{ob(0)}\hfill{ob(1)}\par\vspace{{2.5mm}}
{ob(2)}\hfill{ob(3)}
\end{{tcolorbox}}
\newpage""")
tex.append(r"\end{document}")
open(f"{OUT}/terminale.tex", "w", encoding="utf-8").write("\n".join(tex))
json.dump([[n, th, g] for n, th, g, _ in KEY], open(f"{OUT}/questions.json", "w"))
with open(f"{OUT}/corrige.txt", "w", encoding="utf-8") as f:
    for n, th, g, a in KEY:
        f.write(f"Q{n if n <= HALF else str(n - HALF) + ' B'} ({THEMES[th][0]}) : {g}) {a}\n")
print(len(KEY), "questions"); print("fallback:", FALLBACK)
