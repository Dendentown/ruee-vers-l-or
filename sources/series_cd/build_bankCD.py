"""Derives bankC.py and bankD.py from gen250.py (like build_bankB.py): same 250 question
types in the same order, other values. C = qcm_501-750, D = qcm_751-1000."""
import sys
sys.path.insert(0, "/home/claude/bank5cd")
from qcd import QC, QD

BASE = open("/home/claude/gen250.py", encoding="utf-8").read()
SIG = r'''
import os as _os
def _sig(dr):
    f = getattr(dr, "func", dr)
    return [getattr(f, "__name__", ""), repr(sorted(getattr(dr, "keywords", {}).items()))]
json.dump([[th, en] + _sig(dr) + [list(op)] for (th, en, dr, op, ok, bx) in ALL],
          open(f"{OUT}/sig.json", "w"), ensure_ascii=False, default=str)
if _os.environ.get("SIGONLY"):
    raise SystemExit
'''

# (old text in gen250.py, value for C, value for D)
R = [
    # ---------- géométrie ----------
    ("[((5, 6, 8), True), ((3, 4, 9), False),\n                               ((2, 5, 6), True)]",
     "[((4, 5, 8), True), ((2, 4, 7), False),\n                               ((3, 6, 7), True)]",
     "[((5, 7, 10), True), ((3, 5, 9), False),\n                               ((4, 4, 7), True)]"),
    # ---------- relatifs ----------
    ("[(-5, 5, 1, -4), (-3, 3, 2, -2.5), (-2, 2, 4, -0.75),\n                       (-6, 4, 1, -6), (-3, 3, 2, 0.5)]",
     "[(-5, 5, 1, -2), (-3, 3, 2, -0.5), (-2, 2, 4, -1.75),\n                       (-6, 4, 1, -4), (-3, 3, 2, 2.5)]",
     "[(-5, 5, 1, -5), (-3, 3, 2, -2), (-2, 2, 4, -0.25),\n                       (-6, 4, 1, -3), (-3, 3, 2, -1)]"),
    ("for a, b in [(-4, 3), (-6, -1)]:", "for a, b in [(-2, 5), (-6, -3)]:", "for a, b in [(-5, 1), (-7, -4)]:"),
    ("for a, b, c3 in [(-3, 5, -2), (4, -9, 6)]:", "for a, b, c3 in [(-6, 4, -3), (3, -7, 5)]:",
     "for a, b, c3 in [(-2, 8, -5), (6, -10, 4)]:"),
    ("for z, d, up in [(-12, 5, True), (-8, 6, False), (-15, 9, True)]:",
     "for z, d, up in [(-16, 7, True), (-5, 8, False), (-11, 4, True)]:",
     "for z, d, up in [(-17, 9, True), (-9, 5, False), (-13, 6, True)]:"),
    ("for l0, d in [(-2, 5), (3, -6), (-3, 4)]:", "for l0, d in [(-3, 5), (2, -5), (-4, 7)]:",
     "for l0, d in [(-1, 6), (5, -8), (-2, 3)]:"),
    ("for g_, p_ in [(7, 10), (4, 9), (12, 5)]:", "for g_, p_ in [(8, 13), (5, 7), (11, 3)]:",
     "for g_, p_ in [(3, 10), (7, 4), (10, 15)]:"),
    # ---------- fractions ----------
    ("for n, k in [(5, 2), (6, 5), (10, 3), (9, 4)]:", "for n, k in [(7, 2), (8, 3), (10, 6), (12, 4)]:",
     "for n, k in [(5, 3), (9, 2), (10, 4), (6, 4)]:"),
    ("for r, q, k in [(2, 5, 3), (3, 3, 4), (4, 5, 7)]:", "for r, q, k in [(2, 6, 5), (3, 5, 4), (4, 4, 9)]:",
     "for r, q, k in [(2, 3, 5), (3, 6, 7), (4, 3, 5)]:"),
    ("for hi, d, p in [(2, 3, 4), (2, 5, 7), (3, 4, 9)]:", "for hi, d, p in [(2, 4, 5), (2, 5, 8), (3, 4, 11)]:",
     "for hi, d, p in [(2, 3, 2), (2, 6, 7), (3, 5, 13)]:"),
    ("for a, b, k in [(2, 7, 3), (5, 4, 2), (3, 8, 5), (4, 9, 2)]:",
     "for a, b, k in [(2, 5, 3), (4, 7, 2), (3, 10, 4), (5, 8, 3)]:",
     "for a, b, k in [(3, 4, 5), (2, 9, 3), (6, 7, 2), (5, 3, 4)]:"),
    ('for a, b, d, op in [(2, 3, 9, "+"), (7, 2, 11, "−"), (4, 5, 13, "+"),\n                    (9, 4, 10, "−")]:',
     'for a, b, d, op in [(1, 5, 8, "+"), (9, 4, 13, "−"), (3, 4, 10, "+"),\n                    (7, 3, 9, "−")]:',
     'for a, b, d, op in [(2, 7, 12, "+"), (10, 3, 11, "−"), (5, 6, 17, "+"),\n                    (8, 5, 7, "−")]:'),
    ("for a, b, c3, dd in [(1, 2, 1, 4), (1, 3, 1, 6), (3, 4, 1, 8)]:",
     "for a, b, c3, dd in [(1, 3, 1, 9), (2, 5, 1, 10), (1, 2, 3, 8)]:",
     "for a, b, c3, dd in [(1, 4, 1, 8), (2, 3, 1, 9), (3, 5, 1, 10)]:"),
    ("for (a, b), (c3, dd) in [((2, 3), (5, 6)), ((3, 5), (7, 10)),\n                         ((4, 5), (7, 10))]:",
     "for (a, b), (c3, dd) in [((1, 3), (5, 6)), ((3, 4), (5, 8)),\n                         ((2, 5), (7, 10))]:",
     "for (a, b), (c3, dd) in [((1, 4), (3, 8)), ((5, 6), (2, 3)),\n                         ((3, 5), (4, 10))]:"),
    ("for a, b in [(18, 24), (15, 35)]:", "for a, b in [(16, 24), (14, 35)]:", "for a, b in [(27, 36), (10, 45)]:"),
    ("for n, k in [(8, 3), (6, 1), (10, 4), (12, 5)]:", "for n, k in [(8, 1), (6, 4), (10, 7), (12, 3)]:",
     "for n, k in [(8, 7), (6, 5), (10, 2), (12, 9)]:"),
    ("for n, k, mins in [(4, 3, 45), (3, 2, 40)]:", "for n, k, mins in [(6, 1, 10), (5, 2, 24)]:",
     "for n, k, mins in [(6, 5, 50), (5, 3, 36)]:"),
    ("dure {'trois quarts' if n == 4 else 'deux tiers'} d'heure ?",
     "dure {'un sixième' if n == 6 else 'deux cinquièmes'} d'heure ?",
     "dure {'cinq sixièmes' if n == 6 else 'trois cinquièmes'} d'heure ?"),
    ("for d, p in [(5, 3), (8, 5)]:", "for d, p in [(4, 3), (7, 4)]:", "for d, p in [(5, 4), (9, 5)]:"),
    # ---------- proportionnalité / stats ----------
    ("[(3, (1, 2, 4)), (5, (2, 3, 6)), (4, (1, 3, 5))]", "[(4, (2, 3, 6)), (3, (1, 4, 5)), (6, (2, 3, 4))]",
     "[(5, (1, 3, 4)), (8, (1, 2, 4)), (2, (2, 5, 7))]"),
    ("for pct, N in [(25, 80), (10, 450), (50, 36), (20, 150)]:",
     "for pct, N in [(25, 160), (10, 230), (50, 62), (20, 350)]:",
     "for pct, N in [(25, 40), (10, 680), (50, 48), (20, 450)]:"),
    ("for vals in [(10, 17, 12), (6, 13, 9, 16), (5, 9, 13)]:",
     "for vals in [(12, 15, 9), (8, 14, 11, 15), (4, 10, 13)]:",
     "for vals in [(13, 7, 16), (9, 15, 6, 10), (14, 8, 11)]:"),
    ('(["Rouge", "Vert", "Bleu"], [6, 9, 5])', '(["Rouge", "Vert", "Bleu"], [4, 9, 7])', '(["Rouge", "Vert", "Bleu"], [8, 5, 7])'),
    ('(["A", "B", "C", "D"], [3, 7, 4, 6])', '(["A", "B", "C", "D"], [6, 2, 5, 7])', '(["A", "B", "C", "D"], [4, 6, 3, 7])'),
    ('(["Oui", "Non", "Sans avis"], [12, 5, 3])', '(["Oui", "Non", "Sans avis"], [10, 7, 3])',
     '(["Oui", "Non", "Sans avis"], [13, 4, 3])'),
    ('"Nombre de parts", "Sucre (en g)", 8, 160, 4)', '"Nombre de parts", "Sucre (en g)", 6, 150, 8)',
     '"Nombre de parts", "Sucre (en g)", 5, 100, 8)'),
    ('"Nombre de personnes", "Igname (en g)", 4, 600, 6)', '"Nombre de personnes", "Igname (en g)", 3, 450, 5)',
     '"Nombre de personnes", "Igname (en g)", 6, 900, 4)'),
    ('"Nombre de personnes", "Mangues", 6, 4, 9)', '"Nombre de personnes", "Mangues", 4, 6, 6)',
     '"Nombre de personnes", "Mangues", 8, 6, 12)'),
    ('[("papayes", 4, 600, 6), ("ananas", 3, 750, 5),\n                          ("régimes de bananes", 2, 1200, 3)]',
     '[("papayes", 5, 750, 3), ("ananas", 2, 600, 5),\n                          ("régimes de bananes", 4, 2000, 6)]',
     '[("papayes", 6, 900, 4), ("ananas", 5, 1250, 2),\n                          ("régimes de bananes", 2, 1100, 4)]'),
    ("[(3000, 20, False), (1500, 10, True),\n                          (4000, 25, True)]",
     "[(3500, 20, False), (1200, 25, True),\n                          (5000, 10, True)]",
     "[(4500, 10, False), (2400, 25, True),\n                          (3000, 30, True)]"),
    ("for x0, y0, x1 in [(10, 6, 25), (20, 12, 30)]:", "for x0, y0, x1 in [(10, 7, 30), (15, 9, 25)]:",
     "for x0, y0, x1 in [(10, 5, 35), (20, 14, 30)]:"),
    ('[("Lina", (13, 16, 10)), ("Hugo", (9, 12, 17, 14))]', '[("Lina", (14, 9, 13)), ("Hugo", (11, 15, 8, 18))]',
     '[("Lina", (12, 17, 10)), ("Hugo", (7, 13, 15, 9))]'),
    # ---------- probabilités ----------
    ('''EV = [("un nombre impair", 3), ("un multiple de 3", 2),
      ("un nombre supérieur à 4", 2), ("un nombre inférieur ou égal à 2", 2),
      ("un 5", 1), ("un diviseur de 6", 4), ("un nombre inférieur à 5", 4)]''',
     '''EV = [("un multiple de 2", 3), ("un nombre supérieur à 2", 4),
      ("un nombre inférieur à 4", 3), ("un 6", 1),
      ("un diviseur de 10", 3), ("un multiple de 5", 1), ("un nombre supérieur ou égal à 5", 2)]''',
     '''EV = [("un nombre supérieur à 1", 5), ("un nombre inférieur ou égal à 3", 3),
      ("un 4", 1), ("un diviseur de 8", 3),
      ("un diviseur de 9", 2), ("un nombre différent de 6", 5), ("un nombre compris entre 2 et 5", 4)]'''),
    ("L'événement « obtenir 0 » est :", "L'événement « obtenir 12 » est :", "L'événement « obtenir un nombre négatif » est :"),
    ("L'événement « obtenir un nombre pair » \"\n        \"a :", "L'événement « obtenir un nombre supérieur à 3 » \"\n        \"a :",
     "L'événement « obtenir un nombre inférieur à 4 » \"\n        \"a :"),
    ("L'événement « obtenir un 6 » est :", "L'événement « obtenir un 4 » est :", "L'événement « obtenir un 2 » est :"),
    ("L'événement « obtenir un nombre entre \"\n        \"1 et 6 » est :",
     "L'événement « obtenir un nombre supérieur \"\n        \"ou égal à 1 » est :",
     "L'événement « obtenir un nombre plus petit \"\n        \"que 10 » est :"),
    ('[(10, "un nombre pair", 5), (12, "un multiple de 4", 3),\n                  (9, "un nombre supérieur à 6", 3),\n                  (8, "un multiple de 3", 2)]',
     '[(10, "un multiple de 3", 3), (12, "un nombre supérieur à 9", 3),\n                  (8, "un nombre impair", 4),\n                  (9, "un multiple de 2", 4)]',
     '[(11, "un multiple de 5", 2), (12, "un multiple de 3", 4),\n                  (10, "un nombre inférieur à 4", 3),\n                  (9, "un nombre impair", 5)]'),
    ('[("« obtenir PILE en lançant une pièce »", 0.5),\n                 ("« tirer une boule rouge dans une urne qui ne contient que "\n                  "des boules bleues »", 0)]',
     '[("« obtenir un nombre pair avec un dé à six faces »", 0.5),\n                 ("« obtenir un nombre inférieur à 7 avec un dé à six "\n                  "faces »", 1)]',
     '[("« tirer une carte rouge dans un jeu de 32 cartes »", 0.5),\n                 ("« obtenir 0 avec un dé à six "\n                  "faces »", 0)]'),
    ('for N, k, who in [(50, 4, "Léa"), (100, 5, "Noa")]:', 'for N, k, who in [(40, 3, "Léa"), (120, 4, "Noa")]:',
     'for N, k, who in [(75, 2, "Léa"), (90, 7, "Noa")]:'),
    ("FREQ = [[8, 12, 9, 11, 10, 10], [5, 9, 6, 13, 8, 9], [10, 7, 12, 8, 6, 17]]",
     "FREQ = [[9, 10, 12, 8, 11, 10], [6, 10, 7, 12, 9, 8], [8, 11, 9, 13, 7, 12]]",
     "FREQ = [[11, 9, 8, 10, 13, 9], [8, 7, 11, 9, 6, 9], [12, 9, 10, 8, 15, 6]]"),
    ("for f_, g_ in [(14, 12), (11, 15)]:", "for f_, g_ in [(12, 14), (15, 9)]:", "for f_, g_ in [(16, 10), (9, 13)]:"),
    ('for cnt in [{"jaune": 3, "rouge": 1, "bleu": 4}, {"jaune": 2, "rouge": 5,\n                                                   "bleu": 1}]:',
     'for cnt in [{"jaune": 4, "rouge": 3, "bleu": 1}, {"jaune": 1, "rouge": 2,\n                                                   "bleu": 5}]:',
     'for cnt in [{"jaune": 2, "rouge": 4, "bleu": 2}, {"jaune": 3, "rouge": 2,\n                                                   "bleu": 3}]:'),
]

