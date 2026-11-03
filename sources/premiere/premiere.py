"""Banque Mathématiques 1ère (spécialité, programme 2019) :
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


def sqs(n):
    a, b = 1, n
    f = 2
    while f * f <= b:
        while b % (f * f) == 0:
            b //= f * f; a *= f
        f += 1
    return str(a) if b == 1 else (str(a) if a > 1 else "") + rf"\sqrt{{{b}}}"


def lin(k, a, v="x"):
    return expr([(k, v), (a, "")])


# ============================================================ SUITES
@qtype("sui", "Suite arithmétique : uₙ = u₀ + n × r.",
       [(3, 2, 10), (5, -3, 8), (-4, 5, 12), (7, 4, 15), (2, -4, 9), (-6, 3, 11), (10, -2, 7), (4, 6, 13)])
def _(p):
    a, r, k = p
    return (rf"$(u_n)$ est la suite arithmétique de premier terme $u_0={a}$ et de raison ${r}$. Que vaut $u_{{{k}}}$ ?",
            m(nb(a + k * r)), [m(nb(a + (k - 1) * r)), m(nb(a + (k + 1) * r)), m(nb(k * r)), m(nb(a * r ** 2))])


@qtype("sui", "Suite géométrique : uₙ = u₀ × qⁿ.",
       [(3, 2, 4), (5, 3, 3), (2, -2, 5), (1, 4, 4), (64, F(1, 2), 3), (-3, 2, 5), (81, F(1, 3), 4), (6, -2, 3)])
def _(p):
    a, q, k = p
    q = F(q)
    return (rf"$(u_n)$ est la suite géométrique de premier terme $u_0={a}$ et de raison ${lf(q)}$. Que vaut $u_{{{k}}}$ ?",
            m(lf(a * q ** k)), [m(lf(a + k * q)), m(lf(a * q ** (k - 1))), m(lf(a * q ** (k + 1))), m(lf(a * k * q))])


@qtype("sui", "Calcule les termes un par un : u₁ à partir de u₀, puis u₂ à partir de u₁.",
       [(2, 1, 3), (3, -2, 2), (F(1, 2), 4, 12), (-2, 3, 2), (4, -5, 2), (2, -3, 5), (1, 6, -4), (-1, 10, 3)])
def _(p):
    a, b, u0 = p
    a = F(a)
    u1 = a * u0 + b; u2 = a * u1 + b; u3 = a * u2 + b
    return (rf"On définit $u_0={u0}$ et, pour tout entier $n$, $u_{{n+1}}={expr([(a, 'u_n'), (b, '')])}$. Que vaut $u_2$ ?",
            m(lf(u2)), [m(lf(u1)), m(lf(u3)), m(lf(a * u0 + 2 * b)), m(lf(u2 + 1))])


@qtype("sui", "1 + 2 + … + n = n(n + 1) ÷ 2.",
       [10, 20, 50, 100, 15, 30, 40, 12])
def _(n):
    return (rf"Que vaut la somme $1+2+3+\dots+{n}$ ?", m(nb(n * (n + 1) // 2)), [m(nb(n * n)), m(nb(n * (n - 1) // 2)), m(nb(n * (n + 1)))])


@qtype("sui", "Pour une suite arithmétique, u_p − u_k = (p − k) × r.",
       [((3, 7), (8, 22)), ((2, 10), (6, -2)), ((1, 4), (5, 14)), ((0, -3), (4, 13)), ((5, 20), (10, 10)), ((3, 1), (9, 19)), ((4, 9), (6, 12)), ((1, 0), (6, -15))])
def _(p):
    (i, ui), (j, uj) = p
    r = F(uj - ui, j - i)
    return (rf"$(u_n)$ est une suite arithmétique avec $u_{{{i}}}={ui}$ et $u_{{{j}}}={uj}$. Quelle est sa raison ?",
            m(lf(r)), [m(lf(F(uj - ui, j + i)) if j + i else lf(r + 1)), m(nb(uj - ui)), m(lf(-r)), m(lf(F(j - i, uj - ui)))])


@qtype("sui", "1 + q + q² + … + qⁿ = (qⁿ⁺¹ − 1) ÷ (q − 1).",
       [(2, 6), (3, 4), (2, 9), (5, 3), (4, 4), (3, 5), (10, 4), (2, 4)])
def _(p):
    q, n = p
    return (rf"Que vaut la somme $1+{q}+{q}^2+\dots+{q}^{{{n}}}$ ?",
            m(nb((q ** (n + 1) - 1) // (q - 1))), [m(nb(q ** (n + 1))), m(nb((q ** n - 1) // (q - 1))), m(nb(q ** (n + 1) - 1)), m(nb(q ** n))])


@qtype("sui", "Arithmétique : le signe de la raison ; géométrique de premier terme positif : q > 1 croissante, 0 < q < 1 décroissante.",
       [(r"u_n=5-3n", "décroissante"), (r"u_n=2n+7", "croissante"), (r"u_n=3\times2^n", "croissante"), (r"u_n=4\times0{,}5^n", "décroissante"),
        (r"u_n=-2\times3^n", "décroissante"), (r"u_n=n^2+1", "croissante"), (r"u_n=\dfrac{1}{n+1}", "décroissante"), (r"u_n=7", "constante")])
def _(p):
    f, nat = p
    return (rf"Quel est le sens de variation de la suite définie pour tout entier naturel $n$ par ${f}$ ?", nat,
            [x for x in ["croissante", "décroissante", "constante"] if x != nat] + ["ni croissante ni décroissante"])


@qtype("sui", "Remplace n par sa valeur dans la formule explicite.",
       [(1, -3, 2, 5), (2, 1, -4, 3), (-1, 6, 0, 4), (3, -2, 1, 2), (1, 0, -10, 6), (2, -5, 3, 4), (-2, 3, 7, 3), (1, 4, -1, 2)])
def _(p):
    a, b, c, k = p
    U = lambda n: a * n * n + b * n + c
    return (rf"Pour tout entier naturel $n$, $u_n={expr([(a, 'n^2'), (b, 'n'), (c, '')])}$. Que vaut $u_{{{k}}}$ ?",
            m(nb(U(k))), [m(nb(U(k + 1))), m(nb(U(k - 1))), m(nb(-U(k)) if U(k) else "1"), m(nb(a * 2 * k + b * k + c))])


# ============================================================ SECOND DEGRÉ
def tri(a, b, c):
    return expr([(a, "x^2"), (b, "x"), (c, "")])


@qtype("deg", "Δ = b² − 4ac.",
       [(1, -5, 6), (2, 3, -2), (1, 4, 4), (3, -2, 5), (-1, 6, -9), (2, -7, 3), (1, 1, 1), (4, -4, -3)])
def _(p):
    a, b, c = p
    d = b * b - 4 * a * c
    return (rf"Quel est le discriminant du trinôme ${tri(a, b, c)}$ ?", m(nb(d)), [m(nb(b * b + 4 * a * c)), m(nb(b - 4 * a * c)), m(nb(-d)) if d else m("1"), m(nb(d + 2))])


@qtype("deg", "Δ > 0 : deux racines ; Δ = 0 : une racine double ; Δ < 0 : aucune racine réelle.",
       [(1, 2, 5), (1, -6, 9), (2, 5, 1), (-3, 2, 4), (4, 4, 1), (1, 0, 3), (5, -1, -2), (2, -8, 8)])
def _(p):
    a, b, c = p
    d = b * b - 4 * a * c
    n = "2" if d > 0 else "1" if d == 0 else "0"
    return (rf"Combien de racines réelles le trinôme ${tri(a, b, c)}$ possède-t-il ?", m(n), [m(x) for x in "012" if x != n] + ["une infinité"])


def S2(a, b):
    a, b = sorted((a, b))
    return m(r"\{" + (nb(a) if a == b else rf"{nb(a)}\,;\,{nb(b)}") + r"\}")


@qtype("deg", "Calcule Δ, puis x = (−b ± √Δ) ÷ (2a).",
       [(1, 2, 3), (1, -1, 4), (2, 1, -3), (1, -5, -2), (-1, 2, 6), (3, 1, 2), (1, -4, 4), (1, 0, 7)])
def _(p):
    a, r1, r2 = p
    b, c = -a * (r1 + r2), a * r1 * r2
    return (rf"Quelles sont les racines du trinôme ${tri(a, b, c)}$ ?", S2(r1, r2), [S2(-r1, -r2), S2(r1, -r2) if r1 != -r2 else S2(r1 + 1, r2), S2(r1 + r2, r1 * r2) if {r1 + r2, r1 * r2} != {r1, r2} else S2(r1 - 1, r2 + 1), S2(r1 + 1, r2 + 1), S2(2 * r1, 2 * r2)])


@qtype("deg", "x² + bx + c = (x + b/2)² + c − b²/4.",
       [(6, 5), (-4, 1), (2, -3), (-10, 30), (8, 10), (-6, 2), (4, 9), (-2, -8)])
def _(p):
    b, c = p
    h, k = F(b, 2), c - F(b * b, 4)
    C = lambda hh, kk: m(f"({lin(1, hh)})^2" + (("+" if kk > 0 else "-") + nb(abs(kk)) if kk else ""))
    return (rf"Quelle est la forme canonique de ${tri(1, b, c)}$ ?", C(h, k), [C(-h, k), C(h, F(c)), C(F(b), k), C(h, -k) if k else C(h, 1)])


@qtype("deg", "Le sommet de la parabole a pour abscisse α = −b ÷ (2a) et pour ordonnée β = f(α).",
       [(1, -4, 1), (2, 8, 3), (-1, 6, -5), (1, 2, -8), (3, -12, 7), (-2, 4, 1), (1, -6, 10), (4, 8, -1)])
def _(p):
    a, b, c = p
    al = F(-b, 2 * a); be = a * al * al + b * al + c
    return (rf"Quelles sont les coordonnées du sommet de la parabole d'équation $y={tri(a, b, c)}$ ?",
            m(pt((al, be))), [m(pt((-al, be))), m(pt((al, -be))) if be else m(pt((al, 1))), m(pt((al, F(c)))) if c != be else m(pt((al, c + 1)))])


def iv(lo, hi, lc, hc):
    L = "[" if (lc and lo is not None) else "]"
    R = "]" if (hc and hi is not None) else "["
    a = r"-\infty" if lo is None else nb(lo)
    b = r"+\infty" if hi is None else nb(hi)
    return rf"{L}{a}\,;\,{b}{R}"


def ivs(lo, hi, lc, hc):
    return iv(lo, hi, lc, hc)


@qtype("deg", "Un trinôme est du signe de a à l'extérieur des racines et du signe contraire entre les racines.",
       [(1, -2, 2, "<"), (1, 1, 5, ">"), (-1, 0, 3, ">"), (2, -3, 1, "<="), (1, -1, 4, ">="), (-2, -5, -1, "<"), (1, 2, 6, "<"), (-1, -4, 4, ">=")])
def _(p):
    a, r1, r2, op = p
    b, c = -a * (r1 + r2), a * r1 * r2
    want_pos = op in (">", ">=")
    strict = op in ("<", ">")
    inside = (want_pos and a < 0) or (not want_pos and a > 0)
    IN = m(iv(r1, r2, not strict, not strict))
    OUT = m(iv(None, r1, False, not strict) + r"\cup" + iv(r2, None, not strict, False))
    IN2 = m(iv(r1, r2, strict, strict))
    OUT2 = m(iv(None, r1, False, strict) + r"\cup" + iv(r2, None, strict, False))
    sym = {"<": "<", ">": ">", "<=": r"\leqslant", ">=": r"\geqslant"}[op]
    ans, dis = (IN, [OUT, IN2, OUT2]) if inside else (OUT, [IN, OUT2, IN2])
    return (rf"Quel est l'ensemble des solutions de l'inéquation ${tri(a, b, c)}{sym}0$ ?", ans, dis)


@qtype("deg", "Si le trinôme ax² + bx + c a deux racines, leur somme vaut −b/a et leur produit c/a.",
       [(1, -7, 10, "S"), (2, -6, 3, "P"), (1, 4, -5, "S"), (3, -9, 2, "P"), (1, -1, -12, "P"), (2, 5, -3, "S"), (1, 10, 9, "P"), (5, -20, 1, "S")])
def _(p):
    a, b, c, w = p
    S, P = F(-b, a), F(c, a)
    r, alt = (S, P) if w == "S" else (P, S)
    return (rf"Le trinôme ${tri(a, b, c)}$ a deux racines. Que vaut leur {'somme' if w == 'S' else 'produit'} ?",
            m(lf(r)), [m(lf(-r)), m(lf(alt)) if alt != r else m(lf(r + 1)), m(lf(F(b, a))) if F(b, a) != r else m(lf(F(c))), m(lf(F(c) if w == "P" else F(-b)) if (F(c) if w == "P" else F(-b)) != r else lf(r * 2))])


@qtype("deg", "Si x₁ et x₂ sont les racines, ax² + bx + c = a(x − x₁)(x − x₂).",
       [(2, -2, 3), (1, 1, 4), (3, -1, 2), (-1, 0, 5), (1, -3, -6), (2, 1, 3), (-2, -4, 1), (1, -7, 7)])
def _(p):
    a, r1, r2 = p
    b, c = -a * (r1 + r2), a * r1 * r2
    K = "" if a == 1 else "-" if a == -1 else str(a)
    fac = lambda x1, x2, k: k + (f"x({lin(1, -x2)})" if x1 == 0 else f"({lin(1, -x1)})({lin(1, -x2)})")
    return (rf"Le trinôme ${tri(a, b, c)}$ a pour racines ${nb(r1)}$ et ${nb(r2)}$. Quelle est sa forme factorisée ?",
            m(fac(r1, r2, K)), [m(fac(-r1, -r2, K)) if (r1, r2) != (-r1, -r2) else m(fac(r1, r2 + 1, K)), m(fac(r1, r2, "")) if K else m(fac(r1, r2, "2")), m(fac(r1, r2, "-" if a > 0 else "")), m(fac(-r1, r2, K)) if r1 else m(fac(r1, -r2, K)), m(fac(r1, -r2, K)), m(fac(r1, r2 + 1, K)), m(fac(r1, r2, "2"))])


# ============================================================ DÉRIVATION
@qtype("der", "(xⁿ)' = n xⁿ⁻¹ : dérive terme à terme, puis remplace x.",
       [(1, -2, 3, 5, 2), (2, 0, -5, 1, 1), (-1, 3, 0, 4, 3), (1, 1, 1, 1, -1), (3, -4, 2, 0, 0), (1, 0, -12, 4, 2), (-2, 1, 5, -3, 2), (1, -6, 9, 0, -1)])
def _(p):
    a, b, c, d, x = p
    f = expr([(a, "x^3"), (b, "x^2"), (c, "x"), (d, "")])
    v = 3 * a * x * x + 2 * b * x + c
    return (rf"Soit $f(x)={f}$. Que vaut $f'({nb(x)})$ ?", m(nb(v)),
            [m(nb(a * x ** 3 + b * x * x + c * x + d)), m(nb(3 * a * x * x + b * x + c)), m(nb(a * x * x + b * x + c)), m(nb(v + 1))])


@qtype("der", "Tangente en a : y = f'(a)(x − a) + f(a).",
       [(1, -2, 3, 1), (2, 1, 0, -1), (1, 0, -4, 2), (-1, 4, 1, 1), (3, -6, 2, 2), (1, 3, -1, 0), (-2, 0, 5, 1), (1, -5, 6, 4)])
def _(p):
    a, b, c, x0 = p
    fa, d = a * x0 * x0 + b * x0 + c, 2 * a * x0 + b
    Y = lambda k, q: m("y=" + expr([(k, "x"), (q, "")]))
    return (rf"Quelle est l'équation de la tangente à la courbe de $f(x)={tri(a, b, c)}$ au point d'abscisse ${nb(x0)}$ ?",
            Y(d, fa - d * x0), [Y(d, fa), Y(fa, d - fa * x0) if (fa, d - fa * x0) != (d, fa - d * x0) else Y(d, fa - d * x0 + 1), Y(d, fa + d * x0) if d * x0 else Y(d, fa + 1), Y(fa, 0) if fa else Y(1, 0), Y(d, -fa) if fa else Y(d, 2)])


@qtype("der", "(uv)' = u'v + uv'.",
       [(2, 1, 3, -1, 1), (1, -3, 2, 5, 0), (-1, 2, 4, 1, 2), (3, 0, 1, -2, 1), (2, -1, -1, 3, -1), (1, 4, 1, 4, -2), (5, 1, 2, 0, 1), (-2, 3, 3, 1, 0)])
def _(p):
    a, b, c, d, x = p
    v = a * (c * x + d) + c * (a * x + b)
    return (rf"Soit $f(x)=({lin(a, b)})({lin(c, d)})$. Que vaut $f'({nb(x)})$ ?", m(nb(v)),
            [m(nb(a * c)), m(nb((a * x + b) * (c * x + d))), m(nb(a * (c * x + d))), m(nb(v + 2))])


@qtype("der", "(1/x)' = −1/x², donc (k/x)' = −k/x².",
       [(3, 1), (2, -1), (5, 2), (-4, 2), (6, 3), (1, F(1, 2)), (8, 4), (-2, 1)])
def _(p):
    k, x = p
    x = F(x)
    return (rf"Soit $f(x)=\dfrac{{{k}}}{{x}}$ sur $\mathbb{{R}}^*$. Que vaut $f'({lf(x)})$ ?", m(lf(-k / (x * x))),
            [m(lf(k / (x * x))), m(lf(-k / x)), m(lf(k * x)) if k * x != -k / (x * x) else m(lf(k)), m(lf(-k / (2 * x)))])


@qtype("der", "(√x)' = 1 ÷ (2√x).",
       [4, 9, 16, 1, 25, 36, 64, 100])
def _(x):
    r = int(x ** .5)
    return (rf"Soit $f(x)=\sqrt{{x}}$. Que vaut $f'({x})$ ?", m(lf(F(1, 2 * r))), [m(lf(F(1, r))), m(nb(2 * r)), m(lf(F(r, 2))), m(lf(F(1, 4 * r))), m(lf(F(-1, 2 * r)))])


@qtype("der", "(u e^x)' = u' e^x + u e^x, et e⁰ = 1.",
       [(2, 3), (1, -4), (-3, 1), (4, 0), (1, 1), (-2, 5), (3, -1), (5, 2)])
def _(p):
    a, b = p
    return (rf"Soit $f(x)=({lin(a, b)})e^x$. Que vaut $f'(0)$ ?", m(nb(a + b)),
            [m(nb(a)), m(nb(b)) if b != a + b else m(nb(a * b + 1)), m(nb(a * b)) if a * b != a + b else m(nb(a - b)), m(nb(a + b + 1))])


@qtype("der", "f est décroissante là où f'(x) ≤ 0 : étudie le signe de f'.",
       [(2, -6), (-3, 6), (4, 8), (-1, -5), (5, -10), (-2, 1), (3, 9), (-4, -12)])
def _(p):
    a, b = p
    r = F(-b, a)
    L, R = m(iv(None, r, False, True)), m(iv(r, None, True, False))
    L2, R2 = m(iv(None, -r, False, True)), m(iv(-r, None, True, False))
    ans, other = (L, R) if a > 0 else (R, L)
    return (rf"La fonction $f$ est dérivable sur $\mathbb{{R}}$ et $f'(x)={lin(a, b)}$. Sur quel intervalle $f$ est-elle décroissante ?",
            ans, [other, L2 if ans == L else R2, R2 if ans == L else L2] if r else [other, m(iv(None, 1, False, True)), m(iv(1, None, True, False))])


@qtype("der", "Le trinôme ax² + bx + c atteint son extremum en x = −b ÷ (2a) : un minimum si a > 0, un maximum si a < 0.",
       [(1, -4, 1), (-1, 6, -5), (2, 8, 3), (-2, 4, 1), (1, 2, -8), (-1, -4, 3), (3, -6, 5), (1, -10, 20)])
def _(p):
    a, b, c = p
    al = F(-b, 2 * a); be = a * al * al + b * al + c
    w = "minimum" if a > 0 else "maximum"
    return (rf"Soit $f(x)={tri(a, b, c)}$. Quel est le {w} de $f$ sur $\mathbb{{R}}$ ?", m(lf(be)),
            [m(lf(F(c))) if c != be else m(lf(be + 1)), m(lf(al)) if al != be else m(lf(-al + 1)), m(lf(-be)) if be else m("1"), m(lf(be + 2))])


# ============================================================ TRIGONOMÉTRIE ET EXPONENTIELLE
def ang(t, reduce=False):
    t = F(t)
    if reduce:
        while t <= -1:
            t += 2
        while t > 1:
            t -= 2
    if t == 0:
        return "0"
    s = "-" if t < 0 else ""
    t = abs(t)
    if t.denominator == 1:
        return s + (r"\pi" if t == 1 else f"{t.numerator}\\pi")
    num = "" if t.numerator == 1 else str(t.numerator)
    return rf"{s}\dfrac{{{num}\pi}}{{{t.denominator}}}"


COS = {F(0): "1", F(1, 6): r"\dfrac{\sqrt3}{2}", F(1, 4): r"\dfrac{\sqrt2}{2}", F(1, 3): r"\dfrac12", F(1, 2): "0",
       F(2, 3): r"-\dfrac12", F(3, 4): r"-\dfrac{\sqrt2}{2}", F(5, 6): r"-\dfrac{\sqrt3}{2}", F(1): "-1"}
VALS = ["1", r"\dfrac{\sqrt3}{2}", r"\dfrac{\sqrt2}{2}", r"\dfrac12", "0", r"-\dfrac12", r"-\dfrac{\sqrt2}{2}", r"-\dfrac{\sqrt3}{2}", "-1"]


def cosv(t):
    t = F(t) % 2
    if t > 1:
        t = 2 - t
    return COS[t]


def sinv(t):
    return cosv(F(1, 2) - F(t))


def neg(v):
    return v[1:] if v.startswith("-") else ("0" if v == "0" else "-" + v)


@qtype("tri", "180° correspond à π radians : multiplie par π/180.",
       [60, 45, 30, 120, 135, 150, 90, 270])
def _(d):
    t = F(d, 180)
    return (rf"Quelle est la mesure en radians d'un angle de ${d}^\circ$ ?", m(ang(t)), [m(ang(F(180, d) if F(180, d) != t else F(1, 5))), m(ang(F(d, 90)) if F(d, 90) != t else ang(t * 2)), m(ang(t * 2) if t * 2 != F(d, 90) else ang(t / 2)), m(ang(F(d, 360)))])


@qtype("tri", "π radians correspondent à 180° : multiplie par 180/π.",
       [F(1, 5), F(2, 3), F(3, 2), F(1, 12), F(5, 4), F(7, 6), F(1, 9), F(4, 3)])
def _(t):
    d = t * 180
    D = lambda x: m(rf"{nb(x)}^\circ")
    return (rf"Quelle est la mesure en degrés d'un angle de ${ang(t)}$ radians ?", D(d), [D(d * 2), D(d / 2), D(360 - d) if 360 - d != d else D(d + 90), D(180 - d) if 180 - d > 0 else D(d - 90), D(d + 30)])


def trig_opts(v):
    i = VALS.index(v)
    near = [VALS[j] for j in (i - 1, i + 1, len(VALS) - 1 - i) if 0 <= j < len(VALS) and VALS[j] != v]
    pool = near + [neg(v)] + [x for x in VALS if x != v]
    out = []
    for x in pool:
        if x != v and x not in out:
            out.append(x)
    return [m(x) for x in out[:4]]


@qtype("tri", "Sur le cercle trigonométrique, cos x est l'abscisse du point associé à x.",
       [F(1, 3), F(1, 4), F(1, 6), F(2, 3), F(1), F(3, 4), F(1, 2), F(5, 6)])
def _(t):
    v = cosv(t)
    return (rf"Que vaut $\cos\left({ang(t)}\right)$ ?", m(v), trig_opts(v))


@qtype("tri", "Sur le cercle trigonométrique, sin x est l'ordonnée du point associé à x.",
       [F(1, 6), F(1, 4), F(1, 3), F(1, 2), F(-1, 3), F(1), F(3, 2), F(5, 6)])
def _(t):
    v = sinv(t)
    return (rf"Que vaut $\sin\left({ang(t)}\right)$ ?", m(v), trig_opts(v))


@qtype("tri", "cos(π − x) = −cos x, cos(−x) = cos x, sin(−x) = −sin x, sin(π − x) = sin x, sin(π/2 − x) = cos x.",
       [(r"\cos(\pi-x)", "cos", F(6, 10), -1), (r"\cos(-x)", "cos", F(8, 10), 1), (r"\sin(-x)", "sin", F(3, 10), -1), (r"\cos(\pi+x)", "cos", F(-4, 10), -1),
        (r"\sin(\pi-x)", "sin", F(25, 100), 1), (r"\sin(\pi+x)", "sin", F(7, 10), -1), (r"\cos(x+2\pi)", "cos", F(-5, 10), 1), (r"\sin\left(\dfrac{\pi}{2}-x\right)", "cos", F(9, 10), 1)])
def _(p):
    e, w, v, s = p
    r = s * v
    return (rf"On sait que $\{w} x={nb(v)}$. Que vaut ${e}$ ?", m(nb(r)), [m(nb(-r)), m(nb(1 - v)), m(nb(1 - v * v)) if 1 - v * v not in (r, -r) else m(nb(v / 2))])


@qtype("tri", "La mesure principale est dans ]−π ; π] : ajoute ou retire des multiples de 2π.",
       [F(17, 6), F(7, 3), F(-5, 4), F(9, 2), F(13, 4), F(25, 6), F(-10, 3), F(15, 4)])
def _(t):
    r = ang(t, True)
    rv = F(t)
    while rv <= -1:
        rv += 2
    while rv > 1:
        rv -= 2
    alts = [ang(-rv, True) if -rv != rv else ang(rv + F(1, 2), True), ang(rv + 1, True), ang(rv / 2, True) if rv / 2 != rv else ang(rv + F(1, 3), True), ang(rv + F(1, 3), True), ang(F(t) - 2 * int(F(t) / 2) if F(t) > 0 else F(t) + 2, False)]
    return (rf"Quelle est la mesure principale de l'angle ${ang(t)}$ ?", m(r), [m(a) for a in alts])


@qtype("tri", "cos² x + sin² x = 1 ; sur [0 ; π], sin x ≥ 0.",
       [F(3, 5), F(4, 5), F(5, 13), F(-8, 17), F(1, 2), F(-7, 25), F(12, 13), F(-20, 29)])
def _(c):
    s2 = 1 - c * c
    num, den = s2.numerator, s2.denominator
    rn, rd = int(num ** .5), int(den ** .5)
    s = lf(F(rn, rd)) if rn * rn == num and rd * rd == den else rf"\dfrac{{{sqs(num)}}}{{{rd}}}"
    return (rf"On sait que $x\in[0\,;\,\pi]$ et $\cos x={lf(c)}$. Que vaut $\sin x$ ?", m(s), [m("-" + s), m(lf(1 - c)), m(lf(s2))])


@qtype("tri", "(eᵃ)ⁿ = eⁿᵃ et eᵃ × eᵇ = eᵃ⁺ᵇ.",
       [(2, 3, -1), (-1, 4, 6), (3, 2, -7), (1, 5, -5), (4, -1, 2), (-2, -3, 1), (5, 2, -4), (3, 3, -5)])
def _(p):
    a, n, b = p
    E = lambda k: m("1" if k == 0 else "e" if k == 1 else f"e^{{{k}}}")
    r = a * n + b
    return (rf"Simplifier $\left(e^{{{a}}}\right)^{{{n}}}\times e^{{{b}}}$.", E(r), [E(a + n + b) if a + n + b != r else E(r + 1), E(a ** n + b) if a ** n + b != r else E(r - 1), E(a * (n + b)) if a * (n + b) != r else E(r + 2), E(a * n - b), E(-r) if r else E(1), E(r + 3)])


# ============================================================ PRODUIT SCALAIRE ET GÉOMÉTRIE REPÉRÉE
def vc(v):
    return rf"\begin{{pmatrix}}{nb(v[0])}\\{nb(v[1])}\end{{pmatrix}}"


@qtype("psc", "Dans un repère orthonormé, u · v = x x' + y y'.",
       [((2, 3), (4, -1)), ((-1, 5), (3, 2)), ((4, -2), (1, 2)), ((3, 1), (-2, 5)), ((-3, -4), (2, -1)), ((5, 2), (1, 3)), ((0, 4), (7, -2)), ((6, -1), (2, 4))])
def _(p):
    (x, y), (a, b) = p
    s = x * a + y * b
    return (rf"Dans un repère orthonormé, que vaut $\vec u\cdot\vec v$ pour $\vec u{vc((x, y))}$ et $\vec v{vc((a, b))}$ ?",
            m(nb(s)), [m(nb(x * b + y * a)), m(nb(x * a - y * b)), m(nb(x * b - y * a)) if x * b - y * a != s else m(nb(s + 1)), m(nb(s + 2))])


@qtype("psc", "u · v = ‖u‖ × ‖v‖ × cos(u, v).",
       [(3, 4, 60), (2, 5, 120), (6, 1, 90), (4, 4, 0), (2, 3, 180), (5, 2, 60), (3, 6, 120), (7, 2, 60)])
def _(p):
    a, b, t = p
    c = {0: F(1), 60: F(1, 2), 90: F(0), 120: F(-1, 2), 180: F(-1)}[t]
    r = a * b * c
    return (rf"$\|\vec u\|={a}$, $\|\vec v\|={b}$ et l'angle entre $\vec u$ et $\vec v$ mesure ${t}^\circ$. Que vaut $\vec u\cdot\vec v$ ?",
            m(nb(r)), [m(nb(a * b)) if a * b != r else m(nb(a + b)), m(nb(-r)) if r else m(nb(a * b // 2)), m(nb(a + b)) if a + b != r else m(nb(r + 1))])


@qtype("psc", "Deux vecteurs sont orthogonaux quand leur produit scalaire est nul.",
       [(2, 3, -6), (4, 1, 2), (-3, 2, 3), (5, 2, -4), (1, -3, 6), (6, -1, 3), (3, 5, -3), (-2, -4, 8)])
def _(p):
    a, c, d = p
    r = F(-a * c, d)
    return (rf"Pour quelle valeur de $m$ les vecteurs $\vec u\begin{{pmatrix}}{a}\\m\end{{pmatrix}}$ et $\vec v{vc((c, d))}$ sont-ils orthogonaux ?",
            m("m=" + lf(r)), [m("m=" + lf(-r)), m("m=" + lf(F(-d, a * c))) if F(-d, a * c) != r else m("m=" + lf(r + 1)), m("m=" + nb(-a * c)) if -a * c != r else m("m=" + lf(r * 2))])


@qtype("psc", "Al-Kashi : BC² = AB² + AC² − 2 × AB × AC × cos Â.",
       [(3, 5, 60), (4, 6, 60), (4, 5, 120), (5, 8, 60), (3, 3, 120), (6, 10, 120), (1, 1, 60), (7, 3, 60)])
def _(p):
    a, b, t = p
    c = F(1, 2) if t == 60 else F(-1, 2)
    bc2 = a * a + b * b - 2 * a * b * c
    assert bc2.denominator == 1
    return (rf"Dans le triangle $ABC$, $AB={a}$, $AC={b}$ et $\widehat{{BAC}}={t}^\circ$. Combien mesure $BC$ ?",
            m(sqs(int(bc2))), [m(sqs(a * a + b * b)), m(sqs(int(a * a + b * b + 2 * a * b * c))), m(nb(bc2))])


@qtype("psc", "Une droite d'équation ax + by + c = 0 a pour vecteur normal n(a ; b) et pour vecteur directeur u(−b ; a).",
       [(2, -3, 5), (1, 4, -2), (-5, 1, 3), (3, 3, -1), (4, -1, 0), (1, -2, 7), (-2, -5, 4), (6, 1, -3)])
def _(p):
    a, b, c = p
    eq = expr([(a, "x"), (b, "y"), (c, "")]) + "=0"
    return (rf"Lequel de ces vecteurs est un vecteur normal à la droite d'équation ${eq}$ ?", m(vc((a, b))),
            [m(vc((-b, a))), m(vc((b, a))) if b != a else m(vc((a, -b))), m(vc((a, c))) if c != b else m(vc((a, b + 1)))])


@qtype("psc", "Avec n(a ; b) normal, l'équation est ax + by + c = 0 ; trouve c avec les coordonnées du point.",
       [((2, -1), (1, 3)), ((3, 4), (-1, 2)), ((1, 1), (2, -5)), ((-2, 5), (0, 1)), ((4, -3), (3, 3)), ((1, -2), (-4, -1)), ((5, 2), (1, 0)), ((-1, 3), (2, 2))])
def _(p):
    (a, b), (x, y) = p
    c = -(a * x + b * y)
    Eq = lambda A, B, C: m(expr([(A, "x"), (B, "y"), (C, "")]) + "=0")
    return (rf"Quelle est une équation cartésienne de la droite passant par $A{pt((x, y))}$ et de vecteur normal $\vec n{vc((a, b))}$ ?",
            Eq(a, b, c), [Eq(a, b, -c) if c else Eq(a, b, 1), Eq(-b, a, b * x - a * y) if (-b, a) != (a, b) else Eq(a, b, c + 1), Eq(x, y, -(a * x + b * y)) if (x, y) != (a, b) else Eq(a, b, c + 2)])


@qtype("psc", "Le cercle de centre Ω(a ; b) et de rayon r a pour équation (x − a)² + (y − b)² = r².",
       [(2, -1, 9), (-3, 4, 25), (0, 5, 16), (1, 1, 2), (-2, -6, 49), (4, 0, 12), (-1, 3, 1), (5, -5, 36)])
def _(p):
    a, b, r2 = p
    sq_ = lambda c, v: f"{v}^2" if c == 0 else f"({v}{'-' if c > 0 else '+'}{abs(c)})^2"
    eq = sq_(a, "x") + "+" + sq_(b, "y") + f"={r2}"
    C = lambda P, r: m(rf"\Omega{pt(P)}\text{{, rayon }}{r}")
    return (rf"Quels sont le centre et le rayon du cercle d'équation ${eq}$ ?", C((a, b), sqs(r2)),
            [C((-a, -b), sqs(r2)) if (a, b) != (0, 0) else C((1, 1), sqs(r2)), C((a, b), nb(r2)) if sqs(r2) != nb(r2) else C((a, b), nb(2 * r2)), C((b, a), sqs(r2)) if a != b else C((a, -b), sqs(r2)), C((-a, -b), nb(r2)), C((a, b), nb(2 * r2))])


@qtype("psc", "‖u + v‖² = ‖u‖² + 2 u · v + ‖v‖².",
       [(3, 4, 2), (2, 5, -3), (1, 1, 0), (6, 2, -5), (4, 3, 6), (5, 5, -8), (2, 7, 1), (3, 3, -4)])
def _(p):
    a, b, d = p
    r = a * a + b * b + 2 * d
    return (rf"On a $\|\vec u\|={a}$, $\|\vec v\|={b}$ et $\vec u\cdot\vec v={nb(d)}$. Que vaut $\|\vec u+\vec v\|^2$ ?",
            m(nb(r)), [m(nb(a * a + b * b)) if d else m(nb(r + 2)), m(nb((a + b) ** 2)), m(nb(a * a + b * b + d)) if d else m(nb(r + 1))])


# ============================================================ PROBABILITÉS CONDITIONNELLES ET VARIABLES ALÉATOIRES
D_ = lambda s: F(s)


@qtype("cvp", "P_A(B) = P(A ∩ B) ÷ P(A).",
       [(F(5, 10), F(2, 10)), (F(4, 10), F(1, 10)), (F(8, 10), F(6, 10)), (F(25, 100), F(5, 100)), (F(6, 10), F(3, 10)), (F(5, 10), F(35, 100)), (F(4, 10), F(32, 100)), (F(3, 10), F(27, 100))])
def _(p):
    a, c = p
    return (rf"On a $P(A)={nb(a)}$ et $P(A\cap B)={nb(c)}$. Que vaut $P_A(B)$ ?", m(nb(c / a)), [m(nb(a * c)), m(nb(a - c)), m(nb(a + c)) if a + c <= 1 else m(nb(1 - c)), m(nb(c))])


@qtype("cvp", "P(A ∩ B) = P(A) × P_A(B).",
       [(F(6, 10), F(5, 10)), (F(3, 10), F(4, 10)), (F(8, 10), F(25, 100)), (F(45, 100), F(2, 10)), (F(7, 10), F(9, 10)), (F(25, 100), F(6, 10)), (F(5, 10), F(5, 10)), (F(9, 10), F(3, 10))])
def _(p):
    a, b = p
    return (rf"On a $P(A)={nb(a)}$ et $P_A(B)={nb(b)}$. Que vaut $P(A\cap B)$ ?", m(nb(a * b)),
            [m(nb(a + b)) if a + b <= 1 else m(nb(a + b - 1)), m(nb(a * (1 - b))) if a * (1 - b) != a * b else m(nb(b)), m(nb(b / a)) if b / a <= 1 and b / a != a * b else m(nb(1 - a * b)), m(nb(b)), m(nb(1 - a * b)), m(nb(a * b + F(1, 10)))])


@qtype("cvp", "Probabilités totales : P(B) = P(A) × P_A(B) + P(Ā) × P_Ā(B).",
       [(F(3, 10), F(5, 10), F(2, 10)), (F(6, 10), F(4, 10), F(1, 10)), (F(5, 10), F(8, 10), F(4, 10)), (F(2, 10), F(9, 10), F(3, 10)),
        (F(4, 10), F(25, 100), F(5, 10)), (F(7, 10), F(6, 10), F(2, 10)), (F(1, 10), F(5, 10), F(1, 10)), (F(25, 100), F(4, 10), F(8, 10))])
def _(p):
    a, b, c = p
    r = a * b + (1 - a) * c
    return (rf"On a $P(A)={nb(a)}$, $P_A(B)={nb(b)}$ et $P_{{\overline{{A}}}}(B)={nb(c)}$. Que vaut $P(B)$ ?",
            m(nb(r)), [m(nb(a * b)), m(nb(b + c)) if b + c <= 1 else m(nb(b * c)), m(nb(a * b + a * c)) if a * b + a * c != r else m(nb(r + F(1, 10))), m(nb((1 - a) * c))])


@qtype("cvp", "A et B sont indépendants si et seulement si P(A ∩ B) = P(A) × P(B).",
       [(F(5, 10), F(4, 10), F(2, 10)), (F(3, 10), F(6, 10), F(2, 10)), (F(25, 100), F(8, 10), F(2, 10)), (F(7, 10), F(5, 10), F(3, 10)),
        (F(6, 10), F(5, 10), F(3, 10)), (F(2, 10), F(4, 10), F(1, 10)), (F(9, 10), F(1, 10), F(9, 100)), (F(4, 10), F(4, 10), F(2, 10))])
def _(p):
    a, b, c = p
    ok = a * b == c
    return (rf"On a $P(A)={nb(a)}$, $P(B)={nb(b)}$ et $P(A\cap B)={nb(c)}$. Les événements $A$ et $B$ sont-ils indépendants ?",
            "oui" if ok else "non", ["non" if ok else "oui", "on ne peut pas savoir", "seulement s'ils sont incompatibles"])


def law(p):
    xs = [x for x, q in p]; ps = [q for x, q in p]
    return r"\begin{array}{|l|" + "c|" * len(p) + r"}\hline x_i & " + " & ".join(nb(x) for x in xs) + r"\\\hline P(X=x_i) & " + " & ".join(nb(q) for q in ps) + r"\\\hline\end{array}"


@qtype("cvp", "E(X) = somme des xᵢ × P(X = xᵢ).",
       [((-2, F(3, 10)), (1, F(5, 10)), (5, F(2, 10))), ((0, F(1, 4)), (2, F(1, 2)), (4, F(1, 4))), ((-1, F(4, 10)), (3, F(6, 10))),
        ((1, F(2, 10)), (2, F(3, 10)), (3, F(5, 10))), ((-5, F(1, 10)), (0, F(6, 10)), (10, F(3, 10))), ((2, F(1, 2)), (6, F(1, 2))),
        ((-3, F(1, 2)), (1, F(1, 4)), (5, F(1, 4))), ((10, F(1, 10)), (20, F(2, 10)), (-4, F(7, 10)))])
def _(p):
    E = sum(x * q for x, q in p)
    mean = F(sum(x for x, q in p), len(p))
    return (rf"Voici la loi de probabilité d'une variable aléatoire $X$. Que vaut $E(X)$ ? ${law(p)}$",
            m(nb(E)), [m(nb(mean)) if mean != E else m(nb(E + 2)), m(nb(E + 1)), m(nb(-E)) if E else m("1"), m(nb(sum(x * x * q for x, q in p)))])


@qtype("cvp", "V(X) = E(X²) − E(X)², avec E(X²) = somme des xᵢ² × P(X = xᵢ).",
       [((0, F(1, 2)), (2, F(1, 2))), ((0, F(1, 4)), (4, F(3, 4))), ((-2, F(1, 2)), (2, F(1, 2))), ((0, F(6, 10)), (10, F(4, 10))),
        ((1, F(1, 4)), (2, F(1, 2)), (3, F(1, 4))), ((-3, F(1, 2)), (3, F(1, 2))), ((0, F(2, 10)), (5, F(8, 10))), ((0, F(9, 10)), (10, F(1, 10)))])
def _(p):
    E = sum(x * q for x, q in p); E2 = sum(x * x * q for x, q in p)
    V = E2 - E * E
    return (rf"Voici la loi de probabilité d'une variable aléatoire $X$. Que vaut sa variance $V(X)$ ? ${law(p)}$",
            m(nb(V)), [m(nb(E2)) if E2 != V else m(nb(V + 2)), m(nb(E)) if E != V else m(nb(V * 2)), m(nb(V + 1)), m(nb(2 * V)) if 2 * V not in (E, E2) else m(nb(V + 3))])


@qtype("cvp", "Parmi un groupe, la probabilité se calcule sur l'effectif de ce groupe seulement.",
       [((12, 8), (10, 20), 0), ((15, 5), (9, 11), 1), ((6, 14), (18, 12), 0), ((20, 10), (5, 15), 1), ((9, 3), (7, 21), 0), ((14, 6), (8, 12), 1), ((5, 15), (25, 5), 0), ((18, 2), (10, 10), 1)])
def _(p):
    f, g, w = p
    row = (f, g)[w]
    tot = sum(f) + sum(g)
    T = rf"\begin{{array}}{{|l|c|c|}}\hline & \text{{Demi-pens.}} & \text{{Externes}}\\\hline \text{{Filles}} & {f[0]} & {f[1]}\\\hline \text{{Garçons}} & {g[0]} & {g[1]}\\\hline\end{{array}}"
    who = ("une fille", "un garçon")[w]
    return (rf"On choisit au hasard {who} de ce groupe. Quelle est la probabilité que ce soit un demi-pensionnaire ? ${T}$",
            m(lf(F(row[0], sum(row)))), [m(lf(F(row[0], tot))), m(lf(F(row[0], f[0] + g[0]))), m(lf(F(row[1], sum(row)))), m(lf(F(f[0] + g[0], tot))), m(lf(F(row[0], row[1]))) if row[0] < row[1] else m(lf(F(row[1], row[0])))])


@qtype("cvp", "P(X ≥ k) est la somme des probabilités des valeurs supérieures ou égales à k.",
       [((F(1, 10), F(2, 10), F(3, 10), F(25, 100), F(15, 100)), 2), ((F(2, 10), F(2, 10), F(2, 10), F(2, 10), F(2, 10)), 3), ((F(5, 100), F(15, 100), F(4, 10), F(3, 10), F(1, 10)), 1),
        ((F(3, 10), F(1, 10), F(1, 10), F(35, 100), F(15, 100)), 3), ((F(1, 10), F(1, 10), F(6, 10), F(1, 10), F(1, 10)), 2), ((F(25, 100), F(25, 100), F(2, 10), F(2, 10), F(1, 10)), 4),
        ((F(4, 10), F(3, 10), F(2, 10), F(5, 100), F(5, 100)), 1), ((F(12, 100), F(18, 100), F(3, 10), F(3, 10), F(1, 10)), 2)])
def _(p):
    ps, k = p
    r = sum(ps[k:])
    law_ = list(zip(range(5), ps))
    return (rf"Voici la loi de probabilité d'une variable aléatoire $X$. Que vaut $P(X\geqslant{k})$ ? ${law(law_)}$",
            m(nb(r)), [m(nb(sum(ps[k + 1:]))), m(nb(ps[k])) if ps[k] != r else m(nb(r / 2)), m(nb(1 - r)) if 1 - r != r else m(nb(sum(ps[k:]) + ps[k - 1])), m(nb(r + ps[k - 1])), m(nb(r - F(1, 10)))])


# ============================================================ BUILD
THEMES = {"sui": ("Suites", "1F6FA8"), "deg": ("Second degré", "6A4C93"),
          "der": ("Dérivation", "2E7D6B"), "tri": ("Trigonométrie et exponentielle", "C77F0A"),
          "psc": ("Produit scalaire et géométrie repérée", "C0503A"), "cvp": ("Probabilités conditionnelles et variables aléatoires", "8A5A2B")}
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
                    rf"{{\Large\bfseries\color{{c{th}}}{'abcd'[i]})}}\quad\begin{{minipage}}[c]{{5.3cm}}\raggedright{'\\Large' if len(shown[i]) < 26 else '\\large'} {shown[i]}\end{{minipage}}\end{{tcolorbox}}")
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
open(f"{OUT}/premiere.tex", "w", encoding="utf-8").write("\n".join(tex).replace("\\leqslant", "\\leqslant ").replace("\\geqslant", "\\geqslant "))
json.dump([[n, th, g, h] for n, th, g, _, h in KEY], open(f"{OUT}/questions.json", "w"))
json.dump([t[3] for t in TYPES], open(f"{OUT}/hints.json", "w"), ensure_ascii=False, indent=0)
with open(f"{OUT}/corrige.txt", "w", encoding="utf-8") as f:
    for n, th, g, a, h in KEY:
        f.write(f"Q{n if n <= HALF else str((n - 1) % HALF + 1) + ' ' + 'ABCD'[(n - 1) // HALF]} ({THEMES[th][0]}) : {g}) {a}\n")
print(len(KEY), "questions ; fallback:", FALLBACK)
