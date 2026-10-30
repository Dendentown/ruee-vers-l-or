"""Banque CAPES : 50 types de questions x 4 jeux de valeurs.
Série A = questions 1-100, série B = 101-200 (n + 100 = même question, autres valeurs).
Toutes les bonnes réponses sont calculées ici."""
import json, math, random, subprocess, os
from fractions import Fraction as F
from math import comb, gcd, factorial



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