# random draws: pools that A and B never use, so a C or D question cannot repeat its twin
POOLS = [
    ("x = R.choice([25, 30, 35, 40, 45, 50])", "x = R.choice([20, 55, 65, 70])", "x = R.choice([15, 75, 22, 68])", 1),
    ("apex = R.choice([80, 90, 100, 110, 120])", "apex = R.choice([60, 130, 140])", "apex = R.choice([40, 70, 150])", 1),
    ("for i, a in enumerate(R.sample([20, 25, 30, 35, 40, 45], 4)):", "for i, a in enumerate(R.sample([50, 55, 60, 65, 70, 15], 4)):",
     "for i, a in enumerate(R.sample([38, 42, 48, 52, 58, 62], 4)):", 1),
    ("a = R.choice([50, 55, 60, 65, 75, 80])", "a = R.choice([45, 70, 85, 40])", "a = R.choice([35, 72, 68, 58])", 1),
    ("b = R.choice([5, 6, 7, 8]); h = R.choice([2, 3, 4])", "b = R.choice([9, 10]); h = R.choice([5, 6])",
     "b = R.choice([4, 11]); h = R.choice([5, 7])", 1),
    ("b = R.choice([6, 8, 9, 10]); h = R.choice([3, 4, 5, 6])", "b = R.choice([7, 11, 12]); h = R.choice([4, 7])",
     "b = R.choice([5, 13, 14]); h = R.choice([3, 8])", 1),
    ("a = R.choice([40, 50, 55, 70, 75])", "a = R.choice([35, 45, 60, 65])", "a = R.choice([30, 62, 68, 80])", 1),
    ("a = R.choice([-12, -9, -8, -7, -5, -3, 4, 6, 9])", "a = R.choice([-15, -13, -10, -6, -1, 2, 7, 8])",
     "a = R.choice([-14, -11, -4, 1, 5, 11])", 1),
    ("b = R.choice([-11, -6, -4, -2, 3, 5, 8, 10])", "b = R.choice([-14, -9, -7, -1, 1, 6, 12])",
     "b = R.choice([-13, -10, -5, -3, 2, 9, 13])", 2),
    ("for k in R.sample([3, 5, 6, 7, 1.5, 2.5], 4):", "for k in R.sample([4, 8, 9, 3.5], 4):", "for k in R.sample([2, 11, 12, 4.5], 4):", 1),
]

