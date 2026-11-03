from math import gcd


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


# ============================================================ ARITHMÉTIQUE ET PUISSANCES
@qtype("ari", "Un nombre premier a exactement deux diviseurs : 1 et lui-même. Teste les divisions par 2, 3, 5, 7, 11…",
       [(79, [77, 81, 85]), (59, [57, 63, 65]), (83, [87, 91, 93]), (71, [69, 75, 77]), (103, [105, 111, 117]), (47, [49, 51, 57]), (109, [119, 121, 99]), (43, [39, 45, 51])])
def _(p):
    a, dis = p
    isp = lambda n: n > 1 and all(n % k for k in range(2, int(n ** .5) + 1))
    assert isp(a) and not any(isp(x) for x in dis)
    return ("Lequel de ces nombres est premier ?", m(nb(a)), [m(nb(x)) for x in dis])


@qtype("ari", "Divise successivement par 2, 3, 5, 7… tant que c'est possible.",
       [120, 98, 126, 600, 180, 132, 225, 280])
def _(N):
    fs = factor(N)
    a1 = fs[:]; a1[0] = (a1[0][0], a1[0][1] + 1)
    a2 = fs[:]; a2[-1] = (a2[-1][0], a2[-1][1] + 1)
    p0 = fs[0][0] ** fs[0][1]
    return (rf"Quelle est la décomposition de ${nb(N)}$ en produit de facteurs premiers ?",
            m(fstr(fs)), [m(fstr(a1)), m(fstr(a2)), m(rf"{p0 * fs[1][0]}\times{N // (p0 * fs[1][0])}")])


@qtype("ari", "Décompose le numérateur et le dénominateur en facteurs premiers, puis simplifie les facteurs communs.",
       [(126, 180), (90, 252), (150, 375), (84, 196), (210, 330), (132, 220), (72, 270), (264, 360)])
def _(p):
    a, b = p
    g = gcd(a, b)
    raw = [rf"\dfrac{{{a // d}}}{{{b // d}}}" for d in (2, 3, 5, 7) if a % d == 0 and b % d == 0 and d != g]
    return (rf"Quelle est la forme irréductible de $\dfrac{{{a}}}{{{b}}}$ ?", m(rf"\dfrac{{{a // g}}}{{{b // g}}}"),
            [m(x) for x in raw] + [m(rf"\dfrac{{{b // g}}}{{{a // g}}}"), m(rf"\dfrac{{{a // g + 1}}}{{{b // g + 1}}}")])


@qtype("ari", "Le plus grand diviseur commun s'obtient avec les facteurs premiers communs aux deux décompositions.",
       [(84, 126), (60, 90), (72, 120), (105, 75), (48, 180), (96, 144), (66, 110), (150, 225)])
