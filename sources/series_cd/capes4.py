"""Banque CAPES : 50 types de questions x 8 jeux de valeurs.
Séries A, B, C, D = questions 1-100, 101-200, 201-300, 301-400 (n + 100k = même question, autres valeurs).
Toutes les bonnes réponses sont calculées ici."""
import json, math, random, subprocess, os
from fractions import Fraction as F
from math import comb, gcd, factorial

OUT = "build4"
os.makedirs(OUT, exist_ok=True)


# ------------------------------------------------------------ helpers
def lf(x, d=True):
    """LaTeX d'un rationnel."""
    x = F(x)
    if x.denominator == 1:
        return str(x.numerator)
    s = "-" if x < 0 else ""
    fr = r"\dfrac" if d else r"\frac"
    return f"{s}{fr}{{{abs(x.numerator)}}}{{{x.denominator}}}"


def m(s):
    return f"${s}$"


def pmat(rows):
    return r"\begin{pmatrix}" + r"\\".join("&".join(str(v) for v in r) for r in rows) + r"\end{pmatrix}"


def det(M):
    M = [[F(v) for v in r] for r in M]
    n = len(M)
    if n == 1:
        return M[0][0]
    return sum((-1) ** j * M[0][j] * det([r[:j] + r[j + 1:] for r in M[1:]]) for j in range(n))