CTX = {
"C": '''CTX_Q = [(24, 5, 6, "Sur 24 élèves, les 5/6 mangent à la cantine. "
          "Combien mangent à la cantine ?"),
         (30, 3, 5, "Dans un club de va'a de 30 membres, les 3/5 sont des "
          "garçons. Combien y a-t-il de garçons ?"),
         (21, 4, 7, "Sur 21 mangues récoltées, les 4/7 sont mûres. Combien "
          "sont mûres ?"),
         (27, 2, 3, "Les 2/3 des 27 élèves de l'atelier ont choisi le "
          "basket. Combien ont choisi le basket ?"),
         (40, 3, 8, "Sur 40 bus Tanéo, les 3/8 sont électriques. Combien "
          "sont électriques ?"),
         (28, 1, 4, "Un quart des 28 cartes du jeu sont des piques. Combien "
          "y a-t-il de piques ?")]
''',
"D": '''CTX_Q = [(36, 3, 4, "Sur les 36 élèves du niveau, les 3/4 savent nager. "
          "Combien savent nager ?"),
         (25, 3, 5, "Dans un club de va'a de 25 membres, les 3/5 sont des "
          "filles. Combien y a-t-il de filles ?"),
         (24, 5, 8, "Sur 24 mangues récoltées, les 5/8 sont mûres. Combien "
          "sont mûres ?"),
         (15, 2, 3, "Les 2/3 des 15 élèves de l'atelier ont choisi le "
          "football. Combien ont choisi le football ?"),
         (42, 2, 7, "Sur 42 bus Tanéo, les 2/7 sont électriques. Combien "
          "sont électriques ?"),
         (32, 1, 4, "Un quart des 32 cartes du jeu sont des trèfles. Combien "
          "y a-t-il de trèfles ?")]
''',
}


