#!/usr/bin/env python3
"""Public ShuShuCoin mainnet block explorer."""
import json, re, subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
CLI=['/opt/shushucoin/v1.14.9/bin/shushucoin-cli','-datadir=/root/.shushucoin']
class RPCError(Exception): pass
def rpc(*args):
 p=subprocess.run(CLI+list(args),stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
 if p.returncode:
  raise RPCError((p.stderr or p.stdout or 'RPC command failed').strip())
 raw=p.stdout.strip()
 try:return json.loads(raw)
 except ValueError:return raw
def supply(h):
 total=0
 for n,r in ((99999,1000000),(100000,500000),(100000,250000),(100000,125000),(100000,62500),(100000,31250)):
  x=min(h,n);total+=x*r;h-=x
  if h<=0:return total
 return total+h*10000
def payout(tx):
 try:
  s=tx['vout'][0]['scriptPubKey']
  return (s.get('addresses') or [s.get('address') or 'Unknown'])[0]
 except (KeyError,IndexError,TypeError):return 'Unknown'
def blocks():
 tip=rpc('getblockcount');out=[]
 for h in range(max(0,tip-11),tip+1):
  b=rpc('getblock',rpc('getblockhash',str(h)),'2')
  coinbase=b['tx'][0]
  out.append({'height':h,'hash':b['hash'],'time':b['time'],'tx':len(b['tx']),'confirmations':b['confirmations'],'size':b.get('size',0),'miner_address':payout(coinbase),'reward_shushu':sum(v.get('value',0) for v in coinbase.get('vout',[]))})
 return list(reversed(out))
def address_result(q):
 # This chain does not expose scantxoutset, so scan its compact mainnet history.
 # Limit keeps the explorer responsive as the chain grows.
 tip=rpc('getblockcount'); first=max(0,tip-9999); matches=[]; total=0
 for h in range(first,tip+1):
  b=rpc('getblock',rpc('getblockhash',str(h)),'2')
  for tx in b.get('tx',[]):
   for v in tx.get('vout',[]):
    s=v.get('scriptPubKey',{}); addrs=s.get('addresses') or [s.get('address')]
    if q in addrs:
     amount=v.get('value',0);total+=amount
     matches.append({'height':h,'block_hash':b['hash'],'time':b['time'],'txid':tx['txid'],'vout':v.get('n'),'amount_shushu':amount,'confirmations':b.get('confirmations',0)})
 return {'query_type':'address','address':q,'note':'Matching outputs in the most recent 10,000 blocks. Spend status is not indexed yet.','total_received_shushu':total,'matching_output_count':len(matches),'outputs':list(reversed(matches))}
class H(BaseHTTPRequestHandler):
 def sendj(self,x,status=200):
  b=json.dumps(x,indent=2).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  u=urlparse(self.path)
  try:
   if u.path=='/api/chain':
    c=rpc('getblockchaininfo');self.sendj({'height':c['blocks'],'difficulty':c['difficulty'],'best_block':c['bestblockhash'],'issued_supply_shushu':supply(c['blocks']),'estimated_network_hashrate_hs':round(c['difficulty']*4294967296/60,2)});return
   if u.path=='/api/blocks':self.sendj(blocks());return
   if u.path=='/api/search':
    q=parse_qs(u.query).get('q',[''])[0].strip()
    if not q:raise RPCError('Enter a block height, block hash, transaction ID, or SHUSHU address.')
    if q.isdigit():self.sendj({'query_type':'block_height','block':rpc('getblock',rpc('getblockhash',q),'2')});return
    if re.match(r'^S[1-9A-HJ-NP-Za-km-z]{25,40}$',q):self.sendj(address_result(q));return
    if re.match(r'^[0-9a-fA-F]{64}$',q):
     try:self.sendj({'query_type':'block','block':rpc('getblock',q,'2')});return
     except RPCError:self.sendj({'query_type':'transaction','transaction':rpc('getrawtransaction',q,'1')});return
    raise RPCError('Unrecognized search format.')
   if u.path!='/':self.send_error(404);return
   html='''<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>ShuShuCoin Explorer</title><style>body{margin:0;background:#101114;color:#f5e7b5;font:16px system-ui}main{max-width:1200px;margin:auto;padding:26px}h1{font-size:34px;margin-bottom:4px}input{width:min(72%,680px);padding:14px;border-radius:9px;border:1px solid #66501e;background:#191a20;color:white}button{padding:14px 20px;border:0;border-radius:9px;background:#e3ad31;font-weight:bold;cursor:pointer}section{background:#1a1b22;border:1px solid #393021;border-radius:14px;padding:20px;margin:18px 0}.cards{display:flex;gap:12px;flex-wrap:wrap}.card{background:#25201a;border-radius:10px;padding:14px;min-width:180px}.muted{color:#aaa}a{color:#ffd369}pre{white-space:pre-wrap;word-break:break-all;color:#cfe8ff;max-height:520px;overflow:auto}.scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:10px;border-bottom:1px solid #38322a;text-align:left;white-space:nowrap}td a{word-break:break-all}.hash{font-family:ui-monospace,monospace;max-width:235px;overflow:hidden;text-overflow:ellipsis}@media(max-width:700px){main{padding:14px}input{width:62%}table{font-size:12px}td,th{padding:7px}}</style><main><h1>🐭 ShuShuCoin Explorer</h1><p class=muted>Mainnet · chain data refreshes every 15 seconds</p><section><input id=q placeholder="Block height, hash, transaction ID, or SHUSHU address" onkeydown="if(event.key==='Enter')go()"><button onclick="go()">Search</button><p class=muted>Address searches show currently unspent outputs.</p><pre id=result></pre></section><section><div id=cards class=cards></div></section><section><h2>Latest blocks</h2><div class=scroll><table><thead><tr><th>Height</th><th>Block hash</th><th>Time</th><th>Transactions</th><th>Reward</th><th>Miner payout address</th><th>Size</th><th>Confirmations</th></tr></thead><tbody id=blocks></tbody></table></div></section></main><script>const fmt=n=>Number(n).toLocaleString();const time=t=>new Date(t*1000).toLocaleString();async function api(u){let r=await fetch(u),j=await r.json();if(!r.ok||j.error)throw Error(j.error||r.statusText);return j}async function load(){try{let c=await api('/api/chain');cards.innerHTML=`<div class=card>Height<br><b>${fmt(c.height)}</b></div><div class=card>Difficulty<br><b>${c.difficulty}</b></div><div class=card>Issued supply<br><b>${fmt(c.issued_supply_shushu)} SHUSHU</b></div><div class=card>Estimated network hash rate<br><b>${fmt(c.estimated_network_hashrate_hs)} H/s</b></div>`;let b=await api('/api/blocks');blocks.innerHTML=b.map(x=>`<tr><td><a href='#' onclick="search('${x.height}');return false">${x.height}</a></td><td class=hash title='${x.hash}'><a href='#' onclick="search('${x.hash}');return false">${x.hash}</a></td><td>${time(x.time)}</td><td>${x.tx}</td><td>${fmt(x.reward_shushu)} SHUSHU</td><td class=hash title='${x.miner_address}'><a href='#' onclick="search('${x.miner_address}');return false">${x.miner_address}</a></td><td>${fmt(x.size)} B</td><td>${fmt(x.confirmations)}</td></tr>`).join('')}catch(e){result.textContent='Load error: '+e.message}}async function search(q){result.textContent='Loading…';try{result.textContent=JSON.stringify(await api('/api/search?q='+encodeURIComponent(q)),null,2)}catch(e){result.textContent='Search error: '+e.message}}function go(){search(document.getElementById('q').value.trim())}load();setInterval(load,15000)</script>''';b=html.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
  except RPCError as e:self.sendj({'error':str(e)},400)
  except Exception as e:self.sendj({'error':'Internal explorer error: '+str(e)},500)
 def log_message(self,*a):pass
HTTPServer(('0.0.0.0',3335),H).serve_forever()


