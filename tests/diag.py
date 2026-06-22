# -*- coding: utf-8 -*-
import os, threading, http.server, socketserver, functools, time
DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root (parent of tests/)
H=functools.partial(http.server.SimpleHTTPRequestHandler,directory=DIR); H.log_message=lambda *a,**k:None
httpd=socketserver.TCPServer(("127.0.0.1",0),H); PORT=httpd.server_address[1]
threading.Thread(target=httpd.serve_forever,daemon=True).start()
from playwright.sync_api import sync_playwright
msgs=[]
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True); ctx=b.new_context(); pg=ctx.new_page()
    pg.on("console",lambda m: msgs.append(m.type+": "+m.text))
    pg.on("pageerror",lambda e: msgs.append("PAGEERROR: "+str(e)))
    pg.goto("http://127.0.0.1:%d/Mortgage_Dashboard.html?test"%PORT)
    time.sleep(2)
    has=pg.evaluate("!!document.getElementById('testpanel')")
    bodyloaded=pg.evaluate("!!document.getElementById('m-cold')")
    print("testpanel present:",has,"| app rendered:",bodyloaded)
    print("--- console/page messages ---")
    for m in msgs[:30]: print(m)
    b.close()
httpd.shutdown()
