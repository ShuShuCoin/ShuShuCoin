#!/usr/bin/env python3
"""Authenticated ShuShuCoin CPU mining pool with live miner telemetry."""
import argparse, hashlib, json, os, secrets, socketserver, struct, subprocess, time, uuid, threading
from collections import Counter
from http.server import BaseHTTPRequestHandler, HTTPServer

CLI=['/opt/shushucoin/v1.14.9/bin/shushucoin-cli','-datadir=/root/.shushucoin']; ALPHABET='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
JOBS={}; MINERS={}; LOCK=threading.RLock(); JOB_TTL=1800; ACTIVE_SECONDS=45

def rpc(method,*params): return subprocess.check_output(CLI+[method]+list(params),universal_newlines=True).strip()
def dsha(data): return hashlib.sha256(hashlib.sha256(data).digest()).digest()
def vi(n):
 if n<0xfd:return bytes([n])
 if n<=0xffff:return b'\xfd'+struct.pack('<H',n)
 if n<=0xffffffff:return b'\xfe'+struct.pack('<I',n)
 return b'\xff'+struct.pack('<Q',n)
def b58decode(text):
 n=0
 for ch in text:n=n*58+ALPHABET.index(ch)
 raw=n.to_bytes((n.bit_length()+7)//8,'big'); return b'\0'*(len(text)-len(text.lstrip('1')))+raw
def p2pkh(address):
 raw=b58decode(address)
 if len(raw)!=25 or raw[0]!=63 or dsha(raw[:-4])[:4]!=raw[-4:]:raise ValueError('invalid ShuShuCoin P2PKH address')
 return bytes.fromhex('76a914')+raw[1:21]+bytes.fromhex('88ac')
def script_num(n):
 if n==0:return b''
 out=bytearray()
 while n:out.append(n&0xff);n>>=8
 if out[-1]&0x80:out.append(0)
 return bytes(out)
def push(data): return (bytes([len(data)]) if len(data)<76 else b'\x4c'+bytes([len(data)]))+data
def merkle_root(hashes):
 while len(hashes)>1:
  if len(hashes)&1:hashes.append(hashes[-1])
  hashes=[dsha(hashes[i]+hashes[i+1]) for i in range(0,len(hashes),2)]
 return hashes[0]
def touch(address,rate=None,**event):
 now=time.time()
 with LOCK:
  m=MINERS.setdefault(address,{'address':address,'first_seen':now,'last_seen':now,'hashrate':0.0,'jobs':0,'submissions':0,'accepted':0,'stale':0,'rejected':0})
  m['last_seen']=now
  if rate is not None:
   try:m['hashrate']=max(0.0,float(rate))
   except (TypeError,ValueError):pass
  for k,v in event.items():m[k]=m.get(k,0)+v
 return m
def make_job(address,rate=None):
 tpl=json.loads(rpc('getblocktemplate','{"rules":[]}')); height,value=tpl['height'],tpl['coinbasevalue']; previous=tpl['previousblockhash']
 script_sig=push(script_num(height))+push(secrets.token_bytes(4)); script=p2pkh(address)
 coinbase=struct.pack('<I',1)+b'\x01'+b'\0'*32+struct.pack('<I',0xffffffff)+vi(len(script_sig))+script_sig+struct.pack('<I',0xffffffff)+b'\x01'+struct.pack('<Q',value)+vi(len(script))+script+struct.pack('<I',0)
 txs=[coinbase]+[bytes.fromhex(tx['data']) for tx in tpl['transactions']]; root=merkle_root([dsha(tx) for tx in txs]); bits=int(tpl['bits'],16); target=(bits&0x007fffff)<<(8*((bits>>24)-3)); ntime=max(int(time.time()),tpl['mintime'],tpl['curtime']); prefix=struct.pack('<I',tpl['version'])+bytes.fromhex(previous)[::-1]+root+struct.pack('<II',ntime,bits); job_id=uuid.uuid4().hex
 with LOCK:JOBS[job_id]={'prefix':prefix,'body':vi(len(txs))+b''.join(txs),'target':target,'created':time.time(),'height':height,'previous':previous,'address':address}; touch(address,rate,jobs=1)
 return {'job_id':job_id,'height':height,'header_prefix':prefix.hex(),'target':format(target,'064x'),'bits':tpl['bits'],'coinbasevalue':value}
def stale(job):
 return job is None or time.time()-job['created']>JOB_TTL or rpc('getbestblockhash')!=job['previous']
def heartbeat(job_id,address,rate):
 with LOCK:job=JOBS.get(job_id)
 touch(address,rate)
 return {'stale':stale(job),'height':job['height'] if job else None}
def submit(job_id,nonce):
 with LOCK:job=JOBS.pop(job_id,None)
 if job is None or stale(job):
  if job:touch(job['address'],None,submissions=1,stale=1)
  return {'accepted':False,'reason':'stale-job'}
 if not isinstance(nonce,int) or nonce<0 or nonce>0xffffffff:touch(job['address'],None,submissions=1,rejected=1);return {'accepted':False,'reason':'bad-nonce'}
 header=job['prefix']+struct.pack('<I',nonce); pow_raw=hashlib.scrypt(header,salt=header,n=1024,r=1,p=1,dklen=32)
 if int.from_bytes(pow_raw,'little')>job['target']:touch(job['address'],None,submissions=1,rejected=1);return {'accepted':False,'reason':'high-hash'}
 reply=rpc('submitblock',(header+job['body']).hex()); accepted=reply in ('','null'); touch(job['address'],None,submissions=1,**({'accepted':1} if accepted else {'rejected':1}))
 return {'accepted':accepted,'reply':reply or 'null','block_hash':dsha(header)[::-1].hex(),'pow_hash':pow_raw[::-1].hex()}
def snapshot():
 now=time.time()
 with LOCK:
  miners=[dict(m,online=(now-m['last_seen']<=ACTIVE_SECONDS),seconds_since_seen=round(now-m['last_seen'],1)) for m in MINERS.values()]
  miners.sort(key=lambda m:(not m['online'],-m['last_seen']))
  active=[m for m in miners if m['online']]
  return {'generated_at':int(now),'active_miners':len(active),'known_miners':len(miners),'reported_hashrate_hs':round(sum(m['hashrate'] for m in active),2),'miners':miners,'pool':{'job_ttl_seconds':JOB_TTL,'active_window_seconds':ACTIVE_SECONDS,'blocks_accepted':sum(m['accepted'] for m in miners),'stale_submissions':sum(m['stale'] for m in miners)}}
class Handler(socketserver.StreamRequestHandler):
 def handle(self):
  try:
   request=json.loads(self.rfile.readline(65536).decode());
   if request.get('token')!=self.server.token:raise ValueError('authentication failed')
   method=request.get('method'); address=request.get('address')
   if method=='getjob':response={'ok':True,'job':make_job(address,request.get('hashrate'))}
   elif method=='heartbeat':response={'ok':True,'status':heartbeat(request['job_id'],address,request.get('hashrate'))}
   elif method=='submit':response={'ok':True,'result':submit(request['job_id'],request['nonce'])}
   elif method=='stats':response={'ok':True,'stats':snapshot()}
   else:raise ValueError('unknown method')
  except Exception as exc:response={'ok':False,'error':str(exc)}
  self.wfile.write((json.dumps(response,separators=(',',':'))+'\n').encode())
class Server(socketserver.ThreadingTCPServer):allow_reuse_address=True
class StatusServer(socketserver.ThreadingMixIn, HTTPServer):
 daemon_threads=True
 allow_reuse_address=True
class StatusHandler(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path not in ('/','/status.json'):self.send_error(404);return
  data=snapshot()
  if self.path=='/status.json':body=json.dumps(data,indent=2).encode();ctype='application/json'
  else:
   rows=''.join('<tr><td>%s</td><td>%s</td><td>%.1f</td><td>%s</td><td>%s</td><td>%s</td></tr>'%(m['address'],('online' if m['online'] else 'idle'),m['hashrate'],m['accepted'],m['stale'],m['seconds_since_seen']) for m in data['miners'])
   body=('<!doctype html><meta charset=utf-8><title>ShuShuCoin Pool</title><h1>ShuShuCoin Pool Status</h1><p>Active miners: %s | Reported hashrate: %s H/s | Accepted blocks: %s | Stale submits: %s</p><table border=1 cellpadding=6><tr><th>Address</th><th>Status</th><th>H/s</th><th>Blocks</th><th>Stale</th><th>Last seen (s)</th></tr>%s</table><p><a href=/status.json>JSON</a></p>'%(data['active_miners'],data['reported_hashrate_hs'],data['pool']['blocks_accepted'],data['pool']['stale_submissions'],rows)).encode();ctype='text/html; charset=utf-8'
  self.send_response(200);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def log_message(self,*args):pass
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--bind',default='0.0.0.0');p.add_argument('--port',type=int,default=3333);p.add_argument('--status-bind',default='0.0.0.0');p.add_argument('--status-port',type=int,default=3334);a=p.parse_args();token=os.environ.get('SHUSHU_POOL_TOKEN')
 if not token:raise SystemExit('SHUSHU_POOL_TOKEN is required')
 status=StatusServer((a.status_bind,a.status_port),StatusHandler);threading.Thread(target=status.serve_forever,daemon=True).start()
 with Server((a.bind,a.port),Handler) as server:server.token=token;server.serve_forever()