def make(L, seed, start, QX):
    s = BASE

    def rep(a, b):
        nonlocal s
        assert s.count(a) == 1, (s.count(a), a[:80])
        s = s.replace(a, b)

    rep('head = head.replace(\'OUT = "qcm"\', \'OUT = "qcm250"\')',
        f'head = head.replace(\'OUT = "qcm"\', \'OUT = "qcm{L}"\')\n'
        f'head = head.replace(\'f"Question {{n}}"\', \'f"Question {{n - {start - 1}}} {L}"\')')
    rep("R = random.Random(2026)", f"R = random.Random({seed})")
    col = 1 if L == "C" else 2
    for t in R:
        rep(t[0], t[col])
    for old, c_, d_, cnt in POOLS:
        assert s.count(old) == cnt, (s.count(old), old)
        s = s.replace(old, c_ if L == "C" else d_)
    i0 = s.index("CTX_Q = [")
    i1 = s.index("for N, a, b, txt in CTX_Q:")
    s = s[:i0] + CTX[L] + s[i1:]
    rep("# ============================== BUILD ==============================",
        QX + "\n# ============================== BUILD ==============================")
    rep("for i, (th, en, dr, op, ok, bx) in enumerate(ALL, 1):",
        SIG + f"for i, (th, en, dr, op, ok, bx) in enumerate(ALL, {start}):")
    rep('"""Builds all 250 QCM images', f'"""Série {L} ({start}-{start + 249}). Builds all 250 QCM images')
    return s


for L, seed, start, QX in [("C", 4417, 501, QC), ("D", 9183, 751, QD)]:
    open(f"/home/claude/bank{L}.py", "w", encoding="utf-8").write(make(L, seed, start, QX))
    print(f"bank{L}.py written")

# signature-only copies of A and B, to check that no C/D question repeats them
a = BASE.replace("for i, (th, en, dr, op, ok, bx) in enumerate(ALL, 1):", SIG + "for i, (th, en, dr, op, ok, bx) in enumerate(ALL, 1):")
open("/home/claude/sigA.py", "w", encoding="utf-8").write(a)
b = open("/home/claude/bankB.py", encoding="utf-8").read()
b = b.replace("for i, (th, en, dr, op, ok, bx) in enumerate(ALL, 251):", SIG + "for i, (th, en, dr, op, ok, bx) in enumerate(ALL, 251):")
assert "_sig" in b
open("/home/claude/sigB.py", "w", encoding="utf-8").write(b)
