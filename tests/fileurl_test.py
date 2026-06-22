# -*- coding: utf-8 -*-
import sys, os, time
from pathlib import Path
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
def asc(s): return ''.join(c if ord(c)<128 else '?' for c in str(s))

DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root (parent of tests/)
FILE_URI=Path(os.path.join(DIR,"Mortgage_Dashboard.html")).as_uri()
print("file URI:", asc(FILE_URI))

from playwright.sync_api import sync_playwright

def run_engine(pw, label, **launch):
    print("\n==== Engine:", label, "====")
    try:
        b=pw.chromium.launch(headless=True, **launch)
    except Exception as e:
        print("  SKIP (cannot launch):", asc(e)[:160]); return None
    errs=[]
    ctx=b.new_context(); pg=ctx.new_page()
    pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.on("pageerror",lambda e: errs.append("PAGEERROR: "+str(e)))
    pg.goto(FILE_URI)
    try:
        pg.wait_for_function("document.getElementById('m-cold') && document.getElementById('m-cold').textContent.indexOf('1.100')>=0", timeout=10000)
        rendered=True
    except Exception:
        rendered=False
    # does file:// localStorage work + did bootstrap persist the index?
    ls_ok = pg.evaluate("(function(){try{localStorage.setItem('__t','1');var v=localStorage.getItem('__t')==='1';localStorage.removeItem('__t');return v;}catch(e){return false;}})()")
    idx1 = pg.evaluate("localStorage.getItem('mpd:index')")
    pg.reload()
    try: pg.wait_for_function("document.getElementById('m-cold')", timeout=10000)
    except Exception: pass
    idx2 = pg.evaluate("localStorage.getItem('mpd:index')")
    cold = pg.evaluate("var e=document.getElementById('m-cold');return e?e.textContent:''") if False else pg.eval_on_selector("#m-cold","e=>e.textContent")
    print("  app rendered sample:", rendered, "(m-cold="+asc(cold)+")")
    print("  localStorage usable on file://:", bool(ls_ok))
    print("  bootstrap wrote mpd:index:", idx1 is not None)
    print("  index persisted across reload:", (idx2 is not None and idx1==idx2))
    print("  console/page errors:", len(errs), (asc(errs[0]) if errs else ""))
    b.close()
    return {"rendered":rendered,"ls":bool(ls_ok),"persist":(idx2 is not None and idx1==idx2),"errs":len(errs)}

with sync_playwright() as pw:
    r1=run_engine(pw,"bundled Chromium")
    r2=run_engine(pw,"installed Google Chrome (channel=chrome)", channel="chrome")
    # Brave (Chromium-based) , try common install path
    brave=r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    if os.path.exists(brave):
        r3=run_engine(pw,"installed Brave", executable_path=brave)
    else:
        print("\n==== Engine: Brave ====\n  SKIP (brave.exe not at default path)")