def rank(M):
    M = [[F(v) for v in r] for r in M]
    r = 0
    rows, cols = len(M), len(M[0])
    for c in range(cols):
        piv = next((i for i in range(r, rows) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        for i in range(rows):
            if i != r and M[i][c] != 0:
                f = M[i][c] / M[r][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        r += 1
    return r


def harm(k):
    return sum(F(1, i) for i in range(1, k + 1))


def sq(n):
    """LaTeX de sqrt(n) simplifiée."""
    a, b = 1, n
    for f in range(2, int(n ** .5) + 1):
        while b % (f * f) == 0:
            b //= f * f
            a *= f
    if b == 1:
        return str(a)
    return (f"{a}" if a > 1 else "") + rf"\sqrt{{{b}}}"


def frac_sq(num, rad):
    """num / sqrt(rad), rationalised: num*sqrt(rad)/rad."""
    a, b = 1, rad
    for f in range(2, int(rad ** .5) + 1):
        while b % (f * f) == 0:
            b //= f * f
            a *= f
    # num/(a sqrt b) = num sqrt b /(a b)
    if b == 1:
        return lf(F(num, a))
    c = F(num, a * b)
    top = f"{c.numerator}" if c.numerator != 1 else ""
    s = rf"{top}\sqrt{{{b}}}"
    return s if c.denominator == 1 else rf"\dfrac{{{s}}}{{{c.denominator}}}"


def angle(t):
    """t en fraction de pi, réduit dans ]-pi, pi]."""
    t = F(t)
    while t <= -1:
        t += 2
    while t > 1:
        t -= 2
    if t == 0:
        return "0"
    s = "-" if t < 0 else ""
    t = abs(t)
    if t == 1:
        return s + r"\pi"
    if t.denominator == 1:
        return f"{s}{t.numerator}\\pi"
    num = "" if t.numerator == 1 else str(t.numerator)
    return rf"{s}\dfrac{{{num}\pi}}{{{t.denominator}}}"


TYPES = []


def ex(k):
    return "e" if k == 1 else f"e^{{{k}}}"


def qtype(theme, params):
    def deco(fn):
        TYPES.append((theme, fn, params))
        return fn
    return deco


# ============================================================ ANALYSE
@qtype("ana", [2, 3, -1, 5])
def _(a):
    sg = "+" if a > 0 else "-"
    return (rf"Que vaut $\displaystyle\lim_{{n\to+\infty}}\left(1{sg}\frac{{{abs(a)}}}{{n}}\right)^{{n}}$ ?",
            m(rf"e^{{{a}}}"), [m("1"), m(r"+\infty"), m(rf"e^{{{lf(F(1, a), False)}}}"), m("e")])


@qtype("ana", [(2, 3), (-1, 4), (3, 5), (-2, 1)])
def _(p):
    a, b = p
    ca = {1: "", -1: "-"}.get(a, str(a))
    return (rf"Soit $f(x)=e^{{{ca}x}}\cos({'' if b == 1 else b}x)$. Que vaut $f'(0)$ ?",
            m(str(a)), [m(str(b)), m(str(a + b)), m("0"), m(str(a - b)), m(str(-a))])


@qtype("ana", [1, 2, 3, 4])
def _(k):
    xk = "x" if k == 1 else f"x^{{{k}}}"
    e = f"e^{{{k + 1}}}"
    kk = "" if k == 1 else str(k)
    return (rf"Que vaut $\displaystyle\int_1^{{e}} {xk}\ln x\,\mathrm{{d}}x$ ?",
            m(rf"\dfrac{{{kk}{e}+1}}{{{(k + 1) ** 2}}}"),
            [m(rf"\dfrac{{{e}}}{{{k + 1}}}"), m(rf"\dfrac{{{kk}{e}-1}}{{{(k + 1) ** 2}}}"),
             m(rf"\dfrac{{{k + 1}{e}+1}}{{{(k + 1) ** 2}}}")])


@qtype("ana", [F(1, 3), F(2, 5), F(3, 4), F(1, 4)])
def _(r):
    return (rf"Que vaut $\displaystyle\sum_{{n=0}}^{{+\infty}}\left({lf(r, False)}\right)^{{n}}$ ?",
            m(lf(1 / (1 - r))), [m(lf(r / (1 - r))), m(lf(1 - r)), m(lf(1 / (1 + r))), m(r"+\infty")])


@qtype("ana", [1, 2, 3, 4])
def _(k):
    v = harm(k) / k
    return (rf"Que vaut $\displaystyle\sum_{{n=1}}^{{+\infty}}\frac{{1}}{{n(n+{k})}}$ ?",
            m(lf(v)), [m(lf(F(1, k))), m(lf(F(1, k * k))), m(lf(harm(k))), m(lf(v + F(1, 2))), m("2"), m(r"\ln 2")])


@qtype("ana", [(3, 2), (5, 4), (2, 7), (6, 5)])
def _(p):
    a, b = p
    return (rf"Que vaut $\displaystyle\lim_{{x\to 0}}\frac{{e^{{{a}x}}-1}}{{\sin({b}x)}}$ ?",
            m(lf(F(a, b))), [m(lf(F(b, a))), m(str(a)), m("1"), m(lf(F(a * a, b)))])


@qtype("ana", [2, 3, 5, 4])
def _(a):
    return (rf"Quel est le coefficient de $x^2$ dans le développement limité à l'ordre 2 en $0$ de $\ln(1+{a}x)$ ?",
            m(lf(F(-a * a, 2))), [m(lf(F(a * a, 2))), m(lf(F(-a, 2))), m(str(a * a)), m(str(-a * a))])


@qtype("ana", [(F(1, 2), 3), (F(1, 3), 4), (F(2, 3), 1), (F(1, 4), 6)])
def _(p):
    a, b = p
    l = F(b) / (1 - a)
    return (rf"La suite définie par $u_0=0$ et $u_{{n+1}}={lf(a, False)}\,u_n+{b}$ converge. Quelle est sa limite ?",
            m(lf(l)), [m(lf(F(b) / (1 + a))), m(str(b)), m(r"+\infty"), m(lf(F(b) * a))])


@qtype("ana", [(2, 1), (3, 2), (5, 3), (4, 1)])
def _(p):
    a, k = p
    nk = "n" if k == 1 else f"n^{{{k}}}"
    return (rf"Quel est le rayon de convergence de la série entière $\displaystyle\sum_{{n\geq 1}}\frac{{{nk}}}{{{a}^{{n}}}}\,x^{{n}}$ ?",
            m(str(a)), [m(lf(F(1, a))), m(str(a ** k) if a ** k != a else str(a + 1)), m(r"+\infty"), m("1")])


@qtype("ana", [(2, 3), (1, 5), (3, 2), (-1, 4)])
def _(p):
    a, c = p
    s = f"+{a}" if a > 0 else f"-{-a}"
    ay = "" if abs(a) == 1 else str(abs(a))
    s = ("+" if a > 0 else "-") + ay
    return (rf"Soit $y$ la solution de $y'{s}y=0$ telle que $y(0)={c}$. Que vaut $y(1)$ ?",
            m(rf"{c}{ex(-a)}"), [m(rf"{c}{ex(a)}"), m(ex(-a)), m(str(c - a)), m(rf"{c + 1}{ex(-a)}")])


# ============================================================ ALGEBRE / ARITHMETIQUE
@qtype("alg", [(252, 198), (1071, 462), (391, 299), (840, 588)])
def _(p):
    a, b = p
    g = gcd(a, b)
    return (rf"Que vaut $\mathrm{{PGCD}}({a},{b})$ ?",
            m(str(g)), [m(str(2 * g)), m(str(g // 2 if g % 2 == 0 else g + 6)), m("1"), m(str(3 * g))])


@qtype("alg", [(2, 100, 7), (3, 50, 11), (5, 77, 13), (7, 64, 9)])
def _(p):
    a, n, md = p
    r = pow(a, n, md)
    dis = [m(str(x)) for x in [(r + 1) % md, (r + 2) % md, (r - 1) % md, (r + 3) % md] if x != r]
    return (rf"Quel est le reste de la division euclidienne de ${a}^{{{n}}}$ par ${md}$ ?", m(str(r)), dis)


@qtype("alg", [360, 720, 504, 1000])
def _(N):
    d = sum(1 for i in range(1, N + 1) if N % i == 0)
    return (rf"Combien l'entier ${N}$ possède-t-il de diviseurs positifs ?",
            m(str(d)), [m(str(d - 2)), m(str(d + 4)), m(str(d // 2)), m(str(d + 1))])


@qtype("alg", [(7, 2026), (3, 2027), (9, 1001), (2, 2028)])
def _(p):
    a, n = p
    r = pow(a, n, 10)
    dis = [m(str(x)) for x in [(r + 2) % 10, (r + 4) % 10, (r + 6) % 10, (r + 1) % 10] if x != r]
    return (rf"Quel est le chiffre des unités de ${a}^{{{n}}}$ ?", m(str(r)), dis)


@qtype("alg", [(-3, 5), (4, -2), (-5, 7), (6, 3)])
def _(p):
    b, c = p
    pol = "X^2" + (f"+{b}X" if b > 0 else f"-{-b}X") + (f"+{c}" if c > 0 else f"-{-c}")
    return (rf"Soient $x_1,x_2$ les racines complexes de ${pol}$. Que vaut $x_1^2+x_2^2$ ?",
            m(str(b * b - 2 * c)), [m(str(b * b + 2 * c)), m(str(-b)), m(str(c * c)), m(str(b * b - c))])


@qtype("alg", [36, 45, 100, 84])
def _(n):
    phi = sum(1 for k in range(1, n + 1) if gcd(k, n) == 1)
    return (rf"Que vaut l'indicatrice d'Euler $\varphi({n})$ ?",
            m(str(phi)), [m(str(n - 1)), m(str(n // 2)), m(str(phi + 2)), m(str(phi * 2))])


@qtype("alg", [(5, 17), (7, 26), (4, 15), (9, 22)])
def _(p):
    a, md = p
    inv = pow(a, -1, md)
    dis = [m(str(x)) for x in [md - inv, (inv + 1) % md, (inv * 2) % md, (inv + 3) % md] if x != inv and x != 0]
    return (rf"Quel est l'inverse de ${a}$ dans $\mathbb{{Z}}/{md}\mathbb{{Z}}$ ?", m(str(inv)), dis)


@qtype("alg", [(6, 2), (5, 3), (7, 2), (8, 3)])
def _(p):
    n, k = p
    c = comb(n, k) * 2 ** k
    return (rf"Quel est le coefficient de $x^{{{k}}}$ dans le développement de $(1+2x)^{{{n}}}$ ?",
            m(str(c)), [m(str(comb(n, k))), m(str(comb(n, k) * 2)), m(str(c * 2)), m(str(2 ** k))])


@qtype("alg", [10, 20, 12, 15])
def _(n):
    s = n * (n + 1) * (2 * n + 1) // 6
    return (rf"Que vaut $\displaystyle\sum_{{k=1}}^{{{n}}}k^{{2}}$ ?",
            m(str(s)), [m(str(n * n * (n + 1) ** 2 // 4)), m(str(n * (n + 1) // 2)), m(str(n ** 3)), m(str(s + n))])


@qtype("alg", [3, 4, 5, 6])
def _(n):
    a, b = 2 ** n - 1, 2 - 2 ** n
    P = lambda x, y: f"{x}X" + (f"+{y}" if y >= 0 else f"-{-y}")
    return (rf"Quel est le reste de la division euclidienne de $X^{{{n}}}$ par $(X-1)(X-2)$ ?",
            m(P(a, b)), [m(P(2 ** n, 1 - 2 ** n)), m(P(a, -b)), m(P(2 ** n - 2, 3 - 2 ** n)), m(str(2 ** n))])


# ============================================================ ALGEBRE LINEAIRE
@qtype("lin", [((3, -2), (4, 1)), ((5, 2), (7, 3)), ((-1, 4), (2, 6)), ((2, 9), (1, -3))])
def _(M):
    d = det(M)
    (a, b), (c, e) = M
    return (rf"Que vaut le déterminant de $A={pmat(M)}$ ?",
            m(lf(d)), [m(lf(a * e + b * c)), m(lf(a + e)), m(lf(b * c - a * e)), m(lf(d + 1))])


@qtype("lin", [((1, 2, 0), (0, 1, 3), (4, 0, 1)), ((2, 1, 1), (1, 3, 2), (1, 0, 0)),
               ((1, 0, 2), (3, 1, 0), (0, 2, 1)), ((3, 1, 0), (0, 2, 1), (1, 0, 1))])
def _(M):
    d = det(M)
    prod = M[0][0] * M[1][1] * M[2][2]
    return (rf"Que vaut le déterminant de $A={pmat(M)}$ ?",
            m(lf(d)), [m(lf(-d)), m(lf(prod)), m(lf(d + 2)), m(lf(d - 4))])


@qtype("lin", [((1, 2), (3, 4)), ((2, -1), (5, 3)), ((0, 3), (2, 1)), ((4, 1), (-2, 1))])
def _(M):
    (a, b), (c, d) = M
    t = a * a + 2 * b * c + d * d
    return (rf"Soit $A={pmat(M)}$. Que vaut $\mathrm{{tr}}(A^2)$ ?",
            m(str(t)), [m(str((a + d) ** 2)), m(str(a * a + d * d)), m(str(a * a + b * b + c * c + d * d)), m(str(t + 2))])


@qtype("lin", [((1, 2, 3), (2, 4, 6), (1, 1, 1)), ((1, 2, 1), (2, 4, 2), (3, 6, 3)),
               ((1, 0, 1), (0, 1, 1), (1, 1, 2)), ((1, 1, 0), (0, 1, 1), (1, 0, 1))])
def _(M):
    r = rank(M)
    return (rf"Quel est le rang de la matrice $A={pmat(M)}$ ?",
            m(str(r)), [m(str(x)) for x in [0, 1, 2, 3] if x != r])


@qtype("lin", [(3, 1), (5, 2), (2, 3), (4, 1)])
def _(p):
    a, b = p
    M = ((a, b), (b, a))
    ans = m(rf"{a - b}\text{{ et }}{a + b}")
    return (rf"Quelles sont les valeurs propres de $A={pmat(M)}$ ?",
            ans, [m(rf"{a}\text{{ et }}{b}"), m(rf"{-a - b}\text{{ et }}{b - a}"), m(rf"{a * a - b * b}\text{{ et }}{2 * a}"),
                  m(rf"{a}\text{{ (double)}}")])


@qtype("lin", [((1, 2, -1, 0), (2, 4, -2, 0), (0, 1, 1, 1)), ((1, 1, 1, 1), (2, 2, 2, 2), (3, 3, 3, 3)),
               ((1, 0, 2, 1), (0, 1, 1, 0), (1, 1, 3, 1)), ((1, 2, 0, 1), (0, 1, 1, 0), (0, 0, 1, 1))])
def _(M):
    r = rank(M)
    k = 4 - r
    return (rf"Soit $f:\mathbb{{R}}^4\to\mathbb{{R}}^3$ de matrice $A={pmat(M)}$. Quelle est la dimension de $\ker f$ ?",
            m(str(k)), [m(str(x)) for x in [0, 1, 2, 3, 4] if x != k][:3])


@qtype("lin", [((2, 1), (3, 2)), ((5, 3), (3, 2)), ((3, -1), (-5, 2)), ((4, 3), (1, 1))])
def _(M):
    (a, b), (c, d) = M
    assert a * d - b * c == 1
    inv = ((d, -b), (-c, a))
    return (rf"Soit $A={pmat(M)}$, de déterminant $1$. Que vaut $A^{{-1}}$ ?",
            m(pmat(inv)), [m(pmat(((a, -b), (-c, d)))), m(pmat(((d, b), (c, a)))), m(pmat(((-d, b), (c, -a)))), m(pmat(((d, -c), (-b, a)))), m(pmat(M))])


@qtype("lin", [(3, 10), (2, 7), (5, 4), (-2, 6)])
def _(p):
    a, n = p
    return (rf"Soit $A={pmat(((1, a), (0, 1)))}$. Quel est le coefficient en haut à droite de $A^{{{n}}}$ ?",
            m(str(n * a)), [m(str(a ** n)), m(str(a)), m(str(n + a)), m(str((n - 1) * a))])


@qtype("lin", [3, 4, 5, 6])
def _(n):
    return (rf"Quelle est la dimension de l'espace $\mathcal{{S}}_{{{n}}}(\mathbb{{R}})$ des matrices symétriques réelles de taille ${n}$ ?",
            m(str(n * (n + 1) // 2)), [m(str(n * n)), m(str(n * (n - 1) // 2)), m(str(2 * n)), m(str(n))])


@qtype("lin", [((1, 2, -1), (3, 1, 2)), ((2, -1, 3), (1, 4, 1)), ((1, 3, 2), (-2, 1, 5)), ((4, 1, -2), (1, 2, 3))])
def _(p):
    u, v = p
    # u = (u1,u2,lambda) ; v ; u.v = 0
    s = u[0] * v[0] + u[1] * v[1]
    lam = F(-s, v[2])
    return (rf"Pour quelle valeur de $\lambda$ les vecteurs $u=({u[0]},{u[1]},\lambda)$ et $v=({v[0]},{v[1]},{v[2]})$ sont-ils orthogonaux ?",
            m(lf(lam)), [m(lf(-lam)), m(lf(F(s, v[2] if v[2] != 1 else 2))), m(lf(lam + 1)), m(lf(lam * 2))])


# ============================================================ PROBABILITES
@qtype("prb", [(6, 2), (8, 3), (5, 2), (10, 4)])
def _(p):
    n, k = p
    v = F(comb(n, k), 2 ** n)
    return (rf"$X$ suit la loi binomiale $\mathcal{{B}}\left({n},\frac12\right)$. Que vaut $P(X={k})$ ?",
            m(lf(v)), [m(lf(F(1, 2 ** n))), m(lf(F(k, n))), m(lf(F(comb(n, k), 2 ** k))), m(lf(v * 2))])


@qtype("prb", [(20, F(1, 4)), (30, F(2, 5)), (12, F(1, 3)), (50, F(1, 5))])
def _(p):
    n, q = p
    return (rf"$X$ suit la loi binomiale $\mathcal{{B}}\left({n},{lf(q, False)}\right)$. Que vaut $V(X)$ ?",
            m(lf(n * q * (1 - q))), [m(lf(n * q)), m(lf(n * q * q)), m(lf(q * (1 - q))), m(lf(n * (1 - q)))])


@qtype("prb", [F(1, 6), F(2, 7), F(1, 4), F(3, 10)])
def _(q):
    return (rf"$X$ suit la loi géométrique de paramètre ${lf(q, False)}$ (à valeurs dans $\mathbb{{N}}^*$). Que vaut $E(X)$ ?",
            m(lf(1 / q)), [m(lf(q)), m(lf((1 - q) / q)), m(lf((1 - q) / q ** 2)), m(lf(1 / q + 1))])


@qtype("prb", [2, 3, 5, 4])
def _(lam):
    return (rf"$X$ suit la loi de Poisson de paramètre ${lam}$. Que vaut $P(X=1)$ ?",
            m(rf"{lam}e^{{-{lam}}}"), [m(rf"e^{{-{lam}}}"), m(rf"\dfrac{{{lam}}}{{e}}"), m(rf"1-e^{{-{lam}}}"), m(rf"{lam}e^{{{lam}}}")])


@qtype("prb", [(2, 3), (F(1, 2), 4), (3, 2), (F(1, 3), 6)])
def _(p):
    lam, t = p
    ex = F(lam) * t
    return (rf"$X$ suit la loi exponentielle de paramètre ${lf(lam, False)}$. Que vaut $P(X>{t})$ ?",
            m(rf"e^{{-{lf(ex, False)}}}"), [m(rf"1-e^{{-{lf(ex, False)}}}"), m(rf"e^{{{lf(ex, False)}}}"),
                                            m(rf"e^{{-{lf(F(t) / F(lam), False)}}}") if F(t) / F(lam) != ex else m(rf"{lf(lam, False)}e^{{-{lf(ex, False)}}}")])


@qtype("prb", [(F(1, 100), F(9, 10), F(1, 10)), (F(1, 50), F(4, 5), F(1, 20)),
               (F(1, 20), F(9, 10), F(1, 5)), (F(1, 10), F(3, 4), F(1, 4))])
def _(p):
    pm, s, f = p
    v = pm * s / (pm * s + (1 - pm) * f)
    return (rf"Une maladie touche une proportion ${lf(pm, False)}$ de la population. Un test est positif chez un malade avec probabilité ${lf(s, False)}$ et chez un non-malade avec probabilité ${lf(f, False)}$. Quelle est la probabilité d'être malade sachant que le test est positif ?",
            m(lf(v)), [m(lf(s)), m(lf(pm * s)), m(lf(1 - f)), m(lf(pm))])


@qtype("prb", [(0, 6), (2, 8), (-1, 5), (1, 7)])
def _(p):
    a, b = p
    return (rf"$X$ suit la loi uniforme sur $[{a},{b}]$. Que vaut $V(X)$ ?",
            m(lf(F((b - a) ** 2, 12))), [m(lf(F(b - a, 12))), m(lf(F((b - a) ** 2, 4))), m(lf(F(a + b, 2))), m(lf(F((b - a) ** 2, 6)))])


@qtype("prb", [(3, -2, 5), (-2, 7, 4), (4, 1, 3), (-3, 5, 2)])
def _(p):
    a, b, s = p
    return (rf"$X$ suit la loi normale $\mathcal{{N}}(10,{s}^2)$ et $Y={a}X{'+' if b > 0 else '-'}{abs(b)}$. Que vaut $V(Y)$ ?",
            m(str(a * a * s * s)), [m(str(a * s * s)), m(str(a * a * s * s + b)), m(str(a * a * s)), m(str(abs(a) * s))])


@qtype("prb", ["ANANAS", "PAPAYE", "BANANE", "MAMMOUTH"])
def _(w):
    from collections import Counter
    c = Counter(w)
    v = factorial(len(w))
    for k in c.values():
        v //= factorial(k)
    return (rf"Combien d'anagrammes (avec ou sans signification) peut-on former avec les lettres du mot \textsf{{{w}}} ?",
            m(str(v)), [m(str(factorial(len(w)))), m(str(v * 2)), m(str(v // 2 if v % 2 == 0 else v + 10)), m(str(len(w) ** 2))])


@qtype("prb", [(4, 5), (9, 6), (2, 4), (12, 8)])
def _(p):
    V, a = p
    return (rf"Une variable $X$ a pour variance ${V}$. D'après l'inégalité de Bienaymé-Tchebychev, $P\left(|X-E(X)|\geq {a}\right)$ est majorée par :",
            m(lf(F(V, a * a))), [m(lf(F(V, a))), m(lf(F(a * a, V)) if F(a * a, V) != F(V, a * a) else lf(F(1, a))),
                                 m(lf(F(1, a * a))), m(lf(1 - F(V, a * a)))])


# ============================================================ GEOMETRIE / COMPLEXES
@qtype("geo", [((3, 4), 3), ((5, 12), 2), ((1, 1), 6), ((6, 8), 2)])
def _(p):
    (a, b), n = p
    mod2 = a * a + b * b
    r = int(round(mod2 ** .5))
    if r * r == mod2:
        ans = str(r ** n)
        dis = [str(mod2 ** n), str((a + b) ** n), str(r * n)]
    else:
        ans = str(mod2 ** (n // 2)) if n % 2 == 0 else f"{mod2 ** (n // 2)}\\sqrt{{{mod2}}}"
        dis = [str(mod2 ** n), str((a + b) ** n), str(2 * n)]
    return (rf"Que vaut le module de $({a}+{'' if b == 1 else b}i)^{{{n}}}$ ?", m(ans), [m(x) for x in dis])


@qtype("geo", [4, 5, 7, 8])
def _(n):
    a = F(n, 3)
    return (rf"Quel est l'argument principal (dans $]-\pi,\pi]$) de $\left(1+i\sqrt3\right)^{{{n}}}$ ?",
            m(angle(a)), [m(angle(F(n, 6))), m(angle(a + F(1, 3))), m(angle(-a)), m(angle(F(n, 3) + 1))])


@qtype("geo", [3, 4, 5, 6])
def _(n):
    v = (-1) ** (n + 1)
    return (rf"Que vaut le produit des racines ${n}$-ièmes de l'unité ?",
            m(str(v)), [m(str(-v)), m("0"), m(str(n)), m("i")])


@qtype("geo", [((1, 2, 2), 3, (1, 1, 1)), ((2, -1, 2), 1, (3, 0, 1)), ((1, -2, 2), 4, (2, 1, 3)), ((2, 3, 6), 7, (1, 1, 1))])
def _(p):
    (a, b, c), d, (x, y, z) = p
    nn = a * a + b * b + c * c
    num = abs(a * x + b * y + c * z - d)
    plane = f"{a}x" + "".join(f"{'+' if v > 0 else '-'}{'' if abs(v) == 1 else abs(v)}{s}" for v, s in [(b, 'y'), (c, 'z')]) + f"={d}"
    plane = plane.replace("1x", "x") if a == 1 else plane
    ans = frac_sq(num, nn)
    return (rf"Quelle est la distance du point $A({x},{y},{z})$ au plan $\mathcal{{P}} : {plane}$ ?",
            m(ans), [m(frac_sq(num + 1, nn)), m(str(num)), m(frac_sq(num, nn * 4) if num else "1"), m(lf(F(num, nn)) if nn != num else "2")])


@qtype("geo", [((3, 4, -5), (2, 1)), ((4, -3, 2), (1, 3)), ((5, 12, -1), (1, 1)), ((6, 8, 5), (-1, 2))])
def _(p):
    (a, b, c), (x, y) = p
    nn = a * a + b * b
    num = abs(a * x + b * y + c)
    line = f"{a}x" + f"{'+' if b > 0 else '-'}{abs(b)}y" + f"{'+' if c > 0 else '-'}{abs(c)}=0"
    return (rf"Dans le plan, quelle est la distance du point $A({x},{y})$ à la droite $D : {line}$ ?",
            m(frac_sq(num, nn)), [m(str(num)), m(lf(F(num, nn))), m(frac_sq(num + 2, nn)), m(frac_sq(num, nn) + "+1")])


@qtype("geo", [((1, 2, 0), (0, 1, 3)), ((2, 0, 1), (1, 1, 0)), ((1, -1, 2), (3, 0, 1)), ((0, 2, 1), (1, 0, -1))])
def _(p):
    u, v = p
    w = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    T = lambda t: f"({t[0]},{t[1]},{t[2]})"
    return (rf"Que vaut le produit vectoriel $u\wedge v$ pour $u={T(u)}$ et $v={T(v)}$ ?",
            m(T(w)), [m(T(tuple(-x for x in w))), m(T((u[0] * v[0], u[1] * v[1], u[2] * v[2]))), m(T((w[0], -w[1], w[2])) if w[1] else T((w[0] + 1, w[1], w[2])))])


@qtype("geo", [((0, 0), (4, 1), (1, 3)), ((1, 1), (5, 2), (2, 6)), ((-1, 0), (3, 2), (0, 4)), ((2, -1), (6, 1), (3, 4))])
def _(p):
    (x1, y1), (x2, y2), (x3, y3) = p
    A = F(abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)), 2)
    return (rf"Quelle est l'aire du triangle de sommets $A({x1},{y1})$, $B({x2},{y2})$ et $C({x3},{y3})$ ?",
            m(lf(A)), [m(lf(2 * A)), m(lf(A + 1)), m(lf(A / 2)), m(lf(A + F(1, 2)))])


@qtype("geo", [("2i", 2, F(1, 2)), ("1+i", None, F(1, 4)), ("-3", 3, F(1)), ("1-i\\sqrt3", 2, F(-1, 3))])
def _(p):
    a, r, th = p
    rs = r"\sqrt2" if r is None else str(r)
    return (rf"Quels sont le rapport et l'angle de la similitude directe $z\mapsto ({a})z+1$ ?",
            m(rf"{rs}\text{{ et }}{angle(th)}"),
            [m(rf"{rs}\text{{ et }}{angle(-th)}") if th != 1 else m(rf"{rs}\text{{ et }}0"),
             m(rf"{'2' if r is None else r * r}\text{{ et }}{angle(th)}"),
             m(rf"1\text{{ et }}{angle(th)}")])


@qtype("geo", [F(1, 6), F(1, 4), F(1, 3), F(1, 5)])
def _(t):
    return (rf"Deux droites sécantes en $O$ forment un angle de ${angle(t)}$. La composée des réflexions d'axes ces deux droites est :",
            rf"la rotation de centre $O$ et d'angle ${angle(2 * t)}$",
            [rf"la rotation de centre $O$ et d'angle ${angle(t)}$", rf"la rotation de centre $O$ et d'angle ${angle(t / 2)}$",
             r"une translation"])


@qtype("geo", [(2, 3, 4), (1, -2, -4), (3, 1, 6), (-2, 2, -1)])
def _(p):
    a, b, c = p
    r2 = a * a + b * b - c
    t = lambda v, s: (f"+{2 * abs(v)}{s}" if v < 0 else f"-{2 * v}{s}")
    eq = f"x^2+y^2{t(a, 'x')}{t(b, 'y')}" + (f"+{c}" if c > 0 else f"-{-c}") + "=0"
    return (rf"Quel est le rayon du cercle d'équation ${eq}$ ?",
            m(sq(r2)), [m(str(r2)), m(sq(a * a + b * b + c) if a * a + b * b + c > 0 else "1"), m(sq(r2 + 2)), m(str(abs(c)))])



# ---------- séries C et D : 4 jeux de valeurs de plus par type (idx 4-7) ----------
EXTRA = [
    # analyse
    [4, -2, -3, 6],
    [(4, 1), (-3, 2), (5, 3), (2, 5)],
    [5, 6, 7, 8],
    [F(1, 2), F(2, 3), F(1, 5), F(3, 5)],
    [5, 6, 7, 8],
    [(4, 3), (7, 2), (3, 5), (5, 6)],
    [6, 7, 8, 10],
    [(F(1, 5), 4), (F(3, 4), 2), (F(2, 5), 3), (F(1, 6), 5)],
    [(6, 2), (7, 1), (3, 3), (8, 2)],
    [(3, 4), (-2, 3), (4, 5), (5, 2)],
    # algèbre et arithmétique
    [(1260, 1617), (2024, 1288), (918, 1530), (1001, 1573)],
    [(3, 100, 7), (2, 60, 11), (4, 45, 13), (5, 30, 9)],
    [600, 840, 2016, 450],
    [(3, 2026), (7, 2027), (8, 2025), (9, 2026)],
    [(2, -3), (-4, 5), (5, 6), (-7, 2)],
    [60, 72, 90, 50],
    [(3, 11), (5, 23), (7, 19), (8, 21)],
    [(4, 2), (6, 3), (9, 2), (7, 3)],
    [8, 25, 30, 9],
    [7, 8, 9, 10],
    # algèbre linéaire
    [((4, 3), (2, 5)), ((6, -1), (3, 2)), ((-2, 5), (1, 3)), ((7, 2), (4, 1))],
    [((2, 0, 1), (1, 3, 0), (0, 1, 2)), ((1, 1, 2), (0, 2, 1), (3, 0, 1)),
     ((2, 1, 0), (1, 2, 1), (0, 1, 2)), ((1, 0, 3), (2, 1, 0), (0, 4, 1))],
    [((2, 3), (1, -1)), ((3, 2), (-1, 4)), ((1, -2), (4, 0)), ((5, 1), (2, -3))],
    [((2, 4, 6), (1, 2, 3), (3, 6, 9)), ((1, 2, 3), (0, 1, 4), (1, 3, 7)),
     ((1, 0, 0), (0, 2, 0), (0, 0, 3)), ((1, 2, 0), (2, 1, 0), (3, 3, 0))],
    [(4, 2), (6, 1), (3, 2), (5, 3)],
    [((1, 2, 3, 4), (2, 4, 6, 8), (1, 0, 1, 0)), ((1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)),
     ((2, 2, 2, 2), (1, 1, 1, 1), (0, 0, 0, 0)), ((1, 1, 0, 0), (0, 0, 1, 1), (1, 1, 1, 1))],
    [((3, 2), (4, 3)), ((2, 3), (1, 2)), ((5, 2), (2, 1)), ((7, 3), (2, 1))],
    [(4, 5), (2, 9), (-3, 4), (5, 6)],
    [2, 7, 8, 10],
    [((2, 1, 0), (1, 3, 2)), ((3, -2, 0), (2, 1, 4)), ((1, 4, 0), (-3, 2, 1)), ((2, 2, 0), (1, -3, 2))],
    # probabilités
    [(7, 2), (9, 3), (6, 4), (8, 5)],
    [(40, F(1, 4)), (25, F(1, 5)), (18, F(2, 3)), (60, F(1, 3))],
    [F(1, 5), F(1, 3), F(2, 5), F(1, 8)],
    [6, 7, 8, 10],
    [(4, 2), (F(1, 4), 8), (5, 1), (F(2, 3), 3)],
    [(F(1, 25), F(9, 10), F(1, 10)), (F(1, 5), F(4, 5), F(1, 10)), (F(1, 10), F(9, 10), F(1, 5)), (F(1, 40), F(4, 5), F(1, 20))],
    [(0, 12), (3, 9), (1, 4), (2, 12)],
    [(2, 3, 4), (-5, 1, 2), (3, -4, 3), (-2, -6, 5)],
    ["COCOTIER", "TORTUE", "BALEINE", "CAILLOU"],
    [(3, 2), (6, 4), (5, 3), (16, 5)],
    # géométrie et complexes
    [((8, 15), 2), ((1, 2), 4), ((2, 1), 3), ((7, 24), 2)],
    [2, 10, 11, 13],
    [7, 8, 9, 10],
    [((2, 2, 1), 5, (1, 2, 3)), ((1, 4, 8), 3, (2, 0, 1)), ((1, 1, 1), 2, (3, 1, -1)), ((2, -2, 1), 4, (3, 1, 2))],
    [((3, -4, 2), (1, 3)), ((5, -12, 3), (2, 1)), ((2, 1, -3), (4, 2)), ((8, 6, -5), (1, 2))],
    [((1, 0, 2), (2, 1, 0)), ((2, 1, -1), (0, 3, 1)), ((3, 1, 0), (1, 2, 1)), ((1, 2, 3), (3, 2, 1))],
    [((0, 0), (6, 0), (2, 5)), ((1, 2), (4, 6), (-2, 5)), ((2, 0), (5, 4), (0, 3)), ((-1, -1), (3, 1), (1, 5))],
    [("3i", 3, F(1, 2)), ("1+i\\sqrt3", 2, F(1, 3)), ("-2i", 2, F(-1, 2)), ("\\sqrt3+i", 2, F(1, 6))],
    [F(1, 8), F(1, 12), F(2, 5), F(3, 8)],
    [(4, 3, 9), (2, -5, 4), (3, 4, -11), (1, 1, -7)],
]
assert len(EXTRA) == len(TYPES) == 50 and all(len(e) == 4 for e in EXTRA)
for i, (th, fn, params) in enumerate(TYPES):
    TYPES[i] = (th, fn, list(params) + EXTRA[i])
    assert len(set(map(repr, TYPES[i][2]))) == 8, (i, TYPES[i][2])

# ============================================================ BUILD
THEMES = {"ana": ("Analyse", "1F6FA8"), "alg": ("Algèbre et arithmétique", "6A4C93"),
          "lin": ("Algèbre linéaire", "2E7D6B"), "prb": ("Probabilités et statistiques", "C77F0A"),
          "geo": ("Géométrie et complexes", "C0503A")}
ORDER = ["ana", "alg", "lin", "prb", "geo"]

Q = {}
for th in ORDER:
    types = [t for t in TYPES if t[0] == th]
    assert len(types) == 10, (th, len(types))
for ti, th in enumerate(ORDER):
    types = [t for t in TYPES if t[0] == th]
    for k, (_, fn, params) in enumerate(types):
        assert len(params) == 8
        for j in range(2):
            nA = ti * 20 + k * 2 + j + 1
            for serie, idx, n in ((L_, 2 * si + j, nA + si * 100) for si, L_ in enumerate("ABCD")):
                st, ans, dis = fn(params[idx])
                opts = [ans]
                for d in dis:
                    if d not in opts:
                        opts.append(d)
                    if len(opts) == 4:
                        break
                if len(opts) < 4:
                    import re
                    mm = re.fullmatch(r"\$(-?\d+)\$", ans)
                    if mm:
                        for dlt in (1, -1, 2, -2, 3):
                            c = m(str(int(mm.group(1)) + dlt))
                            if c not in opts:
                                opts.append(c)
                            if len(opts) == 4:
                                break
                assert len(opts) == 4, (n, ans, dis)
                Q[n] = (th, serie, st, opts)

# distinct A/B statements for twins
for n in range(1, 101):
    assert len({Q[n + si * 100][2] for si in range(4)}) == 4, n

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
    rng = random.Random(n * 7 + 3)
    perm = [0, 1, 2, 3]
    rng.shuffle(perm)
    shown = [opts[i] for i in perm]
    good = "abcd"[perm.index(0)]
    KEY.append([n, th, good, opts[0]])
    lab = THEMES[th][0]
    num = n if n <= 100 else f"{(n - 1) % 100 + 1} {'ABCD'[(n - 1) // 100]}"
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
open(f"{OUT}/capes.tex", "w", encoding="utf-8").write("\n".join(tex))
json.dump([[n, th, g] for n, th, g, _ in KEY], open(f"{OUT}/questions.json", "w"))
with open(f"{OUT}/corrige.txt", "w", encoding="utf-8") as f:
    for n, th, g, a in KEY:
        f.write(f"Q{n if n <= 100 else str((n - 1) % 100 + 1) + ' ' + 'ABCD'[(n - 1) // 100]} ({THEMES[th][0]}) : {g}) {a}\n")
print(len(KEY), "questions")