def _(p):
    a, b = p
    g = gcd(a, b)
    return (rf"Quel est le plus grand diviseur commun à ${a}$ et ${b}$ ?", m(nb(g)), [m(nb(g // 2)) if g % 2 == 0 else m(nb(g * 2)), m(nb(g * 2)) if g % 2 == 0 else m(nb(g // 3 if g % 3 == 0 else g + 1)), m(nb(a * b // g)), m(nb(g + 1))])


@qtype("ari", "Le nombre maximal de paquets identiques est le plus grand diviseur commun des deux quantités.",
       [(60, 84), (48, 72), (90, 126), (75, 105), (64, 96), (54, 81), (120, 150), (36, 132)])
def _(p):
    a, b = p
    g = gcd(a, b)
    return (rf"Un fleuriste a ${a}$ roses et ${b}$ tulipes. Il veut faire le plus grand nombre de bouquets identiques en utilisant toutes les fleurs. Combien de bouquets peut-il faire ?",
            m(nb(g)), [m(nb(g // 2)) if g % 2 == 0 else m(nb(g * 3)), m(nb(a + b)), m(nb(g * 2)), m(nb(a // g + b // g))])


@qtype("ari", "Liste les multiples de chaque nombre jusqu'au premier qui est commun aux deux.",
       [(6, 8), (4, 10), (9, 12), (15, 20), (8, 14), (12, 18), (10, 25), (6, 21)])
def _(p):
    a, b = p
    l = a * b // gcd(a, b)
    return (rf"Un phare clignote toutes les ${a}$ secondes et un autre toutes les ${b}$ secondes. Ils viennent de clignoter ensemble. Dans combien de secondes clignoteront-ils de nouveau ensemble ?",
            u(nb(l), "s"), [u(nb(a * b), "s") if a * b != l else u(nb(l * 2), "s"), u(nb(a + b), "s"), u(nb(gcd(a, b)), "s"), u(nb(l + a), "s")])


@qtype("ari", "Multiplie les nombres entre eux et les puissances de 10 entre elles, puis écris le résultat en notation scientifique.",
       [((3, 5), (2, -3)), ((4, -2), (2, 6)), ((5, 3), (3, 4)), ((1.5, 7), (4, -2)), ((6, -4), (5, -3)), ((2.5, 2), (4, 5)), ((8, 3), (3, -8)), ((7, -1), (2, 9))])
def _(p):
    (a, e1), (b, e2) = p
    pr_ = F(str(a)) * F(str(b)); e = e1 + e2
    while pr_ >= 10:
        pr_ /= 10; e += 1
    S = lambda mm, k: m(rf"{nb(mm)}\times10^{{{k}}}")
    return (rf"Que vaut $({nb(F(str(a)))}\times10^{{{e1}}})\times({nb(F(str(b)))}\times10^{{{e2}}})$, en notation scientifique ?",
            S(pr_, e), [S(pr_, e1 * e2) if e1 * e2 != e else S(pr_, e + 2), S(pr_, e - 1), S(pr_ * 10, e - 1) if pr_ * 10 != pr_ else S(pr_, e + 1), S(F(str(a)) + F(str(b)), e1 + e2)])


@qtype("ari", "a⁻ⁿ = 1 ÷ aⁿ : un exposant négatif ne rend pas le nombre négatif.",
       [(5, 2), (2, 3), (10, 3), (4, 2), (2, 5), (20, 1), (8, 1), (5, 3)])
def _(p):
    a, n = p
    v = F(1, a ** n)
    return (rf"Quelle est l'écriture décimale de ${a}^{{-{n}}}$ ?", m(nb(v)), [m(nb(-a ** n)), m(nb(-a * n)), m(nb(F(1, a * n))) if F(1, a * n) != v else m(nb(v * 10)), m(nb(v / 10))])


# ============================================================ CALCUL LITTÉRAL ET ÉQUATIONS
@qtype("lit", "(a + b)(c + d) = ac + ad + bc + bd, puis réduis.",
       [((2, 3), (1, -4)), ((3, -1), (2, 5)), ((1, 6), (4, -2)), ((5, -2), (1, -3)), ((-2, 1), (3, 4)), ((4, 5), (2, -1)), ((1, -7), (3, 2)), ((-3, 2), (-1, 5))])
def _(p):
    (a, b), (c, d) = p
    Q = lambda c2, c1, c0: m(expr([(c2, "x^2"), (c1, "x"), (c0, "")]))
    return (rf"Développer et réduire $({lin(a, b)})({lin(c, d)})$.", Q(a * c, a * d + b * c, b * d),
            [Q(a * c, 0, b * d), Q(a * c, a * d - b * c, b * d) if b * c else Q(a * c, a * d + 1, b * d), Q(a + c, a * d + b * c, b * d), Q(a * c, a * d + b * c, b + d)])


@qtype("lit", "a² − b² = (a − b)(a + b).",
       [(1, 6), (3, 2), (1, 10), (2, 7), (5, 3), (4, 1), (1, 9), (6, 5)])
def _(p):
    k, a = p
    e = expr([(k * k, "x^2"), (-a * a, "")])
    return (rf"Factoriser ${e}$.", m(f"({lin(k, -a)})({lin(k, a)})"),
            [m(f"({lin(k, -a)})^2"), m(f"({lin(k, a)})^2"), m(f"({lin(k, -a * a)})({lin(k, a * a)})") if a > 1 else m(f"({lin(k * k, -1)})({lin(k * k, 1)})")])


def S2(vals):
    vs = sorted(set(vals))
    return m(r"\{" + r"\,;\,".join(lf(v) for v in vs) + r"\}")


@qtype("lit", "Un produit est nul si et seulement si l'un au moins de ses facteurs est nul.",
       [((1, -3), (2, 5)), ((1, 4), (1, -1)), ((3, -6), (1, 2)), ((2, 1), (1, -5)), ((1, 7), (3, -2)), ((4, -1), (1, 3)), ((5, 10), (2, -3)), ((1, -8), (1, 8))])
def _(p):
    (a, b), (c, d) = p
    r1, r2 = F(-b, a), F(-d, c)
    return (rf"Quelles sont les solutions de l'équation $({lin(a, b)})({lin(c, d)})=0$ ?", S2([r1, r2]),
            [S2([-r1, -r2]) if {-r1, -r2} != {r1, r2} else S2([r1, r2 + 1]), S2([F(b), F(d)]) if {F(b), F(d)} != {r1, r2} else S2([r1 * 2, r2 * 2]), S2([r1]), S2([F(-a, b) if b else 1, r2])])


@qtype("lit", "Repère le facteur commun, puis mets-le en facteur et réduis la deuxième parenthèse.",
       [((1, 1), (2, -3), (1, 5)), ((1, -2), (3, 1), (1, 4)), ((2, 1), (1, 6), (1, -2)), ((1, 3), (4, -1), (2, 2)),
        ((3, -1), (1, 2), (1, 5)), ((1, 5), (2, 7), (-1, 1)), ((2, -3), (1, -4), (3, 2)), ((1, -6), (5, 1), (2, -3))])
def _(p):
    (a, b), (c, d), (e, f) = p
    A, B, C = lin(a, b), lin(c, d), lin(e, f)
    return (rf"Factoriser $({A})({B})+({A})({C})$.", m(f"({A})({lin(c + e, d + f)})"),
            [m(f"({A})({lin(c * e, d * f)})"), m(f"({A})^2({lin(c + e, d + f)})"), m(f"({A})({lin(c - e, d - f)})") if (c - e, d - f) != (c + e, d + f) else m(f"({A})({lin(c + e, d + f + 1)})")])


@qtype("lit", "Isole x ; si tu divises par un nombre négatif, l'inégalité change de sens.",
       [(3, -5, 7, ">"), (-2, 4, 10, "<"), (5, 1, -9, ">"), (-4, -3, 9, ">"), (2, 7, 1, "<"), (-1, 6, 2, "<"), (6, -2, 16, ">"), (-3, 8, -1, ">")])
def _(p):
    a, b, c, op = p
    r = F(c - b, a)
    flip = a < 0
    res_op = op if not flip else {">": "<", "<": ">"}[op]
    o2 = {">": "<", "<": ">"}[res_op]
    X = lambda o, v: m(f"x{o}{lf(v)}")
    return (rf"Quelles sont les solutions de l'inéquation ${lin(a, b)}{op}{nb(c)}$ ?", X(res_op, r),
            [X(o2, r), X(res_op, F(c + b, a)) if F(c + b, a) != r else X(res_op, r + 1), X(res_op, -r) if r else X(res_op, 1)])


@qtype("lit", "x² = a admet deux solutions √a et −√a si a > 0, une seule si a = 0, aucune si a < 0.",
       [16, 36, -9, 81, 7, 0, 100, -25])
def _(k):
    S = lambda s: m(r"\{" + s + r"\}")
    if k > 0:
        ans, dis = S(rf"-{sqs(k)}\,;\,{sqs(k)}"), [S(sqs(k)), S(rf"-{nb(F(k, 2))}\,;\,{nb(F(k, 2))}"), "aucune solution"]
    elif k == 0:
        ans, dis = S("0"), ["aucune solution", S(r"-1\,;\,1"), S(r"0\,;\,1")]
    else:
        ans, dis = "aucune solution", [S(rf"-{sqs(-k)}\,;\,{sqs(-k)}"), S(rf"-{sqs(-k)}"), S(nb(k))]
    return (rf"Quelles sont les solutions de l'équation $x^2={nb(k)}$ ?", ans, dis)


@qtype("lit", "Remplace x par le nombre dans chaque membre et compare les deux résultats.",
       [(-2, (1, 3, 2)), (3, (1, -5, 6)), (1, (2, 1, -4)), (-1, (1, -4, -5)), (4, (1, -1, -10)), (2, (3, -2, -8)), (-3, (1, 2, -3)), (5, (1, -6, 4))])
def _(p):
    x, (a, b, c) = p
    v = a * x * x + b * x + c
    ok = v == 0
    return (rf"Le nombre ${nb(x)}$ est-il solution de l'équation ${expr([(a, 'x^2'), (b, 'x'), (c, '')])}=0$ ?",
            "oui" if ok else "non", ["non" if ok else "oui", "on ne peut pas savoir", "seulement si $x$ est positif"])


@qtype("lit", "Suis les étapes dans l'ordre, en partant du nombre choisi.",
       [(3, 4, 2), (-2, 5, 3), (5, -1, 4), (4, 6, -1), (-3, 2, 5), (7, -3, 2), (2, 10, -3), (-5, 4, 1)])
def _(p):
    x, a, b = p
    r = (x + a) * x - b
    step1 = f"ajouter ${a}$" if a > 0 else f"soustraire ${-a}$"
    step3 = f"soustraire ${b}$" if b > 0 else f"ajouter ${-b}$"
    return (rf"Programme de calcul : choisir un nombre ; {step1} ; multiplier le résultat par le nombre choisi ; {step3}. Quel résultat obtient-on en choisissant ${nb(x)}$ ?",
            m(nb(r)), [m(nb((x + a) * x + b)), m(nb(x + a * x - b)), m(nb((x + a) - b)), m(nb(-r)) if r else m("1")])


# ============================================================ FONCTIONS
@qtype("fon", "L'image de x par f est f(x) : remplace x par sa valeur.",
       [(3, -5, 4), (-2, 7, 3), (5, 1, -2), (-4, -3, -1), (6, -9, 2), (1, 8, -5), (-3, 2, 6), (7, -4, 0)])
def _(p):
    a, b, x = p
    v = a * x + b
    return (rf"Soit $f(x)={lin(a, b)}$. Quelle est l'image de ${nb(x)}$ par $f$ ?", m(nb(v)), [m(lf(F(x - b, a))), m(nb(a * x - b)), m(nb(a + b + x)), m(nb(v + 1))])


@qtype("fon", "Un antécédent de y est un nombre x tel que f(x) = y : résous l'équation.",
       [(2, 5, 13), (-3, 4, -8), (5, -2, 23), (4, 1, -7), (-2, -6, 4), (3, 0, 12), (6, -5, 13), (-1, 9, 2)])
def _(p):
    a, b, y = p
    return (rf"Soit $f(x)={lin(a, b)}$. Quel est l'antécédent de ${nb(y)}$ par $f$ ?", m(lf(F(y - b, a))),
            [m(nb(a * y + b)), m(lf(F(y + b, a))) if F(y + b, a) != F(y - b, a) else m(lf(F(y - b, a) + 1)), m(lf(F(y, a) - b) if F(y, a) - b != F(y - b, a) else lf(F(y - b, a) - 1))])


@qtype("fon", "Une fonction linéaire s'écrit f(x) = ax : a = f(x) ÷ x.",
       [(4, 12), (5, -15), (-2, 7), (3, 1), (8, 6), (-5, -20), (10, 4), (6, -9)])
def _(p):
    x, y = p
    a = F(y, x)
    return (rf"$f$ est une fonction linéaire telle que $f({nb(x)})={nb(y)}$. Quel est son coefficient ?", m(lf(a)), [m(lf(F(x, y))), m(nb(x * y)), m(nb(y - x)), m(lf(-a))])


@qtype("fon", "Pour une fonction affine, a = (f(x₂) − f(x₁)) ÷ (x₂ − x₁).",
       [((1, 5), (3, 11)), ((2, 1), (6, -7)), ((0, 4), (5, 14)), ((-1, 3), (2, -3)), ((4, 2), (8, 4)), ((-2, -5), (3, 10)), ((1, 0), (4, 9)), ((3, 7), (5, 6))])
def _(p):
    (x1, y1), (x2, y2) = p
    a = F(y2 - y1, x2 - x1)
    return (rf"$f$ est une fonction affine telle que $f({nb(x1)})={nb(y1)}$ et $f({nb(x2)})={nb(y2)}$. Quel est le coefficient $a$ de $f(x)=ax+b$ ?",
            m(lf(a)), [m(lf(F(x2 - x1, y2 - y1))) if y2 != y1 else m("1"), m(lf(-a)), m(nb(y2 - y1)), m(lf(F(y2 + y1, x2 + x1)) if x2 + x1 else lf(a + 1)), m(lf(a + 1)), m(lf(a * 2)), m(lf(a - 1))])


@qtype("fon", "f(x) = ax + b : remplace x et f(x) par les valeurs connues pour trouver b.",
       [(2, (3, 11)), (-3, (1, 4)), (4, (-2, -5)), (5, (2, 7)), (-1, (6, 0)), (3, (-1, 5)), (F(1, 2), (4, 6)), (-2, (-3, 1))])
def _(p):
    a, (x, y) = p
    a = F(a)
    b = y - a * x
    return (rf"$f$ est la fonction affine $f(x)={lf(a) if a.denominator != 1 else ('' if a == 1 else '-' if a == -1 else nb(a))}x+b$ et $f({nb(x)})={nb(y)}$. Que vaut $b$ ?",
            m(lf(b)), [m(lf(y + a * x)), m(nb(y)), m(lf(F(y, x) if x else y) if (F(y, x) if x else y) != b else lf(b + 1)), m(lf(-b)) if b else m("1")])


@qtype("fon", "Augmenter de t %, c'est multiplier par 1 + t/100 ; diminuer de t %, par 1 − t/100.",
       [(20, "aug"), (15, "dim"), (8, "aug"), (35, "dim"), (150, "aug"), (5, "dim"), (2, "aug"), (60, "dim")])
def _(p):
    t, w = p
    c = 1 + F(t, 100) * (1 if w == "aug" else -1)
    verb = "Augmenter" if w == "aug" else "Diminuer"
    return (rf"{verb} une quantité de ${t}\,\%$ revient à la multiplier par :", m(nb(c)), [m(nb(F(t, 100))), m(nb(2 - c)), m(nb(1 + F(t, 10) * (1 if w == "aug" else -1))) if 1 + F(t, 10) * (1 if w == "aug" else -1) > 0 else m(nb(c + 1)), m(nb(t))])


@qtype("fon", "Remplace x par sa valeur entre parenthèses ; calcule d'abord le carré.",
       [(1, -3, 0, 4), (2, 1, -5, -2), (-1, 4, 3, 3), (1, 5, -2, -1), (3, 0, -4, 2), (1, -2, -8, -3), (-2, 3, 1, 1), (1, 1, 1, 5)])
def _(p):
    a, b, c, x = p
    v = a * x * x + b * x + c
    return (rf"Soit $g(x)={expr([(a, 'x^2'), (b, 'x'), (c, '')])}$. Que vaut $g({nb(x)})$ ?", m(nb(v)),
            [m(nb(-a * x * x + b * x + c)), m(nb(a * 2 * x + b * x + c)), m(nb(-v)) if v else m("1"), m(nb(v + 2))])


@qtype("fon", "Linéaire : f(x) = ax ; affine : f(x) = ax + b ; une fonction constante est affine (a = 0).",
       [("4x", "linéaire"), ("2x+3", "affine non linéaire"), ("x^2", "ni affine ni linéaire"), ("5", "constante"),
        ("-x", "linéaire"), ("3-x", "affine non linéaire"), (r"\dfrac{1}{x}", "ni affine ni linéaire"), ("2(x+1)", "affine non linéaire")])
def _(p):
    f, nat = p
    return (rf"De quel type est la fonction $f:x\mapsto {f}$ ?", nat, [x for x in ["linéaire", "affine non linéaire", "constante", "ni affine ni linéaire"] if x != nat])


# ============================================================ GÉOMÉTRIE
@qtype("geo", "Thalès : quand (AB) et (CD) sont parallèles et se coupent en O, OA/OC = OB/OD = AB/CD.",
       [(3, 6, 4), (2, 5, 3), (4, 10, 7), (5, 3, 8), (6, 9, 4), (2, 7, 5), (8, 6, 10), (3, 4, 9)])
def _(p):
    oa, oc, ab = p
    cd = F(ab * oc, oa)
    return (rf"Les droites $(AC)$ et $(BD)$ se coupent en $O$, et les droites $(AB)$ et $(CD)$ sont parallèles. $OA={oa}$ cm, $OC={oc}$ cm et $AB={ab}$ cm. Combien mesure $CD$ ?",
            u(nb(cd), "cm"), [u(nb(F(ab * oa, oc)), "cm"), u(nb(ab + oc - oa), "cm"), u(nb(F(oa * oc, ab)), "cm"), u(nb(cd + 1), "cm")])


@qtype("geo", "Réciproque de Thalès : si les points sont alignés dans le même ordre et que les rapports sont égaux, les droites sont parallèles.",
       [((3, 9), (4, 12)), ((2, 5), (3, 8)), ((5, 15), (6, 18)), ((4, 10), (6, 14)), ((7, 21), (2, 6)), ((3, 7), (6, 15)), ((6, 8), (9, 12)), ((5, 9), (4, 8))])
def _(p):
    (am, ab), (an, ac) = p
    ok = am * ac == an * ab
    return (rf"Les points $A$, $M$, $B$ sont alignés dans cet ordre, ainsi que $A$, $N$, $C$. $AM={am}$, $AB={ab}$, $AN={an}$ et $AC={ac}$. Les droites $(MN)$ et $(BC)$ sont-elles parallèles ?",
            "oui" if ok else "non", ["non" if ok else "oui", "on ne peut pas savoir", "seulement si le triangle est rectangle"])


@qtype("geo", "Dans un triangle rectangle, sin(angle) = côté opposé ÷ hypoténuse, donc côté opposé = hypoténuse × sin.",
       [(10, F(6, 10)), (8, F(5, 10)), (20, F(45, 100)), (12, F(75, 100)), (15, F(2, 10)), (5, F(8, 10)), (40, F(35, 100)), (16, F(25, 100))])
def _(p):
    h, s = p
    return (rf"Le triangle $ABC$ est rectangle en $A$, avec $BC={h}$ cm et $\sin\widehat{{ABC}}={nb(s)}$. Combien mesure $AC$ ?",
            u(nb(h * s), "cm"), [u(nb(h * (1 - s)), "cm"), u(nb(h * s / 2), "cm"), u(nb(h * s * 2), "cm"), u(nb(h * s + 1), "cm")])


@qtype("geo", "tan(angle) = côté opposé ÷ côté adjacent.",
       [(4, 3), (5, 12), (8, 6), (7, 7), (10, 4), (3, 9), (6, 8), (15, 5)])
def _(p):
    ab, ac = p
    t = F(ac, ab)
    hyp2 = ab * ab + ac * ac
    return (rf"Le triangle $ABC$ est rectangle en $A$, avec $AB={ab}$ cm et $AC={ac}$ cm. Que vaut $\tan\widehat{{ABC}}$ ?",
            m(lf(t)), [m(lf(1 / t)) if t != 1 else m(lf(F(1, 2))), m(lf(t + 1)), m(lf(F(ab, ab + ac))), m(lf(t * 2))])


@qtype("geo", "Une homothétie de rapport k multiplie les longueurs par |k| (le signe change seulement le côté).",
       [(-2, 3), (3, F(5, 2)), (F(1, 2), 8), (-3, 4), (F(-1, 2), 6), (4, F(3, 2)), (-1, 7), (F(3, 2), 10)])
def _(p):
    k, L = p
    k, L = F(k), F(L)
    return (rf"Une homothétie de rapport ${lf(k)}$ transforme le segment $[AB]$, de longueur ${nb(L)}$ cm, en $[A'B']$. Combien mesure $A'B'$ ?",
            u(nb(abs(k) * L), "cm"), [u(nb(abs(k) * L + 1), "cm"), u(nb(L / abs(k)), "cm") if L / abs(k) != abs(k) * L else u(nb(L * 2), "cm"), u(nb(L + abs(k)), "cm"), u(nb(k * k * L), "cm"), u(nb(abs(k) * L + 2), "cm"), u(nb(abs(k) * L * 3), "cm"), u(nb(abs(k) * L / 2), "cm")])


@qtype("geo", "Volume d'une boule = 4/3 × π × r³ (valeur exacte en fonction de π).",
       [3, 6, 1, 9, 2, F(3, 2), 12, F(3, 4)])
def _(r):
    r = F(r)
    P = lambda k: m(rf"{lf(k) if k != 1 else ''}\pi~\text{{cm}}^3")
    return (rf"Quel est le volume exact d'une boule de rayon ${nb(r)}$ cm ?", P(F(4, 3) * r ** 3), [P(4 * r * r), P(r ** 3), P(F(4, 3) * r * r), P(F(4, 3) * r ** 3 * 2)])


@qtype("geo", "Dans un triangle rectangle, le carré de l'hypoténuse est égal à la somme des carrés des deux autres côtés.",
       [("hyp", 3, 4), ("ech", 13, 5), ("ecr", 60, 80), ("cote", 10, 6), ("hyp", 5, 12), ("ech", 5, 3), ("ecr", 90, 120), ("cote", 25, 7)])
def _(p):
    c, a, b = p
    if c in ("hyp", "ecr"):
        r = round((a * a + b * b) ** .5)
        dis = [a + b, a * a + b * b, r + 1 if c == "hyp" else r + 10, abs(b - a)]
    else:
        r = round((a * a - b * b) ** .5)
        dis = [a - b, a * a - b * b, a + b, r + 1]
    un = "cm" if c != "ech" else "m"
    q = {"hyp": rf"Le triangle $ABC$ est rectangle en $A$, avec $AB={a}$ cm et $AC={b}$ cm. Combien mesure $BC$ ?",
         "cote": rf"Le triangle $ABC$ est rectangle en $A$, avec $BC={a}$ cm et $AB={b}$ cm. Combien mesure $AC$ ?",
         "ech": rf"Une échelle de ${a}$ m est appuyée contre un mur vertical. Son pied est à ${b}$ m du mur, sur un sol horizontal. À quelle hauteur l'échelle touche-t-elle le mur ?",
         "ecr": rf"Un écran rectangulaire mesure ${b}$ cm de large et ${a}$ cm de haut. Combien mesure sa diagonale ?"}[c]
    return (q, u(nb(r), un), [u(nb(x), un) for x in dis])


PY_OPTS = ["Oui, par la réciproque de Pythagore", "Non, par la contraposée de Pythagore",
           "Oui, par le théorème de Pythagore", "Non, par la réciproque de Pythagore"]


@qtype("geo", "Compare le carré du plus grand côté à la somme des carrés des deux autres : s'il y a égalité, la réciproque prouve que le triangle est rectangle ; sinon, la contraposée prouve qu'il ne l'est pas.",
       [(6, 8, 10), (5, 7, 9), (4, 6, 7), (9, 12, 15), (8, 15, 17), (6, 9, 11), (5, 11, 12), (7, 24, 25)])
def _(p):
    a, b, c = p
    ok = a * a + b * b == c * c
    ans = PY_OPTS[0] if ok else PY_OPTS[1]
    return (rf"Le triangle $EFG$ est tel que $EF={a}$ cm, $FG={b}$ cm et $EG={c}$ cm. Est-il rectangle ?",
            ans, [x for x in PY_OPTS if x != ans])


# ============================================================ STATISTIQUES ET PROBABILITÉS
def med(v):
    s = sorted(v); n = len(s)
    return F(s[n // 2]) if n % 2 else F(s[n // 2 - 1] + s[n // 2], 2)


@qtype("sta", "Range les valeurs dans l'ordre croissant : la médiane est la valeur du milieu (ou la moyenne des deux valeurs du milieu).",
       [(12, 7, 15, 9, 11), (3, 8, 14, 6, 10, 2), (18, 25, 13, 20, 16), (5, 9, 1, 12), (21, 17, 30, 14, 26, 19, 23), (4, 4, 9, 2, 7, 6), (40, 35, 52, 48, 39), (11, 15, 8, 20, 13, 9)])
def _(v):
    md = med(v); n = len(v)
    mid = F(v[n // 2]) if n % 2 else F(v[n // 2 - 1] + v[n // 2], 2)
    return (rf"Quelle est la médiane de la série ${'\\ ;\\ '.join(map(str, v))}$ ?", m(nb(md)),
            [m(nb(mid)) if mid != md else m(nb(md + 1)), m(nb(F(sum(v), n))) if F(sum(v), n) != md else m(nb(md - 1)), m(nb(max(v) - min(v))), m(nb(F(n + 1, 2)))])


@qtype("sta", "Moyenne = somme des valeurs ÷ nombre de valeurs.",
       [(14, 9, 16, 11), (8, 12, 10, 15, 5), (20, 17, 11), (6, 9, 13, 4), (25, 30, 35, 18), (3, 11, 7, 9, 5), (16, 14, 19, 12), (1, 4, 2, 8, 10)])
def _(v):
    me = F(sum(v), len(v))
    return (rf"Quelle est la moyenne de la série ${'\\ ;\\ '.join(map(str, v))}$ ?", m(nb(me)), [m(nb(sum(v))), m(nb(med(v))) if med(v) != me else m(nb(me + 2)), m(nb(me + 1)), m(nb(max(v)))])


@qtype("sta", "Étendue = plus grande valeur − plus petite valeur.",
       [(14, 9, 16, 11), (8, 12, 10, 15, 5), (20, 17, 11, 26), (6, 9, 13, 4), (25, 30, 35, 18), (3, 11, 7, 9, 5), (16, 14, 19, 12), (1, 4, 2, 8, 10)])
def _(v):
    e = max(v) - min(v)
    return (rf"Quelle est l'étendue de la série ${'\\ ;\\ '.join(map(str, v))}$ ?", m(nb(e)), [m(nb(max(v))), m(nb(max(v) + min(v))), m(nb(e + 1)), m(nb(F(sum(v), len(v))))])


@qtype("sta", "Sans remise, il y a une boule de moins au deuxième tirage : multiplie les probabilités le long de l'arbre.",
       [(3, 5), (2, 4), (4, 6), (2, 5), (3, 7), (5, 8), (2, 6), (4, 10)])
def _(p):
    r, N = p
    q = F(r, N) * F(r - 1, N - 1)
    return (rf"Une urne contient ${N}$ boules dont ${r}$ rouges. On tire successivement deux boules, sans remise. Quelle est la probabilité de tirer deux boules rouges ?",
            m(lf(q)), [m(lf(F(r, N) ** 2)), m(lf(F(2 * r, N))) if F(2 * r, N) <= 1 else m(lf(F(r, N))), m(lf(F(r, N) * F(r - 1, N))), m(lf(F(r - 1, N - 1)))])


@qtype("sta", "Pour deux expériences indépendantes, on multiplie les probabilités.",
       [("un 6 avec le dé", F(1, 6), "PILE avec la pièce", F(1, 2)), ("un nombre pair avec le dé", F(1, 2), "PILE avec la pièce", F(1, 2)),
        ("un 1 ou un 2 avec le dé", F(1, 3), "FACE avec la pièce", F(1, 2)), ("un 5 avec le dé", F(1, 6), "un 5 avec un deuxième dé", F(1, 6)),
        ("un multiple de 3 avec le dé", F(1, 3), "PILE avec la pièce", F(1, 2)), ("un nombre impair avec le dé", F(1, 2), "un 6 avec un deuxième dé", F(1, 6)),
        ("un nombre supérieur à 4 avec le dé", F(1, 3), "un nombre pair avec un deuxième dé", F(1, 2)), ("un 3 avec le dé", F(1, 6), "FACE avec la pièce", F(1, 2))])
def _(p):
    e1, p1, e2, p2 = p
    return (rf"On lance un dé équilibré à six faces et une pièce équilibrée (ou un deuxième dé). Quelle est la probabilité d'obtenir {e1} et {e2} ?",
            m(lf(p1 * p2)), [m(lf(p1 + p2)) if p1 + p2 <= 1 else m(lf(p1 * p2 * 2)), m(lf(p1)), m(lf(p2)) if p2 != p1 else m(lf(p1 * p2 * 2)), m(lf(p1 * p2 * 2)) if p1 * p2 * 2 not in (p1, p2) else m(lf(p1 * p2 / 2))])


@qtype("sta", "Fréquence en % = effectif ÷ effectif total × 100.",
       [(8, 25), (12, 40), (9, 20), (30, 120), (14, 56), (21, 30), (7, 35), (33, 60)])
def _(p):
    k, N = p
    r = F(100 * k, N)
    pc = lambda x: m(rf"{nb(x)}\,\%")
    return (rf"Dans une classe de ${N}$ élèves, ${k}$ pratiquent un sport en club. Quelle est la fréquence, en pourcentage, de ces élèves ?" if N <= 40 else
            rf"Sur ${N}$ personnes interrogées, ${k}$ ont répondu « oui ». Quelle est la fréquence, en pourcentage, des « oui » ?",
            pc(r), [pc(k), pc(100 - r), pc(F(k, N) * 10), pc(r + 5)])


@qtype("sta", "Probabilité = nombre d'issues favorables ÷ nombre total d'issues ; simplifie la fraction.",
       [(4, 6, 2), (5, 3, 4), (2, 8, 6), (7, 5, 3), (6, 6, 3), (3, 9, 3), (10, 2, 4), (1, 7, 4)])
def _(p):
    r, b, v = p
    N = r + b + v
    bo = lambda c, w: f"${c}$ boule{'s' if c > 1 else ''} {w}{'s' if c > 1 else ''}"
    return (rf"Un sac contient {bo(r, 'rouge')}, {bo(b, 'bleue')} et {bo(v, 'verte')}. On tire une boule au hasard. Quelle est la probabilité de ne pas tirer une boule rouge ?",
            m(lf(F(N - r, N))), [m(lf(F(r, N))), m(lf(F(N - r, r))) if N - r != r else m(lf(F(1, 3))), m(lf(F(b, N))) if F(b, N) != F(N - r, N) else m(lf(F(v, N))), m(lf(F(N - r, N + 1)))])


@qtype("sta", "La probabilité de l'événement contraire de A est 1 − P(A).",
       [F(3, 7), F(15, 100), F(5, 9), F(72, 100), F(1, 8), F(4, 10), F(11, 12), F(6, 100)])
def _(q):
    d = q.denominator in (10, 100, 50, 25, 20, 4, 5)
    sh = (lambda x: nb(x)) if d else (lambda x: lf(x))
    return (rf"La probabilité d'un événement $A$ est ${sh(q)}$. Quelle est la probabilité de l'événement contraire de $A$ ?",
            m(sh(1 - q)), [m(sh(q)), m(sh(abs(F(1, 2) - q))) if abs(F(1, 2) - q) != 1 - q else m(sh(q / 2)), m(sh((1 - q) / 2)), m(sh(1 - q / 2))])


# ============================================================ GRANDEURS ET PROPORTIONNALITÉ
@qtype("gra", "1 m/s = 3,6 km/h : pour passer des m/s aux km/h, multiplie par 3,6.",
       [10, 25, 5, 15, 20, 30, F(5, 2), 40])
def _(v):
    v = F(v)
    kmh = lambda x: m(rf"{nb(x)}~\text{{km/h}}")
    return (rf"Une vitesse de ${nb(v)}$ m/s correspond à :", kmh(v * F(36, 10)), [kmh(v / F(36, 10)) if (v / F(36, 10)).denominator in (1, 2, 4, 5, 10, 20, 25, 50, 100) else kmh(v * 10), kmh(v * 60), kmh(v * 1000), kmh(v * 36)])


@qtype("gra", "Vitesse moyenne = distance ÷ durée (en heures).",
       [(180, F(2)), (135, F(3, 2)), (60, F(3, 4)), (420, F(7, 2)), (25, F(1, 4)), (330, F(3)), (99, F(9, 10)), (70, F(5, 4))])
def _(p):
    d, t = p
    v = F(d) / t
    kmh = lambda x: m(rf"{nb(x)}~\text{{km/h}}")
    return (rf"Un véhicule parcourt ${d}$ km en {dur(t)}. Quelle est sa vitesse moyenne ?", kmh(v), [kmh(d * t), kmh(v + 10), kmh(v / 2), kmh(v * 2)])


@qtype("gra", "Nouveau prix = prix × (1 + t/100) pour une hausse, × (1 − t/100) pour une baisse.",
       [(60, 15), (240, -25), (1500, 12), (85, -20), (400, 35), (2200, -15), (75, 40), (1200, -5)])
def _(p):
    P0, t = p
    P1 = F(P0) * (1 + F(t, 100))
    w = f"augmente de ${t}\\,\\%$" if t > 0 else f"baisse de ${-t}\\,\\%$"
    eu = lambda x: u(nb(x), "F")
    return (rf"Un article coûte ${nb(P0)}$ F. Son prix {w}. Quel est son nouveau prix ?", eu(P1), [eu(P0 + t), eu(F(P0) * (1 - F(t, 100))), eu(F(P0) * abs(t) / 100), eu(P1 + 10)])


@qtype("gra", "Taux d'évolution en % = (valeur finale − valeur initiale) ÷ valeur initiale × 100.",
       [(80, 100), (250, 200), (40, 46), (120, 90), (500, 575), (60, 51), (200, 260), (1000, 850)])
def _(p):
    a, b = p
    t = F(b - a, a) * 100
    pc = lambda x: m(rf"{'+' if x > 0 else ''}{nb(x)}\,\%")
    return (rf"Un prix passe de ${nb(a)}$ F à ${nb(b)}$ F. Quel est le pourcentage d'évolution ?", pc(t), [pc(b - a), pc(-t), pc(t / 2), pc(t + 5)])


@qtype("gra", "Un débit est une grandeur quotient : volume ÷ durée.",
       [(120, 5), (90, 6), (250, 10), (36, 4), (300, 12), (45, 2), (84, 7), (150, 20)])
def _(p):
    V, t = p
    r = F(V, t)
    L = lambda x: m(rf"{nb(x)}~\text{{L/min}}")
    return (rf"Un robinet remplit une cuve de ${V}$ L en ${t}$ min. Quel est son débit ?", L(r), [L(V * t), L(F(t, V) * 100), L(r + 2), L(r * 2)])


@qtype("gra", "À l'échelle 1/n, une longueur réelle est n fois plus grande que sur le plan (attention aux unités).",
       [(1000, 4), (500, 6), (25000, 2), (200, 15), (100000, 3), (50, 12), (2000, F(5, 2)), (10000, 7)])
def _(p):
    s, c = p
    real_m = F(c) * s / 100
    mm = lambda x: u(nb(x), "m")
    return (rf"Sur une carte à l'échelle $\dfrac{{1}}{{{nb(s)}}}$, deux points sont distants de ${nb(c)}$ cm. Quelle est la distance réelle ?",
            mm(real_m), [mm(F(c) * s), mm(real_m / 10), mm(real_m * 10)])


@qtype("gra", "Partager dans le ratio a : b, c'est faire a + b parts égales et en donner a d'un côté, b de l'autre.",
       [(60, 2, 3), (84, 3, 4), (45, 1, 2), (120, 3, 5), (90, 4, 5), (56, 5, 2), (150, 7, 3), (72, 1, 5)])
def _(p):
    T, a, b = p
    x, y = F(T * a, a + b), F(T * b, a + b)
    P = lambda v, w: m(rf"{nb(v)}\text{{ et }}{nb(w)}")
    return (rf"On partage ${T}$ bonbons entre Léa et Noa dans le ratio ${a}:{b}$. Combien chacun en reçoit-il (Léa, puis Noa) ?",
            P(x, y), [P(y, x), P(F(T, 2), F(T, 2)), P(F(T * a, a + b + 1), T - F(T * a, a + b + 1)) if (T * a) % (a + b + 1) == 0 else P(x - 1, y + 1)])


@qtype("gra", "1 m³ = 1 000 L, 1 dm³ = 1 L, 1 cm³ = 1 mL.",
       [(F(5, 2), "m^3", "L", 1000), (750, "mL", "cm^3", 1), (F(3, 10), "m^3", "dm^3", 1000), (4500, "L", "m^3", F(1, 1000)),
        (2, "dm^3", "cm^3", 1000), (125, "cm^3", "dm^3", F(1, 1000)), (F(3, 2), "L", "cm^3", 1000), (8000, "dm^3", "m^3", F(1, 1000))])
def _(p):
    x, a, b, f = p
    U = lambda s: rf"\text{{{s[:-2]}}}^3" if s.endswith("^3") else rf"\text{{{s}}}"
    V = lambda v: m(rf"{nb(v)}~{U(b)}")
    r = F(x) * f
    return (rf"Compléter : ${nb(x)}~{U(a)}=\;?\;{U(b)}$", V(r), [V(r * 10) if f != 1 else V(r * 1000), V(r / 10) if f != 1 else V(r / 1000), V(r * 100) if f != 1 else V(r * 10), V(r / 100) if f != 1 else V(r / 10)])
