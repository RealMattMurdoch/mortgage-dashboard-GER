# -*- coding: utf-8 -*-
# German/English localisation test for the Mortgage Dashboard.
# Verifies the DE/EN toggle swaps static markup, dynamic builders, the wizard and the
# manage panel to proper German finance terminology, persists the choice, restores English,
# and never throws a console error. The maths and numbers are locale-independent and are
# covered by e2e_test.py / analyst_check.py; this file is purely about the words.
import sys, os, threading, http.server, socketserver, functools, tempfile
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
def asc(s): return "".join(c if ord(c) < 128 else "?" for c in str(s))

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # House-stuff project root
FILE = "Mortgage_Dashboard.html"

Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=DIR)
Handler.log_message = lambda *a, **k: None
httpd = socketserver.TCPServer(("127.0.0.1", 0), Handler)
PORT = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()
BASE = "http://127.0.0.1:%d/%s" % (PORT, FILE.replace(" ", "%20"))

from playwright.sync_api import sync_playwright

results = []
def check(name, cond, detail=""):
    results.append((bool(cond), name, str(detail)))
    print(("PASS" if cond else "FAIL"), "|", asc(name), ("" if not detail else ("-> " + asc(detail))))

console_errors = []
def wire(page):
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: console_errors.append("PAGEERROR: " + str(e)))

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context()
    page = ctx.new_page(); wire(page)
    page.goto(BASE)
    page.wait_for_function("document.getElementById('m-cold') && document.getElementById('m-cold').textContent.indexOf('1.100')>=0", timeout=15000)

    def t(id): return page.inner_text("#" + id)
    def attr(sel, a): return page.get_attribute(sel, a)
    # raw textContent, immune to CSS text-transform:uppercase used on the hero/tile labels
    def raw(sel): return page.eval_on_selector(sel, "e=>e.textContent")

    # ---- starts in English ----
    check("default locale is English (tab label)", "Monthly money" in t("tb-money"), t("tb-money"))
    check("toggle button offers DE", "DE" == t("lang-toggle"), t("lang-toggle"))
    check("html lang is en", attr("html", "lang") == "en", attr("html", "lang"))

    # ---- switch to German ----
    page.click("#lang-toggle")
    page.wait_for_function("document.getElementById('tb-money').textContent.indexOf('Monatliche')>=0", timeout=8000)

    de_checks = [
        ("tab uses Anschlussfinanzierung", "Anschlussfinanzierung" in t("tb-plan2035"), t("tb-plan2035")),
        ("tab Sondertilgung", "Sondertilgung" in t("tb-overpay"), t("tb-overpay")),
        ("hero question is German", "Was kostet mich" in raw("[data-i18n='hero_q']"), raw("[data-i18n='hero_q']")),
        ("Restschuld tile label", "Restschuld" in raw("[data-i18n='hero_owe']"), raw("[data-i18n='hero_owe']")),
        ("Werbungskosten section", "Werbungskosten" in t("tb-tax") or page.locator("text=Werbungskosten").count() > 0, ""),
        ("toggle now offers EN", "EN" == t("lang-toggle"), t("lang-toggle")),
        ("html lang is de", attr("html", "lang") == "de", attr("html", "lang")),
        # dynamic builder: hero anchor sentence rebuilt in German
        ("hero anchor in German", "nach Steuer" in t("hero-anchor") and "Mieter" in t("hero-anchor"), t("hero-anchor")),
        # dynamic builder: next-date tile uses German month
        ("next date uses German month", "Dez." in t("t-date"), t("t-date")),
    ]
    for n, c, d in de_checks:
        check(n, c, d)

    # ---- numbers stay de-DE on both sides (the rule): cold rent still 1.100,00 ----
    check("German keeps de-DE number format", "1.100,00" in t("m-cold"), t("m-cold"))

    # ---- the overpay takeaway (dynamic sentence) is German after dragging ----
    page.click("#tb-overpay")
    page.fill("#snum", "2000")
    page.eval_on_selector("#snum", "e=>e.dispatchEvent(new Event('input',{bubbles:true}))")
    page.wait_for_timeout(200)
    tk = page.inner_text("#o-takeaway")
    check("overpay takeaway is German", ("Sie tilgen" in tk) or ("Sondertilgung" in tk) or ("getilgt" in tk), tk[:60])

    # ---- wizard opens in German ----
    page.click("#prop-add")
    page.wait_for_selector("#wz_name", timeout=8000)
    check("wizard title German", "hinzu" in t("wz-h"), t("wz-h"))
    check("wizard Continue button German", "Weiter" in t("wz-next"), t("wz-next"))
    wlabel = page.inner_text("label[for='wz_name']")
    check("wizard field label German", "Anzeigename" in wlabel, wlabel)
    page.click("#wz-close")

    # ---- manage panel opens in German ----
    page.click("#prop-manage")
    page.wait_for_selector("[data-path='loan.ratePct']", timeout=8000)
    body = page.inner_text("#mg-body")
    check("manage uses Sollzins", "Sollzins" in body, "")
    check("manage uses Anschluss-Projektion", "Anschluss" in body, "")
    check("manage save button German", "speichern" in t("mg-save"), t("mg-save"))
    # data hooks the suite depends on must survive translation
    check("manage still exposes data-path fields", page.locator("[data-path='tax.dedInterest']").count() == 1, "")
    check("manage still exposes data-add hooks", page.locator("[data-add='hausgeld']").count() == 1, "")
    page.click("#mg-close")

    # ---- persistence across reload ----
    page.reload()
    page.wait_for_function("document.getElementById('tb-money').textContent.indexOf('Monatliche')>=0", timeout=8000)
    check("German persists across reload", "Monatliche" in t("tb-money"), t("tb-money"))

    # ---- back to English restores the originals exactly ----
    page.click("#lang-toggle")
    page.wait_for_function("document.getElementById('tb-money').textContent.indexOf('Monthly money')>=0", timeout=8000)
    check("toggle back restores English tab", "Monthly money" in t("tb-money"), t("tb-money"))
    check("English restores hero question", "really cost me" in raw("[data-i18n='hero_q']"), raw("[data-i18n='hero_q']"))
    check("English anchor restored", "after tax, to own" in t("hero-anchor"), t("hero-anchor"))

    check("no console/page errors during locale walkthrough", len(console_errors) == 0,
          "; ".join(console_errors[:4]) if console_errors else "")

    ctx.close()
    browser.close()

passed = sum(1 for ok, _, _ in results if ok)
total = len(results)
print("\n================ I18N RESULT: %d / %d passed ================" % (passed, total))
fails = [n for ok, n, _ in results if not ok]
if fails:
    print("FAILED:", "; ".join(asc(f) for f in fails))
    sys.exit(1)
