# -*- coding: utf-8 -*-
import sys, os, threading, http.server, socketserver, functools, json, tempfile, time
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
def asc(s): return ''.join(c if ord(c)<128 else '?' for c in str(s))

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root (parent of tests/)
FILE = "Mortgage_Dashboard.html"

# ---- serve the directory over http (localStorage needs a real origin) ----
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

prompt_answer = {"v": ""}
def on_dialog(d):
    if d.type == "prompt":
        d.accept(prompt_answer["v"])
    else:
        d.accept()

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    shot = lambda pg, n: pg.screenshot(path=os.path.join(tempfile.gettempdir(), "e2e_"+n+".png"))

    # ================= TEST 1: built-in ?test suite =================
    ctx = browser.new_context()
    page = ctx.new_page(); wire(page)
    page.goto(BASE + "?test")
    page.wait_for_selector("#testpanel .summary", timeout=15000)
    summary = page.inner_text("#testpanel .summary")
    fails = page.locator("#testpanel td.fail").all_inner_texts()
    check("built-in ?test suite present", "tests passed" in summary, summary)
    check("built-in ?test suite ALL GREEN", ("✓" in summary) and (len(fails) == 0), summary + (" fails=" + str(fails) if fails else ""))
    shot(page, "01_tests")
    ctx.close()

    # ================= TEST 2: sample property renders its baseline numbers =================
    ctx = browser.new_context()
    page = ctx.new_page(); wire(page)
    page.goto(BASE)
    page.wait_for_function("document.getElementById('m-cold') && document.getElementById('m-cold').textContent.indexOf('1.100')>=0", timeout=15000)
    def t(id): return page.inner_text("#" + id)
    qb = {
        "m-mort": "1.397,87", "m-hg": "350,00", "m-sev": "30,00", "m-out": "1.777,87",
        "m-cold": "1.100,00", "m-warm": "1.400,00", "hero-net": "-141,08", "td-total": "19.965",
        "f-loan": "300.000", "hdr-title": "Sample apartment",
        "tsl-v": "42,00%", "f-rate": "3,80%", "f-eff": "3,87%", "idx-v": "2,00%",
    }
    for id, exp in qb.items():
        check("sample "+id+" contains "+exp, exp in t(id), t(id))
    check("sample sale profit shown", "€" in t("sale-profit"), t("sale-profit"))
    shot(page, "02_quickborn")

    # ================= TEST 2b: one-off Sondertilgung via the Overpay tab =================
    tc = lambda id: page.eval_on_selector("#"+id, "e=>e.textContent")
    page.click("#tb-overpay")
    page.wait_for_selector("#oneoff-add", timeout=8000)
    bbal_before = tc("b-bal"); bint_before = tc("b-int")
    page.click("#oneoff-add")
    page.wait_for_timeout(350)
    check("one-off editor adds an input row", page.locator("#oneoff-list .drow").count() >= 1, str(page.locator("#oneoff-list .drow").count()))
    check("one-off lowers balance at fixed end", bbal_before != tc("b-bal"), bbal_before+" -> "+tc("b-bal"))
    check("one-off lowers lifetime interest", bint_before != tc("b-int"), bint_before+" -> "+tc("b-int"))
    # set the one-off above the annual cap to trigger the warning
    page.fill("#oneoff-list input[data-oo='amount']", "20000")
    page.eval_on_selector("#oneoff-list input[data-oo='amount']", "e=>e.dispatchEvent(new Event('change',{bubbles:true}))")
    page.wait_for_timeout(300)
    check("over-cap one-off shows allowance warning", page.locator("#oneoff-warn").is_visible(), tc("oneoff-warn")[:40])
    shot(page, "02b_oneoff")
    # remove the one-off so the refinance test runs on a clean baseline
    while page.locator("#oneoff-list [data-oodel]").count() > 0:
        page.locator("#oneoff-list [data-oodel]").first.click(); page.wait_for_timeout(150)
    check("one-off removed, balance restored", bbal_before == tc("b-bal"), bbal_before+" == "+tc("b-bal"))

    # ================= TEST 2c: follow-on rate projection via the after-2035 tab =================
    def change(sel, val):
        page.fill(sel, val); page.eval_on_selector(sel, "e=>e.dispatchEvent(new Event('change',{bubbles:true}))")
    page.click("#tb-plan2035")
    page.wait_for_selector("#refi-rate", timeout=8000)
    check("after-2035 tab is framed as a projection", "Projection" in tc("refi-summary"), tc("refi-summary")[:40])
    aint_before = tc("a-int")
    # worse-case: 8% preset should raise lifetime interest and the slider label
    page.click("#rate-presets [data-rate='8']")
    page.wait_for_timeout(400)
    check("8% preset updates the rate label", "8,00" in tc("rsl-v"), tc("rsl-v"))
    check("higher follow-on rate raises lifetime interest", aint_before != tc("a-int"), aint_before+" -> "+tc("a-int"))
    check("scenario table lists multiple rates", page.locator("#refi-scen tr").count() >= 3, str(page.locator("#refi-scen tr").count()))
    # shorten the follow-on term at the current rate -> earlier payoff
    apay_before = tc("a-pay")
    change("#refi-rate", "3.80"); change("#refi-end", "2045")
    page.wait_for_timeout(400)
    check("shorter follow-on term shortens payoff", apay_before != tc("a-pay") and "2045" in tc("a-pay"), apay_before+" -> "+tc("a-pay"))
    check("projected payoff tile shows 2045", "2045" in tc("refi-r-payoff"), tc("refi-r-payoff"))
    # reset to contract restores the current-rate continuation
    page.click("#refi-reset"); page.wait_for_timeout(400)
    check("reset restores current-rate projection (3,80%)", "3,80" in tc("rsl-v"), tc("rsl-v"))
    check("reset restores payoff to 2055", "2055" in tc("a-pay"), tc("a-pay"))
    page.click("#tb-money"); page.wait_for_timeout(150)

    # ================= TEST 3: add a dummy 'Lübeck flat' via the wizard =================
    page.click("#prop-add")
    page.wait_for_selector("#wz_name", timeout=8000)
    steps = [
        {"wz_name":"Lübeck flat","wz_addr":"Musterstr 1, Lübeck","wz_country":"DE"},
        {"wz_price":"250000","wz_ek":"30000","wz_pc":"20000","wz_sc":"3.57"},
        {"wz_loan":"220000","wz_rate":"3.4","wz_pay":"1050","wz_sy":"2026","wz_fix":"2036","wz_term":"2056","wz_smax":"5000"},
        {"wz_hg":"210","wz_sev":"0"},
        {"wz_rfrom":"2026-09","wz_cold":"980","wz_warm":"1250","wz_idx":"2"},
        {"wz_tax":"42","wz_afa":"4000","wz_dhg":"2000","wz_dgr":"250","wz_dint":"7400","wz_reno":"30000"},
        {"wz_appr":"2","wz_sonder":"1000"},
    ]
    for i, fields in enumerate(steps):
        first_id = list(fields.keys())[0]
        page.wait_for_selector("#"+first_id, timeout=8000)
        for fid, val in fields.items():
            page.fill("#"+fid, val)
        page.click("#wz-next")
        time.sleep(0.15)
    # wizard should have finished and activated Lübeck
    page.wait_for_function("document.getElementById('m-cold') && document.getElementById('m-cold').textContent.indexOf('980')>=0", timeout=8000)
    check("Lübeck active after wizard (cold rent 980)", "980" in t("m-cold"), t("m-cold"))
    check("Lübeck warm rent 1.250", "1.250" in t("m-warm"), t("m-warm"))
    check("Lübeck hero anchor shows 250.000", "250.000" in t("hero-anchor"), t("hero-anchor"))
    check("Lübeck loan 220.000 in facts", "220.000" in t("f-loan"), t("f-loan"))
    check("Lübeck effective rate derived from its 3,4% nominal", "3,4" in t("f-eff"), t("f-eff"))
    check("Lübeck NOT showing sample 1.100", "1.100" not in t("m-cold"), t("m-cold"))
    check("Lübeck pill exists", page.locator(".proppill", has_text="Lübeck flat").count() >= 1, "")
    shot(page, "03_luebeck")

    # ================= TEST 4: switch isolation =================
    page.locator(".proppill", has_text="Sample apartment").first.click()
    page.wait_for_function("document.getElementById('m-cold').textContent.indexOf('1.100')>=0", timeout=8000)
    check("switch back to sample restores 1.100", "1.100" in t("m-cold"), t("m-cold"))
    page.locator(".proppill", has_text="Lübeck flat").first.click()
    page.wait_for_function("document.getElementById('m-cold').textContent.indexOf('980')>=0", timeout=8000)
    check("switch to Lübeck restores 980 (no leak)", "980" in t("m-cold"), t("m-cold"))

    # ================= TEST 5: dated edit (future cost rise lowers sale profit) =================
    profit_before = t("sale-profit")
    page.click("#prop-manage")
    page.wait_for_selector("[data-add='hausgeld']", timeout=8000)
    page.click("[data-add='hausgeld']")
    time.sleep(0.2)
    # set the newly added hausgeld value (last value input) high
    val_inputs = page.locator("[data-k='hausgeld'][data-f='value']")
    val_inputs.nth(val_inputs.count()-1).fill("600")
    page.click("#mg-save")
    page.wait_for_timeout(400)
    profit_after = t("sale-profit")
    check("dated cost rise changes sale profit", profit_before != profit_after, profit_before+" -> "+profit_after)

    # ============ TEST 5b: Edit panel completeness audit + a remortgage edit ============
    required = ["loan.principal","loan.ratePct","loan.payment","loan.startYear","loan.fixedUntilYear",
                "loan.termEndYear","loan.sonderMax","loan.varRatePct","refinance.ratePct","refinance.termEndYear",
                "refinance.payment","purchase.price","purchase.eigenkapital","purchase.purchaseCosts",
                "purchase.condoBonus","purchase.sellCostPct","purchase.saleYears","tax.marginalPct","tax.dedInterest",
                "tax.dedAfa","tax.dedHausgeld","tax.dedSev","tax.dedGrundsteuer","tax.dedOther","tax.dedFinancingOneOff","tax.renoLimit",
                "assumptions.idxPct","assumptions.apprPct","assumptions.sonderAnnual","asOfMonth","asOfPayments"]
    page.click("#prop-manage")
    page.wait_for_selector("[data-path='loan.ratePct']", timeout=8000)
    missing = [p for p in required if page.locator("[data-path='%s']" % p).count() == 0]
    check("Edit panel exposes every pivotal credit/tax/purchase field", not missing, "missing: " + ",".join(missing) if missing else "all %d present" % len(required))
    # remortgage: change the current rate AND monthly payment, expect lifetime interest to move
    aint_before = tc("a-int")
    change("[data-path='loan.ratePct']", "5.25"); change("[data-path='loan.payment']", "1200")
    page.click("#mg-save"); page.wait_for_timeout(400)
    check("remortgage edit (rate + payment) changes lifetime interest", aint_before != tc("a-int"), aint_before + " -> " + tc("a-int"))
    # a tax-deduction edit must move the after-tax monthly figure
    net_before = t("hero-net")
    page.click("#prop-manage"); page.wait_for_selector("[data-path='tax.dedInterest']", timeout=8000)
    change("[data-path='tax.dedInterest']", "20000")
    page.click("#mg-save"); page.wait_for_timeout(400)
    check("tax-deduction edit changes the after-tax monthly figure", net_before != t("hero-net"), net_before + " -> " + t("hero-net"))
    shot(page, "05b_editpanel")

    # ================= TEST 6: export -> import round-trip =================
    with page.expect_download() as di:
        page.click("#prop-export")
    dl = di.value
    out_path = os.path.join(tempfile.gettempdir(), "luebeck_export.json")
    dl.save_as(out_path)
    with open(out_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    check("export produced JSON with Lübeck name", data.get("name") == "Lübeck flat", data.get("name"))
    check("export carries NO seeded condoBonus", data.get("purchase",{}).get("condoBonus") == 0, data.get("purchase",{}).get("condoBonus"))
    page.set_input_files("#importfile", out_path)
    page.wait_for_timeout(500)
    check("import created a copy pill", page.locator(".proppill", has_text="imported").count() >= 1, "")
    shot(page, "06_after_import")

    # ================= TEST 7: delete the imported copy =================
    pills_before = page.locator(".proppill").count()
    prompt_answer["v"] = "Lübeck flat (imported)"
    page.on("dialog", on_dialog)
    # make the imported copy active, then delete
    page.locator(".proppill", has_text="imported").first.click()
    page.wait_for_timeout(300)
    page.click("#prop-delete")
    page.wait_for_timeout(600)
    pills_after = page.locator(".proppill").count()
    check("delete removed a property", pills_after == pills_before - 1, str(pills_before)+" -> "+str(pills_after))

    # ================= console errors =================
    check("no console/page errors during walkthrough", len(console_errors) == 0, "; ".join(console_errors[:5]))

    ctx.close()
    browser.close()

httpd.shutdown()
passed = sum(1 for r in results if r[0]); total = len(results)
print("\n================ E2E RESULT: %d / %d passed ================" % (passed, total))
if passed != total:
    print("FAILURES:")
    for ok, n, d in results:
        if not ok: print("  -", asc(n), "::", asc(d))
sys.exit(0 if passed == total else 1)
