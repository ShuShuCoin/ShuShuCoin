#!/usr/bin/env python3
"""Small public ShuShuCoin block explorer."""
import json, subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
CLI=['/opt/shushucoin/v1.14.9/bin/shushucoin-cli','-datadir=/root/.shushucoin']
def rpc(*args): return json.loads(subprocess.check_output(CLI+list(args),universal_newlines=True))
def supply(h):
 total=0
 for n,r in ((99999,1000000),(100000,500000),(100000,250000),(100000,125000),(100000,62500),(100000,31250)):
  x=min(h,n);total+=x*r;h-=x
  if h<=0:return total
 return total+h*10000
def blocks():
 tip=rpc('getblockcount');out=[]
 for h in range(max(0,tip-11),tip+1):
  b=rpc('getblock',rpc('getblockhash',str(h)),'1');out.append({'height':h,'hash':b['hash'],'time':b['time'],'tx':len(b['tx']),'confirmations':b['confirmations']})
 return list(reversed(out))
class H(BaseHTTPRequestHandler):
 def sendj(self,x):
  b=json.dumps(x,indent=2).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  u=urlparse(self.path)
  try:
   if u.path=='/api/chain':
    c=rpc('getblockchaininfo');self.sendj({'height':c['blocks'],'difficulty':c['difficulty'],'best_block':c['bestblockhash'],'issued_supply_shushu':supply(c['blocks'])});return
   if u.path=='/api/blocks':self.sendj(blocks());return
   if u.path=='/api/search':
    q=parse_qs(u.query).get('q',[''])[0].strip()
    if q.isdigit():self.sendj(rpc('getblock',rpc('getblockhash',q),'2'));return
    try:self.sendj(rpc('getblock',q,'2'));return
    except Exception:self.sendj(rpc('getrawtransaction',q,'1'));return
   if u.path!='/':self.send_error(404);return
   html='''<!doctype html><meta charset=utf-8><title>ShuShuCoin Explorer</title><style>body{margin:0;background:#101114;color:#f5e7b5;font:16px system-ui}main{max-width:1050px;margin:auto;padding:32px}h1{font-size:36px}input{width:70%;padding:14px;border-radius:9px;border:1px solid #66501e;background:#191a20;color:white}button{padding:14px 20px;border:0;border-radius:9px;background:#e3ad31;font-weight:bold}section{background:#1a1b22;border:1px solid #393021;border-radius:14px;padding:20px;margin:18px 0}.cards{display:flex;gap:12px;flex-wrap:wrap}.card{background:#25201a;border-radius:10px;padding:14px;min-width:180px}.muted{color:#aaa}a{color:#ffd369}pre{white-space:pre-wrap;word-break:break-all;color:#cfe8ff}table{width:100%;border-collapse:collapse}td,th{padding:10px;border-bottom:1px solid #38322a;text-align:left}td a{word-break:break-all}</style><main><h1>🐭 ShuShuCoin Explorer</h1><p class=muted>Mainnet block and transaction explorer</p><section><input id=q placeholder="Block height, block hash, or transaction ID"><button onclick="go()">Search</button><pre id=result></pre></section><section><div id=cards class=cards></div></section><section><h2>Latest blocks</h2><table><thead><tr><th>Height</th><th>Block hash</th><th>Transactions</th><th>Confirmations</th></tr></thead><tbody id=blocks></tbody></table></section></main><script>async function load(){let c=await fetch('/api/chain').then(r=>r.json());cards.innerHTML=`<div class=card>Height<br><b>${c.height}</b></div><div class=card>Difficulty<br><b>${c.difficulty}</b></div><div class=card>Issued supply<br><b>${Number(c.issued_supply_shushu).toLocaleString()} SHUSHU</b></div>`;let b=await fetch('/api/blocks').then(r=>r.json());blocks.innerHTML=b.map(x=>`<tr><td><a href='#' onclick="search('${x.height}')">${x.height}</a></td><td><a href='#' onclick="search('${x.hash}')">${x.hash.slice(0,22)}…</a></td><td>${x.tx}</td><td>${x.confirmations}</td></tr>`).join('')}async function search(q){result.textContent='Loading…';result.textContent=JSON.stringify(await fetch('/api/search?q='+encodeURIComponent(q)).then(r=>r.json()),null,2)}function go(){search(q.value)}load();setInterval(load,15000)</script>''';b=html.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
  except Exception as e:self.sendj({'error':str(e)})
 def log_message(self,*a):pass
HTTPServer(('0.0.0.0',3335),H).serve_forever()

