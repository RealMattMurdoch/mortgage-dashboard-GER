# -*- coding: utf-8 -*-
# Financial-analyst accuracy harness.
# Independently re-computes the mortgage maths (a) by a from-scratch month-by-month
# amortiser written in Python and (b) by pure closed-form annuity formulae, then
# compares both against the app's own engine (exposed as window.MD_ENGINE under ?test)
# across a matrix of current-term and follow-on-term interest rates.
import sys, os, math, threading, http.server, socketserver, functools
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
def asc(s): return ''.join(c if ord(c)<128 else '?' for c in str(s))

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root (parent of tests/)
FILE = "Mortgage_Dashboard.html"
Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=DIR)
Handler.log_message = lambda *a, **k: None
httpd = socketserver.TCPServer(("127.0.0.1", 0), Handler)
PORT = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()
BASE = "http://127.0.0.1:%d/%s?test" % (PORT, FILE.replace(" ", "%20"))

from playwright.sync_api import sync_playwright

# ---------- independent reference maths (no app code involved) ----------
def annuity(bal, r, n):
    if n <= 0: return bal
    return bal/n if r <= 0 else bal*r/(1-(1+r)**(-n))

def cf_balance(P, rate_pct, pay, k):
    """Exact closed-form remaining balance after k monthly payments (pure formula)."""
    r = rate_pct/100/12
    return P*(1+r)**k - pay*((1+r)**k - 1)/r

MAX_MONTHS = 700  # must match the app engine's iteration cap

def py_amort(P, rate, pay, sy, fix, term, frate, fend, fpay=0, sonder=0, events=None):
    """From-scratch month-by-month amortiser following the documented rules."""
    events = events or []
    MR = rate/100/12
    deviate = (abs(frate - rate) > 1e-9) or (fpay > 0) or (fend != term)
    bal, months, totInt = float(P), 0, 0.0
    balFix, rPay = 0.0, None
    for m in range(MAX_MONTHS):
        if bal <= 1e-6: break
        year, mo = sy + m//12, m % 12
        inFix = year <= fix
        if deviate and (not inFix) and rPay is None:
            n = max(1, (fend - fix)*12)
            rPay = fpay if fpay > 0 else annuity(bal, frate/100/12, n)
        rate_m = MR if inFix else ((frate/100/12) if deviate else MR)
        pay_m = pay if inFix else (rPay if deviate else pay)
        if mo == 0 and sonder > 0 and sy+1 <= year <= fix:
            bal -= min(sonder, bal)
        ym = "%04d-%02d" % (year, mo+1)
        for e in events:
            if e["from"] == ym and e["amount"] > 0:
                bal -= min(e["amount"], bal)
        interest = bal*rate_m
        principal = pay_m - interest
        principal = min(principal, bal)
        if principal < 0: principal = 0
        bal -= principal; totInt += interest; months += 1
        if year == fix and mo == 11: balFix = max(0.0, bal)
    payoff = sy + (months-1)//12
    return dict(months=months, totInt=totInt, balFix=balFix, payoff=payoff)

# ---------- scenario matrix ----------
P0, SY, FIX, TERM = 300000, 2025, 2035, 2055
def pay_for(rate):
    """A realistic monthly payment for the given current rate (annuity over the full term)."""
    return round(annuity(P0, rate/100/12, (TERM-SY)*12), 2)
scenarios = []
for cur in [3.0, 3.80, 5.0, 6.0]:
    for fol in [cur, 5.0, 6.0, 8.0]:
        for sonder in [0, 1500]:
            scenarios.append(dict(rate=cur, pay=pay_for(cur), frate=fol, fend=TERM, fpay=0, sonder=sonder, events=[]))
# a remortgage-in-6-years style case: lump sum, follow-on rate change, shorter follow-on term
scenarios.append(dict(rate=3.80, pay=pay_for(3.80), frate=5.5, fend=2050, fpay=0, sonder=1500,
                      events=[{"from": "2030-06", "amount": 20000}]))
scenarios.append(dict(rate=3.80, pay=pay_for(3.80), frate=6.0, fend=2047, fpay=1800, sonder=0, events=[]))

results = []
def rec(ok, name, detail=""):
    results.append((bool(ok), name, str(detail)))
    print(("PASS" if ok else "FAIL"), "|", asc(name), ("" if not detail else ("-> "+asc(detail))))

with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    pg = b.new_context().new_page()
    pg.goto(BASE)
    pg.wait_for_function("window.MD_ENGINE && typeof MD_ENGINE.amortize==='function'", timeout=15000)

    # closed-form anchor: app engine's fixed-period balance must equal the pure formula at every current rate
    for cur in [3.0, 3.80, 5.0, 6.0, 8.0]:
        pmt = pay_for(cur)
        got = pg.evaluate("""(s)=>{var Q=MD_ENGINE.sampleProperty();Q.loan.ratePct=s.r;Q.loan.payment=s.pmt;Q.refinance={ratePct:s.r,termEndYear:2055,payment:0};MD_ENGINE.setEngineFrom(Q);return MD_ENGINE.amortize(0).balAt2035;}""", {"r": cur, "pmt": pmt})
        exp = cf_balance(P0, cur, pmt, (FIX-SY+1)*12)
        rec(abs(got-exp) < 0.05, "closed-form balance @ %.2f%% current rate" % cur, "exp %.2f vs app %.2f" % (exp, got))

    # full matrix: independent month-by-month vs the app engine
    for s in scenarios:
        exp = py_amort(P0, s["rate"], s["pay"], SY, FIX, TERM, s["frate"], s["fend"], s["fpay"], s["sonder"], s["events"])
        got = pg.evaluate("""(s)=>{var Q=MD_ENGINE.sampleProperty();Q.loan.principal=300000;Q.loan.ratePct=s.rate;Q.loan.payment=s.pay;Q.loan.startYear=2025;Q.loan.fixedUntilYear=2035;Q.loan.termEndYear=2055;Q.refinance={ratePct:s.frate,termEndYear:s.fend,payment:s.fpay};MD_ENGINE.setEngineFrom(Q);var r=MD_ENGINE.amortize(s.sonder,s.events,{ratePct:s.frate,termEndYear:s.fend,payment:s.fpay});return {months:r.months,totInt:r.totInt,balFix:r.balAt2035,payoff:r.payoffYear};}""", s)
        tag = "cur %.2f%% / follow-on %.2f%% / term %d / sonder %d%s" % (
            s["rate"], s["frate"], s["fend"], s["sonder"], (" / +oneoff" if s["events"] else (" / +manualpay" if s["fpay"] else "")))
        okm = exp["months"] == got["months"]
        oki = abs(exp["totInt"]-got["totInt"]) < 1.0
        okb = abs(exp["balFix"]-got["balFix"]) < 0.5
        okp = exp["payoff"] == got["payoff"]
        rec(okm and oki and okb and okp, tag,
            "exp[int=%.2f payoff=%d bal=%.2f] app[int=%.2f payoff=%d bal=%.2f]" % (
                exp["totInt"], exp["payoff"], exp["balFix"], got["totInt"], got["payoff"], got["balFix"]))
    b.close()

httpd.shutdown()
p = sum(1 for r in results if r[0]); t = len(results)
print("\n================ ANALYST ACCURACY: %d / %d checks agree ================" % (p, t))
if p != t:
    for ok, n, d in results:
        if not ok: print("  -", asc(n), "::", asc(d))
sys.exit(0 if p == t else 1)
