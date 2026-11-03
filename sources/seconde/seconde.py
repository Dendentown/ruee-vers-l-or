"""Banque Mathématiques 2nde (programme de seconde générale et technologique, 2019) :
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


# ============================================================ NOMBRES ET CALCULS
def sqs(n):
    """simplified square root of a positive integer n, in LaTeX"""
    a, b = 1, n
    f = 2
    while f * f <= b:
        while b % (f * f) == 0:
            b //= f * f; a *= f
        f += 1
    if b == 1:
        return str(a)
    return (str(a) if a > 1 else "") + rf"\sqrt{{{b}}}"


def ksq(k, b):
    return "0" if k == 0 else (rf"\sqrt{{{b}}}" if k == 1 else f"{k}" + rf"\sqrt{{{b}}}") if b != 1 else str(k)


@qtype("nom", "Écris le nombre sous la racine comme un produit d'un carré parfait et d'un autre nombre : √(a²b) = a√b.",
       [50, 12, 72, 18, 45, 98, 200, 75])
def _(N):
    a, b = 1, N
    for f in range(2, 20):
        while b % (f * f) == 0:
            b //= f * f; a *= f
    return (rf"Écrire $\sqrt{{{N}}}$ sous la forme $a\sqrt{{b}}$, avec $b$ le plus petit possible.",
            m(ksq(a, b)), [m(ksq(b, a)) if a != b else m(ksq(a + 1, b)), m(ksq(a * a, b)), m(ksq(a, 2 * b)), m(ksq(a - 1, b + 1) if a > 1 else ksq(2, b))])


@qtype("nom", "Simplifie chaque racine (√(a²b) = a√b), puis additionne les nombres de √b.",
       [((2, 3), (3, 3)), ((2, 2), (3, 2)), ((2, 5), (3, 5)), ((5, 2), (4, 2)), ((3, 3), (5, 3)), ((3, 2), (6, 2)), ((2, 7), (3, 7)), ((4, 3), (2, 3))])
def _(p):
    (p1, b), (p2, _) = p
    N1, N2 = p1 * p1 * b, p2 * p2 * b
    return (rf"Que vaut $\sqrt{{{N1}}}+\sqrt{{{N2}}}$ ?", m(ksq(p1 + p2, b)), [m(rf"\sqrt{{{N1 + N2}}}"), m(ksq(p1 * p2, b)), m(ksq(p1 + p2, 2 * b)), m(ksq(p1 + p2 + 1, b))])


def lin(k, a, v="x"):
    return expr([(k, v), (a, "")])


@qtype("nom", "(a + b)² = a² + 2ab + b² et (a − b)² = a² − 2ab + b².",
       [(1, 3), (1, -5), (2, 1), (3, -2), (1, 7), (2, -5), (4, 1), (3, 4)])
def _(p):
    k, a = p
    Q = lambda c2, c1, c0: expr([(c2, "x^2"), (c1, "x"), (c0, "")])
    return (rf"Développer $({lin(k, a)})^2$.", m(Q(k * k, 2 * k * a, a * a)), [m(Q(k * k, 0, a * a)), m(Q(k * k, k * a, a * a)), m(Q(k, 2 * k * a, a * a)) if k != 1 else m(Q(1, 2 * a, -a * a)), m(Q(k * k, 2 * k * a, -a * a))])


@qtype("nom", "a² − b² = (a − b)(a + b) : repère les deux carrés.",
       [(1, 3), (1, 5), (2, 1), (3, 4), (1, 7), (5, 2), (4, 3), (1, 8)])
def _(p):
    k, a = p
    sq_ = expr([(k * k, "x^2"), (-a * a, "")])
    return (rf"Factoriser ${sq_}$.", m(f"({lin(k, -a)})({lin(k, a)})"),
            [m(f"({lin(k, -a)})^2"), m(f"({lin(k, a)})^2"), m(f"({lin(k * k, -a)})({lin(k * k, a)})") if k != 1 else m(f"({lin(1, -a * a)})({lin(1, a * a)})")])


@qtype("nom", "Reconnais a² + 2ab + b² = (a + b)² ou a² − 2ab + b² = (a − b)².",
       [(1, 3), (1, -4), (3, -2), (2, 5), (5, -1), (4, 3), (1, -6), (3, 5)])
def _(p):
    k, a = p
    Q = expr([(k * k, "x^2"), (2 * k * a, "x"), (a * a, "")])
    return (rf"Factoriser ${Q}$.", m(f"({lin(k, a)})^2"), [m(f"({lin(k, -a)})^2"), m(f"({lin(k, -a)})({lin(k, a)})"), m(f"({lin(k * k, a)})^2") if k != 1 else m(f"({lin(1, 2 * a)})^2")])


def iv(lo, hi, lc, hc):
    L = "[" if (lc and lo is not None) else "]"
    R = "]" if (hc and hi is not None) else "["
    a = r"-\infty" if lo is None else nb(lo)
    b = r"+\infty" if hi is None else nb(hi)
    return rf"{L}{a}\,;\,{b}{R}"


def ineq(lo, hi, lc, hc):
    if lo is None:
        return rf"x{'\\leqslant' if hc else '<'}{nb(hi)}"
    if hi is None:
        return rf"x{'\\geqslant' if lc else '>'}{nb(lo)}"
    return rf"{nb(lo)}{'\\leqslant' if lc else '<'}x{'\\leqslant' if hc else '<'}{nb(hi)}"


@qtype("nom", "Crochet tourné vers le nombre : il est compris (≤) ; crochet tourné vers l'extérieur : il est exclu (<).",
       [(-2, 5, True, False), (3, None, False, False), (None, 4, False, True), (0, 1, True, True),
        (-1, 7, False, True), (-6, None, True, False), (None, -3, False, False), (2, 9, False, False)])
def _(p):
    lo, hi, lc, hc = p
    if lo is None:
        alts = [ineq(lo, hi, lc, not hc), rf"x{'\\geqslant' if hc else '>'}{nb(hi)}", rf"x{'>' if hc else '\\geqslant'}{nb(hi)}"]
    elif hi is None:
        alts = [ineq(lo, hi, not lc, hc), rf"x{'\\leqslant' if lc else '<'}{nb(lo)}", rf"x{'<' if lc else '\\leqslant'}{nb(lo)}"]
    else:
        alts = [ineq(lo, hi, not lc, hc), ineq(lo, hi, lc, not hc), ineq(lo, hi, not lc, not hc)]
    return (rf"Que signifie $x\in{iv(lo, hi, lc, hc)}$ ?", m(ineq(lo, hi, lc, hc)), [m(a) for a in alts])


@qtype("nom", "|x − a| ≤ r signifie que la distance entre x et a est au plus r : a − r ≤ x ≤ a + r.",
       [(3, 2), (-1, 4), (0, 5), (2, 7), (-4, 1), (6, 3), (-2, 2), (1, 6)])
def _(p):
    a, r = p
    ab = "|x|" if a == 0 else f"|x{'-' if a > 0 else '+'}{abs(a)}|"
    I = lambda lo, hi, lc=True, hc=True: m(r"x\in" + iv(lo, hi, lc, hc))
    return (rf"Pour quels réels $x$ a-t-on ${ab}\leqslant{r}$ ?", I(a - r, a + r),
            [I(-a - r, -a + r) if a else I(-r, r, False, False), I(a, a + r), I(a - 2 * r, a + 2 * r), I(a - r, a + r, True, False)])


@qtype("nom", "aᵐ × aⁿ = aᵐ⁺ⁿ et aᵐ ÷ aⁿ = aᵐ⁻ⁿ.",
       [(2, 5, -3, 4), (3, 4, 2, 7), (5, -2, 6, 1), (10, 3, -5, -4), (7, 2, 2, 6), (2, -1, -4, -8), (3, 6, -2, 3), (10, -3, 8, 2)])
def _(p):
    b, x, y, z = p
    P = lambda e: m(f"{b}^{{{e}}}")
    return (rf"Écrire $\dfrac{{{b}^{{{x}}}\times{b}^{{{y}}}}}{{{b}^{{{z}}}}}$ sous la forme d'une puissance de ${b}$.",
            P(x + y - z), [P(x * y - z), P(x + y + z), P(x - y - z), P(x * y // z if z and (x * y) % z == 0 else x + y - z + 1)])


# ============================================================ ÉVOLUTIONS ET STATISTIQUES
def pc(x):
    return rf"{'+' if x > 0 else ''}{nb(x)}\,\%"


@qtype("sta", "Une hausse de t % correspond au coefficient multiplicateur 1 + t/100 ; une baisse, à 1 − t/100.",
       [20, -15, 5, -30, 150, -2, F(1, 2), -45])
def _(t):
    t = F(t)
    w = f"hausse de ${nb(t)}\\,\\%$" if t > 0 else f"baisse de ${nb(-t)}\\,\\%$"
    return (rf"Quel est le coefficient multiplicateur associé à une {w} ?",
            m(nb(1 + t / 100)), [m(nb(t / 100)), m(nb(1 - t / 100)), m(nb(1 + t / 10)), m(nb(abs(t)))])


@qtype("sta", "Valeur finale = valeur initiale × coefficient multiplicateur.",
       [(80, 25), (250, -20), (1200, 15), (45, -10), (600, 8), (3500, -35), (90, 50), (F(25, 2), -40)])
def _(p):
    P0, t = p
    P1 = F(P0) * (1 + F(t, 100))
    w = f"augmente de ${t}\\,\\%$" if t > 0 else f"baisse de ${-t}\\,\\%$"
    eu = lambda x: u(nb(x), "€")
    return (rf"Un prix de ${nb(P0)}$ € {w}. Quel est le nouveau prix ?",
            eu(P1), [eu(P0 + t), eu(F(P0) * (1 - F(t, 100))), eu(F(P0) * abs(t) / 100), eu(P1 + 1)])


@qtype("sta", "Taux d'évolution = (valeur finale − valeur initiale) ÷ valeur initiale.",
       [(50, 65), (80, 60), (200, 230), (40, 50), (125, 100), (250, 280), (90, 99), (1500, 1140)])
def _(p):
    a, b = p
    t = F(b - a, a) * 100
    return (rf"Une quantité passe de ${nb(a)}$ à ${nb(b)}$. Quel est son taux d'évolution ?",
            m(pc(t)), [m(pc(b - a)), m(pc(-t)), m(pc(t / 2)), m(pc(t + 5))])


@qtype("sta", "Des évolutions successives se combinent en multipliant les coefficients multiplicateurs.",
       [(20, -20), (10, 10), (-50, 50), (30, -10), (-20, -20), (25, -20), (50, 20), (-10, 20)])
def _(p):
    t1, t2 = p
    g = ((1 + F(t1, 100)) * (1 + F(t2, 100)) - 1) * 100
    W = lambda t: f"une hausse de ${t}\\,\\%$" if t > 0 else f"une baisse de ${-t}\\,\\%$"
    return (rf"Un prix subit {W(t1)}, puis {W(t2)}. Quelle est son évolution globale ?",
            m(pc(g) if g else r"0\,\%"), [m(pc(t1 + t2) if t1 + t2 else r"0\,\%"), m(pc(F(t1 * t2, 100)) if t1 * t2 else r"0\,\%"), m(pc(g + 1)), m(pc(g - 2))])


@qtype("sta", "Pour annuler une évolution de coefficient c, il faut l'évolution de coefficient 1/c.",
       [("baisse", 20), ("baisse", 50), ("hausse", 25), ("baisse", 60), ("hausse", 100), ("baisse", F(75, 2)), ("hausse", 300), ("baisse", 80)])
def _(p):
    w, t = p
    c = 1 + F(t, 100) * (1 if w == "hausse" else -1)
    r = (1 / c - 1) * 100
    other = "hausse" if r > 0 else "baisse"
    W = lambda x: f"une {other} de ${nb(abs(x))}\\,\\%$"
    return (rf"Après {('une hausse' if w == 'hausse' else 'une baisse')} de ${nb(t)}\,\%$, quelle évolution faut-il appliquer pour revenir au prix de départ ?",
            W(r), [W(t) if t != abs(r) else W(t + 5), f"une {w} de ${nb(abs(r))}\\,\\%$", W(abs(r) + 10), W(abs(r) / 2)])


@qtype("sta", "La proportion d'une sous-population se calcule en multipliant les deux proportions.",
       [(40, 25), (60, 50), (30, 20), (80, 15), (25, 60), (90, 10), (70, 30), (55, 40)])
def _(p):
    a, b = p
    r = F(a * b, 100)
    P = lambda x: m(rf"{nb(x)}\,\%")
    return (rf"Dans un lycée, ${a}\,\%$ des élèves sont internes et ${b}\,\%$ des internes viennent d'une autre commune. Quelle proportion des élèves du lycée sont des internes venant d'une autre commune ?",
            P(r), [P(a + b) if a + b <= 100 else P(abs(a - b) + 1), P(abs(a - b)), P(F(a + b, 2)), P(r * 2)])


@qtype("sta", "Moyenne pondérée = somme des (valeur × effectif) ÷ effectif total.",
       [((8, 2), (12, 5), (15, 3)), ((10, 4), (14, 4), (18, 2)), ((5, 1), (10, 3), (20, 1)), ((0, 2), (1, 5), (2, 3)),
        ((12, 6), (16, 2)), ((1, 3), (2, 4), (3, 2), (4, 1)), ((9, 5), (11, 5), (16, 10)), ((6, 2), (13, 3))])
def _(p):
    vs = [v for v, e in p]; es = [e for v, e in p]
    mean = F(sum(v * e for v, e in p), sum(es))
    T = r"\begin{array}{|l|" + "c|" * len(p) + r"}\hline \text{Valeur} & " + " & ".join(map(str, vs)) + r"\\\hline \text{Effectif} & " + " & ".join(map(str, es)) + r"\\\hline\end{array}"
    return (rf"Quelle est la moyenne de cette série statistique ? ${T}$",
            m(nb(mean)), [m(nb(F(sum(vs), len(vs)))), m(nb(F(sum(v * e for v, e in p), len(p)))), m(nb(mean + 1)), m(nb(mean - F(1, 2)))])


@qtype("sta", "Le premier quartile Q₁ est la plus petite valeur de la série rangée telle qu'au moins 25 % des valeurs lui soient inférieures ou égales.",
       [(3, 5, 7, 8, 10, 12, 15, 18), (2, 4, 4, 6, 9, 11, 13, 14, 20), (10, 12, 13, 15, 16, 18, 21, 22, 25, 30), (1, 1, 2, 3, 5, 8, 13, 21),
        (7, 9, 10, 10, 11, 14, 15, 16, 17, 19, 20, 24), (5, 6, 8, 9, 12, 14, 15), (20, 22, 25, 26, 28, 30, 31, 35, 40), (4, 8, 9, 12, 15, 16, 18, 22, 23, 27, 30)])
def _(v):
    n = len(v)
    k = -(-n // 4)
    q1 = v[k - 1]
    md = F(v[n // 2]) if n % 2 else F(v[n // 2 - 1] + v[n // 2], 2)
    q3 = v[-(-3 * n // 4) - 1]
    return (rf"Voici une série rangée dans l'ordre croissant : ${'\\ ;\\ '.join(map(str, v))}$. Quel est son premier quartile $Q_1$ ?",
            m(nb(q1)), [m(nb(md)), m(nb(q3)), m(nb(v[k])), m(nb(v[0]))])


# ============================================================ FONCTIONS
@qtype("fon", "Remplace x par sa valeur entre parenthèses et respecte les priorités : le carré d'abord.",
       [(2, -3, 1, -2), (1, 4, -5, 3), (-1, 2, 6, -3), (3, 0, -7, 2), (-2, -1, 4, 1), (1, -6, 9, 5), (4, 1, -2, -1), (2, 5, -3, -4)])
def _(p):
    a, b, c, x = p
    v = a * x * x + b * x + c
    return (rf"Soit $f(x)={expr([(a, 'x^2'), (b, 'x'), (c, '')])}$. Que vaut $f({nb(x)})$ ?",
            m(nb(v)), [m(nb(-a * x * x + b * x + c)), m(nb(a * 2 * x + b * x + c)), m(nb(-v) if v else "1"), m(nb(v + 2))])


@qtype("fon", "Un antécédent de c est un nombre x tel que f(x) = c : résous l'équation.",
       [(2, 3, 11), (-3, 5, -1), (4, -7, 5), (5, 2, -8), (-2, 9, 15), (3, -4, -4), (6, 1, 4), (-5, -2, 8)])
def _(p):
    a, b, c = p
    x = F(c - b, a)
    return (rf"Soit $f(x)={lin(a, b)}$. Quel est l'antécédent de ${c}$ par $f$ ?",
            m(lf(x)), [m(nb(a * c + b)), m(lf(F(c + b, a))), m(nb((c - b) * a)), m(lf(x + 1))])


@qtype("fon", "Coefficient directeur de (AB) = (y_B − y_A) ÷ (x_B − x_A).",
       [((1, 2), (3, 8)), ((-2, 5), (2, -3)), ((0, 1), (4, 3)), ((1, -4), (5, 6)), ((-3, -1), (1, 7)), ((2, 6), (8, -3)), ((-1, 0), (2, 9)), ((4, 5), (7, 5))])
def _(p):
    A, B = p
    mm = F(B[1] - A[1], B[0] - A[0])
    inv = F(B[0] - A[0], B[1] - A[1]) if B[1] != A[1] else F(1)
    return (rf"Quel est le coefficient directeur de la droite $(AB)$, avec $A{pt(A)}$ et $B{pt(B)}$ ?",
            m(lf(mm)), [m(lf(inv)), m(lf(-mm) if mm else "1"), m(lf(F(B[1] + A[1], B[0] + A[0])) if B[0] + A[0] else "2"), m(lf(mm + 1))])


@qtype("fon", "y = mx + p : remplace x et y par les coordonnées du point pour trouver p.",
       [(2, (1, 5)), (-3, (2, 1)), (F(1, 2), (4, 0)), (4, (-1, -2)), (-1, (3, 3)), (5, (0, -4)), (-2, (-2, 1)), (3, (2, -1))])
def _(p):
    mm, (x0, y0) = p
    mm = F(mm)
    Y = lambda a, b: m("y=" + expr([(a, "x"), (b, "")]))
    pp = y0 - mm * x0
    return (rf"Quelle est l'équation réduite de la droite de coefficient directeur ${lf(mm)}$ passant par $A{pt((x0, y0))}$ ?",
            Y(mm, pp), [Y(mm, y0 + mm * x0), Y(mm, y0), Y(x0, pp) if x0 not in (0, mm) else Y(mm, pp + 1), Y(mm, -pp) if pp else Y(mm, 1), Y(-mm, pp), Y(pp, mm) if pp != mm else Y(mm, pp - 1)])


@qtype("fon", "ax + b > 0 : si a > 0, x > −b/a ; si a < 0, le sens de l'inégalité change : x < −b/a.",
       [(2, -6), (-3, 12), (5, 10), (-4, -8), (1, -7), (-2, 5), (3, 1), (-1, -3)])
def _(p):
    a, b = p
    r = F(-b, a)
    g, l = rf"x>{lf(r)}", rf"x<{lf(r)}"
    return (rf"Pour quels réels $x$ a-t-on ${lin(a, b)}>0$ ?", m(g if a > 0 else l),
            [m(l if a > 0 else g), m(rf"x>{lf(-r)}") if r else m(r"x>1"), m(rf"x<{lf(-r)}") if r else m(r"x<1")])


@qtype("fon", "x² = k a deux solutions √k et −√k si k > 0, une seule (0) si k = 0, aucune si k < 0.",
       [9, 25, -4, 0, 2, 49, -1, 12])
def _(k):
    S = lambda s: m(r"\{" + s + r"\}")
    if k > 0:
        ans = S(rf"-{sqs(k)}\,;\,{sqs(k)}")
        dis = [S(sqs(k)), S(rf"-{k}\,;\,{k}"), "aucune solution"]
    elif k == 0:
        ans, dis = S("0"), ["aucune solution", S(r"-1\,;\,1"), S(r"0\,;\,1")]
    else:
        ans, dis = "aucune solution", [S(rf"-{sqs(-k)}\,;\,{sqs(-k)}"), S(rf"-{sqs(-k)}"), S(str(k)), S(sqs(-k)), S("0")]
    return (rf"Quelles sont les solutions de l'équation $x^2={k}$ ?", ans, dis)


@qtype("fon", "Une fonction affine f(x) = ax + b est croissante si a > 0, décroissante si a < 0, constante si a = 0.",
       [(-3, 5), (2, -1), (0, 4), (F(-1, 2), 2), (7, 0), (1, -3), (-4, -4), (0, -2)])
def _(p):
    a, b = p
    a = F(a)
    nat = "croissante" if a > 0 else "décroissante" if a < 0 else "constante"
    f = expr([(a, "x"), (b, "")]) if a else nb(b)
    return (rf"Quel est le sens de variation de la fonction $f(x)={f}$ sur $\mathbb{{R}}$ ?", f"{nat} sur $\\mathbb{{R}}$",
            [f"{x} sur $\\mathbb{{R}}$" for x in ["croissante", "décroissante", "constante"] if x != nat] + ["croissante puis décroissante"])


@qtype("fon", "Regroupe les x d'un côté ; si tu divises par un nombre négatif, change le sens de l'inégalité.",
       [(3, 2, 1, 10), (2, 5, 5, -4), (-1, 4, 2, -8), (4, -3, 1, 6), (1, 7, 3, 1), (5, 0, 2, -9), (-2, 1, 1, -5), (6, -1, 2, 7)])
def _(p):
    a, b, c, d = p
    k, r = a - c, F(d - b, a - c)
    le, ge = rf"x\leqslant{lf(r)}", rf"x\geqslant{lf(r)}"
    return (rf"Quelles sont les solutions de l'inéquation ${lin(a, b)}\leqslant{lin(c, d)}$ ?",
            m(le if k > 0 else ge), [m(ge if k > 0 else le), m(rf"x\leqslant{lf(F(d + b, a - c))}"), m(rf"x\geqslant{lf(-r)}") if r else m(r"x\geqslant1"), m(rf"x\leqslant{lf(r + 1)}"), m(rf"x<{lf(r)}")])


# ============================================================ VECTEURS ET REPÉRAGE
def vc(v):
    return rf"\begin{{pmatrix}}{nb(v[0])}\\{nb(v[1])}\end{{pmatrix}}"


PAIRS = [((1, 2), (4, -3)), ((-2, 5), (3, 1)), ((0, -4), (-3, 2)), ((6, 1), (2, 7)), ((-5, -2), (1, -6)), ((3, 3), (-1, 8)), ((2, -7), (7, -2)), ((-4, 0), (0, 5))]


@qtype("vec", "Les coordonnées de AB→ sont (x_B − x_A ; y_B − y_A).", PAIRS)
def _(p):
    A, B = p
    d = (B[0] - A[0], B[1] - A[1])
    return (rf"Dans un repère, $A{pt(A)}$ et $B{pt(B)}$. Quelles sont les coordonnées du vecteur $\overrightarrow{{AB}}$ ?",
            m(pt(d)), [m(pt((-d[0], -d[1]))), m(pt((A[0] + B[0], A[1] + B[1]))), m(pt((d[1], d[0]))) if d[0] != d[1] else m(pt((d[0], -d[1])))])


@qtype("vec", "Le milieu de [AB] a pour coordonnées les moyennes : ((x_A + x_B)/2 ; (y_A + y_B)/2).",
       [((1, 2), (5, -4)), ((-2, 5), (4, 1)), ((0, -3), (-6, 7)), ((3, 3), (8, -1)), ((-5, -2), (1, 6)), ((2, 9), (-4, 1)), ((7, -2), (3, 4)), ((-1, 0), (6, 5))])
def _(p):
    A, B = p
    M = (F(A[0] + B[0], 2), F(A[1] + B[1], 2))
    return (rf"Dans un repère, $A{pt(A)}$ et $B{pt(B)}$. Quelles sont les coordonnées du milieu de $[AB]$ ?",
            m(pt(M)), [m(pt((F(B[0] - A[0], 2), F(B[1] - A[1], 2)))), m(pt((A[0] + B[0], A[1] + B[1]))), m(pt((M[0], F(A[1] - B[1], 2)))) if A[1] != B[1] else m(pt((M[0], M[1] + 1)))])


@qtype("vec", "Dans un repère orthonormé, AB = √((x_B − x_A)² + (y_B − y_A)²).",
       [((1, 2), (4, 6)), ((-2, 1), (3, 13)), ((0, 0), (2, 3)), ((-3, 4), (3, -4)), ((2, 5), (4, 1)), ((-1, -2), (7, 4)), ((0, 3), (1, 1)), ((6, -2), (1, 10))])
def _(p):
    A, B = p
    dx, dy = B[0] - A[0], B[1] - A[1]
    d2 = dx * dx + dy * dy
    return (rf"Dans un repère orthonormé, $A{pt(A)}$ et $B{pt(B)}$. Quelle est la distance $AB$ ?",
            m(sqs(d2)), [m(nb(d2)), m(nb(abs(dx) + abs(dy))), m(sqs(abs(dx * dx - dy * dy))) if dx * dx != dy * dy else m(sqs(d2 + 1)), m(sqs(d2 + 2))])


@qtype("vec", "u(a ; b) et v(c ; d) sont colinéaires si et seulement si ad − bc = 0.",
       [(2, 3, 9), (4, -2, 5), (1, 5, -10), (-3, 6, 4), (6, 4, 10), (5, 2, -3), (-2, -8, 12), (3, 1, 7)])
def _(p):
    a, b, c = p
    r = F(a * c, b)
    return (rf"Pour quelle valeur de $k$ les vecteurs $\vec u{vc((a, b))}$ et $\vec v\begin{{pmatrix}}k\\{c}\end{{pmatrix}}$ sont-ils colinéaires ?",
            m("k=" + lf(r)), [m("k=" + lf(F(b * c, a))), m("k=" + lf(-r)), m("k=" + lf(F(a + c - b))) if F(a + c - b) != r else m("k=" + lf(r + 1))])


@qtype("vec", "Les coordonnées de ku + k'v sont (k x + k' x' ; k y + k' y').",
       [((1, 2), (3, -1), 2, 1), ((4, -3), (1, 2), 1, -2), ((-2, 5), (0, 3), 3, 1), ((2, 2), (-1, 4), -1, 2),
        ((3, -1), (2, 5), 2, -3), ((0, 4), (5, -2), 1, 3), ((-3, 1), (2, 2), -2, 1), ((5, 0), (-1, -3), 1, 2)])
def _(p):
    u_, v_, k1, k2 = p
    w = (k1 * u_[0] + k2 * v_[0], k1 * u_[1] + k2 * v_[1])
    combo = expr([(k1, r"\vec u"), (k2, r"\vec v")])
    return (rf"On donne $\vec u{vc(u_)}$ et $\vec v{vc(v_)}$. Quelles sont les coordonnées du vecteur ${combo}$ ?",
            m(pt(w)), [m(pt((u_[0] + v_[0], u_[1] + v_[1]))), m(pt((k1 * u_[0] + v_[0], k1 * u_[1] + v_[1]))) if k2 != 1 else m(pt((u_[0] + k2 * v_[0], u_[1] + k2 * v_[1]))),
                       m(pt((k1 * u_[0] - k2 * v_[0], k1 * u_[1] - k2 * v_[1]))), m(pt((w[1], w[0]))) if w[0] != w[1] else m(pt((w[0] + 1, w[1])))])


@qtype("vec", "Le déterminant de u(x ; y) et v(x' ; y') vaut x y' − y x'.",
       [((2, 3), (4, 1)), ((-1, 5), (2, -3)), ((3, -2), (6, -4)), ((4, 1), (-2, 5)), ((0, 3), (2, 7)), ((5, -1), (3, 2)), ((-2, -4), (1, 2)), ((1, 6), (3, -2))])
def _(p):
    (x, y), (x2, y2) = p
    d = x * y2 - y * x2
    return (rf"Que vaut le déterminant $\det(\vec u,\vec v)$ pour $\vec u{vc((x, y))}$ et $\vec v{vc((x2, y2))}$ ?",
            m(nb(d)), [m(nb(x * y2 + y * x2)), m(nb(x * x2 + y * y2)), m(nb(-d)) if d else m("1"), m(nb(d + 1))])


@qtype("vec", "ABCD est un parallélogramme si et seulement si AB→ = DC→ : donc D = A + C − B.",
       [((1, 1), (4, 2), (5, 5)), ((-2, 0), (1, 3), (0, 6)), ((0, -1), (3, -2), (4, 2)), ((2, 3), (6, 1), (5, -2)),
        ((-3, -2), (0, -4), (2, 1)), ((1, 4), (2, 0), (6, 1)), ((-1, 2), (3, 5), (4, 1)), ((5, 0), (2, -3), (-1, 1))])
def _(p):
    A, B, C = p
    D_ = (A[0] + C[0] - B[0], A[1] + C[1] - B[1])
    return (rf"Dans un repère, $A{pt(A)}$, $B{pt(B)}$ et $C{pt(C)}$. Quelles sont les coordonnées du point $D$ tel que $ABCD$ soit un parallélogramme ?",
            m(pt(D_)), [m(pt((B[0] + C[0] - A[0], B[1] + C[1] - A[1]))), m(pt((A[0] + B[0] - C[0], A[1] + B[1] - C[1]))), m(pt((F(A[0] + C[0], 2), F(A[1] + C[1], 2))))])


@qtype("vec", "Résous par substitution ou par combinaison (additionne ou soustrais les équations).",
       [((1, 1, 1, -1), (3, 1)), ((2, 1, 1, -1), (2, -1)), ((1, 2, 3, -1), (-1, 2)), ((3, 1, 1, 1), (4, -3)),
        ((1, -1, 2, 3), (5, 2)), ((4, 1, 1, -2), (1, 3)), ((1, 3, 2, 1), (-2, 1)), ((2, -3, 1, 1), (3, 1))])
def _(p):
    (a, b, c, d), (x, y) = p
    e1 = expr([(a, "x"), (b, "y")]) + f"={nb(a * x + b * y)}"
    e2 = expr([(c, "x"), (d, "y")]) + f"={nb(c * x + d * y)}"
    S = rf"\left\{{\begin{{array}}{{l}}{e1}\\{e2}\end{{array}}\right."
    return (rf"Quel est le couple solution du système ${S}$ ?", m(pt((x, y))), [m(pt((y, x))) if x != y else m(pt((x, -y))), m(pt((x, -y))), m(pt((-x, y))), m(pt((x + 1, y)))])


# ============================================================ ARITHMÉTIQUE ET ENSEMBLES
@qtype("ari", "Un nombre premier n'a que deux diviseurs : 1 et lui-même. Teste les divisions par 2, 3, 5, 7…",
       [(97, [91, 87, 93]), (53, [51, 57, 49]), (89, [81, 87, 91]), (61, [63, 51, 57]), (101, [111, 121, 91]), (73, [77, 69, 81]), (113, [117, 119, 111]), (67, [69, 77, 87])])
def _(p):
    a, dis = p
    isp = lambda n: n > 1 and all(n % k for k in range(2, int(n ** .5) + 1))
    assert isp(a) and not any(isp(x) for x in dis)
    return ("Lequel de ces nombres est premier ?", m(nb(a)), [m(nb(x)) for x in dis])


def factor(n):
    fs, k = [], 2
    while n > 1:
        e = 0
        while n % k == 0:
            n //= k; e += 1
        if e:
            fs.append((k, e))
        k += 1
    return fs


def fstr(fs):
    return r"\times".join(str(p) if e == 1 else f"{p}^{{{e}}}" for p, e in fs)


@qtype("ari", "Divise successivement par les nombres premiers 2, 3, 5, 7… autant de fois que possible.",
       [360, 84, 150, 1000, 252, 90, 196, 330])
def _(N):
    fs = factor(N)
    a1 = fs[:]; a1[0] = (a1[0][0], a1[0][1] + 1)
    a2 = fs[:]; a2[-1] = (a2[-1][0], a2[-1][1] + 1)
    p0 = fs[0][0] ** fs[0][1]
    return (rf"Quelle est la décomposition de ${nb(N)}$ en produit de facteurs premiers ?",
            m(fstr(fs)), [m(fstr(a1)), m(fstr(a2)), m(rf"{p0 * fs[1][0]}\times{N // (p0 * fs[1][0])}")])


SETS = [r"\mathbb{N}", r"\mathbb{Z}", r"\mathbb{D}", r"\mathbb{Q}", r"\mathbb{R}"]


@qtype("ari", "ℕ ⊂ ℤ ⊂ 𝔻 ⊂ ℚ ⊂ ℝ : 𝔻 contient les nombres décimaux, ℚ les quotients d'entiers.",
       [("-7", 1), ("\\dfrac{3}{4}", 2), ("\\dfrac{1}{3}", 3), ("\\sqrt{2}", 4), ("\\sqrt{49}", 0), ("-2{,}5", 2), ("\\dfrac{22}{7}", 3), ("\\pi", 4)])
def _(p):
    x, k = p
    return (rf"Quel est le plus petit ensemble de nombres auquel appartient ${x}$ ?", m(SETS[k]), [m(s) for i, s in enumerate(SETS) if i != k][:4])


@qtype("ari", "Divise le numérateur et le dénominateur par leur plus grand diviseur commun.",
       [(84, 126), (45, 75), (60, 144), (98, 70), (36, 120), (150, 210), (24, 108), (132, 99)])
def _(p):
    a, b = p
    from math import gcd
    g = gcd(a, b)
    raw = [rf"\dfrac{{{a // d}}}{{{b // d}}}" for d in (2, 3, 5, 7) if a % d == 0 and b % d == 0 and d != g]
    return (rf"Quelle est la forme irréductible de $\dfrac{{{a}}}{{{b}}}$ ?", m(rf"\dfrac{{{a // g}}}{{{b // g}}}"),
            [m(x) for x in raw] + [m(rf"\dfrac{{{b // g}}}{{{a // g}}}"), m(rf"\dfrac{{{a // g + 1}}}{{{b // g + 1}}}")])


@qtype("ari", "2k est toujours pair et 2k + 1 toujours impair ; deux entiers consécutifs comptent toujours un pair.",
       [("2n+4", "pair"), ("2n+1", "impair"), ("n(n+1)", "pair"), ("2n+3", "impair"), ("4n+2", "pair"), ("n^2+n+1", "impair"), ("6n", "pair"), ("2n-1", "impair")])
def _(p):
    e, nat = p
    opts_ = {"pair": "il est toujours pair", "impair": "il est toujours impair"}
    return (rf"Pour tout entier naturel $n$, que peut-on dire de l'entier ${e}$ ?", opts_[nat],
            [opts_["impair" if nat == "pair" else "pair"], "il est pair ou impair selon $n$", "il est toujours premier"])


@qtype("ari", "Les multiples de k entre 1 et N sont k, 2k, 3k… : il y en a autant que la partie entière de N ÷ k.",
       [(7, 100), (9, 200), (12, 150), (5, 73), (11, 500), (4, 99), (13, 300), (6, 1000)])
def _(p):
    k, N = p
    c = N // k
    return (rf"Combien y a-t-il de multiples de ${k}$ compris entre $1$ et ${nb(N)}$ ?", m(nb(c)), [m(nb(c + 1)), m(nb(c - 1)), m(nb(N - c))])


@qtype("ari", "Cherche les diviseurs par paires : pour 36 → 1 × 36, 2 × 18, 3 × 12, 4 × 9, 6 × 6.",
       [36, 24, 49, 72, 17, 64, 18, 100])
def _(N):
    d = sum(1 for i in range(1, N + 1) if N % i == 0)
    return (rf"Combien l'entier ${N}$ a-t-il de diviseurs positifs ?", m(nb(d)), [m(nb(d - 1)), m(nb(d + 1)), m(nb(d + 2)) if d + 2 != N else m(nb(d * 2))])


@qtype("ari", "L'intersection I ∩ J contient les nombres qui sont à la fois dans I et dans J.",
       [("[-3;5]", "[1;8]", "[1;5]", ["[-3;8]", "[1;8]", "[-3;5]"]), ("[0;4[", "[2;9]", "[2;4[", ["[0;9]", "[2;4]", "]2;4["]),
        ("]-inf;3]", "[-1;+inf[", "[-1;3]", ["]-inf;+inf[", "]-1;3[", "[3;+inf["]), ("[-5;2]", "]0;6]", "]0;2]", ["[-5;6]", "[0;2]", "]0;2["]),
        ("[1;7]", "[3;4]", "[3;4]", ["[1;7]", "[1;3]", "[4;7]"]), ("]-2;6[", "[-4;1]", "]-2;1]", ["[-4;6[", "[-2;1]", "]-2;1["]),
        ("[-1;10]", "]5;+inf[", "]5;10]", ["[-1;+inf[", "[5;10]", "]5;10["]), ("[2;9[", "]-inf;5[", "[2;5[", ["]-inf;9[", "[2;5]", "]2;5["])])
def _(p):
    I, J, ans, dis = p
    T = lambda s: m(s.replace(";", r"\,;\,").replace("-inf", r"-\infty").replace("+inf", r"+\infty"))
    return (rf"Que vaut l'intersection ${I.replace(';', r'\,;\,').replace('-inf', r'-\infty').replace('+inf', r'+\infty')}\cap{J.replace(';', r'\,;\,').replace('-inf', r'-\infty').replace('+inf', r'+\infty')}$ ?",
            T(ans), [T(x) for x in dis])


# ============================================================ PROBABILITÉS
def pr(x, d):
    return nb(x) if d else lf(x)


@qtype("pro", "P(A ∪ B) = P(A) + P(B) − P(A ∩ B).",
       [(F(3, 10), F(5, 10), F(1, 10)), (F(40, 100), F(35, 100), F(15, 100)), (F(25, 100), F(60, 100), F(20, 100)), (F(12, 100), F(40, 100), F(8, 100)),
        (F(7, 10), F(2, 10), F(1, 10)), (F(6, 10), F(6, 10), F(45, 100)), (F(35, 100), F(25, 100), F(5, 100)), (F(5, 10), F(45, 100), F(3, 10))])
def _(p):
    a, b, c = p
    return (rf"On a $P(A)={nb(a)}$, $P(B)={nb(b)}$ et $P(A\cap B)={nb(c)}$. Que vaut $P(A\cup B)$ ?",
            m(nb(a + b - c)), [m(nb(a + b)) if a + b <= 1 else m(nb(a + b - 2 * c)), m(nb(a + b + c)) if a + b + c <= 1 else m(nb(a * b)), m(nb(c)), m(nb(a * b))])


@qtype("pro", "P(A ∩ B) = P(A) + P(B) − P(A ∪ B).",
       [(F(5, 10), F(4, 10), F(7, 10)), (F(3, 10), F(6, 10), F(8, 10)), (F(25, 100), F(5, 10), F(6, 10)), (F(6, 10), F(55, 100), F(85, 100)),
        (F(2, 10), F(3, 10), F(45, 100)), (F(8, 10), F(5, 10), F(95, 100)), (F(4, 10), F(4, 10), F(65, 100)), (F(35, 100), F(45, 100), F(7, 10))])
def _(p):
    a, b, c = p
    return (rf"On a $P(A)={nb(a)}$, $P(B)={nb(b)}$ et $P(A\cup B)={nb(c)}$. Que vaut $P(A\cap B)$ ?",
            m(nb(a + b - c)), [m(nb(a * b)), m(nb(c - a)), m(nb(c - b)) if c - b != c - a else m(nb(1 - c)), m(nb(a + b - c + F(1, 10))), m(nb(c)), m(nb(a + b - c + F(2, 10)))])


@qtype("pro", "P(Ā) = 1 − P(A).",
       [F(3, 8), F(2, 9), F(7, 12), F(1, 6), F(4, 15), F(5, 11), F(9, 20), F(13, 16)])
def _(q):
    return (rf"On a $P(A)={lf(q)}$. Que vaut $P(\overline{{A}})$, la probabilité de l'événement contraire ?",
            m(lf(1 - q)), [m(lf(q)), m(lf(1 / q)) if 1 / q != 1 - q else m(lf(q / 2)), m(lf((1 - q) / 2)), m(lf(1 - q / 2))])


@qtype("pro", "Liste les faces qui réalisent l'événement, puis divise par 6.",
       [("pair ou multiple de 3", {2, 3, 4, 6}), ("supérieur à 4 et pair", {6}), ("premier", {2, 3, 5}), ("impair ou supérieur à 4", {1, 3, 5, 6}),
        ("diviseur de 12", {1, 2, 3, 4, 6}), ("pair et inférieur à 5", {2, 4}), ("ni pair ni multiple de 3", {1, 5}), ("multiple de 3 ou égal à 1", {1, 3, 6})])
def _(p):
    txt, S = p
    k = len(S)
    return (rf"On lance un dé équilibré à six faces. Quelle est la probabilité d'obtenir un nombre {txt} ?",
            m(lf(F(k, 6))), [m(lf(F(k + 1, 6))), m(lf(F(k - 1, 6))) if k > 1 else m(lf(F(1, 3))), m(lf(F(6 - k, 6))) if 6 - k != k else m(lf(F(1, 3))), m(lf(F(k, 5)))])


@qtype("pro", "Avec n pièces, il y a 2ⁿ issues équiprobables ; « au moins un » est le contraire de « aucun ».",
       [(2, "que"), (3, "que"), (2, "au"), (3, "au"), (4, "que"), (4, "au"), (5, "que"), (5, "au")])
def _(p):
    n, w = p
    q = F(1, 2 ** n)
    r = q if w == "que" else 1 - q
    t = "de n'obtenir que des PILE" if w == "que" else "d'obtenir au moins une fois FACE"
    return (rf"On lance ${n}$ pièces équilibrées. Quelle est la probabilité {t} ?",
            m(lf(r)), [m(lf(1 - r)), m(lf(F(1, 2 * n))) if F(1, 2 * n) != r else m(lf(F(n, 2 ** n))), m(lf(F(1, 2))), m(lf(F(n, 2 ** n))), m(lf(F(1, 2 ** (n + 1)))), m(lf(F(1, n)))])


@qtype("pro", "La somme des probabilités de toutes les issues vaut 1.",
       [(F(2, 10), F(35, 100), F(1, 10)), (F(15, 100), F(4, 10), F(25, 100)), (F(3, 10), F(3, 10), F(12, 100)), (F(5, 100), F(6, 10), F(15, 100)),
        (F(45, 100), F(2, 10), F(1, 10)), (F(1, 10), F(1, 10), F(5, 10)), (F(32, 100), F(18, 100), F(4, 10)), (F(25, 100), F(25, 100), F(3, 10))])
def _(p):
    a, b, c = p
    x = 1 - a - b - c
    T = r"\begin{array}{|l|c|c|c|c|}\hline \text{Issue} & 1 & 2 & 3 & 4\\\hline \text{Probabilité} & " + f"{nb(a)} & {nb(b)} & ? & {nb(c)}" + r"\\\hline\end{array}"
    return (rf"Voici la loi de probabilité d'une expérience aléatoire. Quelle est la probabilité manquante ? ${T}$",
            m(nb(x)), [m(nb(a + b + c)), m(nb(1 - a - b)), m(nb(F(1, 4))) if x != F(1, 4) else m(nb(F(1, 2))), m(nb(x + F(1, 10)))])


@qtype("pro", "Avec remise, les deux tirages sont identiques et indépendants : on multiplie les probabilités.",
       [(3, 5), (2, 6), (4, 10), (1, 4), (5, 8), (3, 10), (6, 9), (7, 10)])
def _(p):
    r, N = p
    q = F(r, N)
    return (rf"Une urne contient ${N}$ boules dont ${r}$ rouges. On tire une boule, on la remet, puis on en tire une deuxième. Quelle est la probabilité de tirer deux boules rouges ?",
            m(lf(q * q)), [m(lf(min(F(1), 2 * q))), m(lf(q)), m(lf(q * F(r - 1, N - 1))) if r > 1 else m(lf(q / 2)), m(lf(1 - q * q))])


@qtype("pro", "Si A et B sont incompatibles (ne peuvent pas se produire en même temps), P(A ∪ B) = P(A) + P(B).",
       [(F(3, 10), F(45, 100), True), (F(1, 4), F(1, 3), False), (F(15, 100), F(6, 10), True), (F(2, 5), F(1, 6), False),
        (F(8, 100), F(5, 10), True), (F(1, 8), F(3, 4), False), (F(22, 100), F(3, 10), True), (F(2, 9), F(1, 3), False)])
def _(p):
    a, b, d = p
    return (rf"$A$ et $B$ sont deux événements incompatibles, avec $P(A)={pr(a, d)}$ et $P(B)={pr(b, d)}$. Que vaut $P(A\cup B)$ ?",
            m(pr(a + b, d)), [m(pr(a * b, d)), m(pr(a + b - a * b, d)), m(pr(abs(a - b), d)), m(pr(1 - a - b, d))])


# ============================================================ BUILD
THEMES = {"nom": ("Nombres et calculs", "1F6FA8"), "sta": ("Évolutions et statistiques", "C77F0A"),
          "fon": ("Fonctions", "6A4C93"), "vec": ("Vecteurs et repérage", "C0503A"),
          "ari": ("Arithmétique et ensembles de nombres", "2E7D6B"), "pro": ("Probabilités", "8A5A2B")}
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
open(f"{OUT}/seconde.tex", "w", encoding="utf-8").write("\n".join(tex).replace("\\leqslant", "\\leqslant ").replace("\\geqslant", "\\geqslant "))
json.dump([[n, th, g, h] for n, th, g, _, h in KEY], open(f"{OUT}/questions.json", "w"))
json.dump([t[3] for t in TYPES], open(f"{OUT}/hints.json", "w"), ensure_ascii=False, indent=0)
with open(f"{OUT}/corrige.txt", "w", encoding="utf-8") as f:
    for n, th, g, a, h in KEY:
        f.write(f"Q{n if n <= HALF else str((n - 1) % HALF + 1) + ' ' + 'ABCD'[(n - 1) // HALF]} ({THEMES[th][0]}) : {g}) {a}\n")
print(len(KEY), "questions ; fallback:", FALLBACK)
