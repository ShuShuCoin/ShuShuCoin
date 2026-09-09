#!/usr/bin/env python3
"""Minimal authenticated ShuShuCoin CPU-mining pool endpoint."""
import argparse, hashlib, json, os, secrets, socketserver, struct, subprocess, time, uuid

CLI = ['/opt/shushucoin/v1.14.9/bin/shushucoin-cli', '-datadir=/root/.shushucoin']
ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
JOBS = {}

def rpc(method, *params):
    return subprocess.check_output(CLI + [method] + list(params), universal_newlines=True).strip()
def dsha(data): return hashlib.sha256(hashlib.sha256(data).digest()).digest()
def vi(n):
    if n < 0xfd: return bytes([n])
    if n <= 0xffff: return b'\xfd' + struct.pack('<H', n)
    if n <= 0xffffffff: return b'\xfe' + struct.pack('<I', n)
    return b'\xff' + struct.pack('<Q', n)
def b58decode(text):
    n = 0
    for ch in text: n = n * 58 + ALPHABET.index(ch)
    raw = n.to_bytes((n.bit_length() + 7) // 8, 'big')
    return b'\0' * (len(text) - len(text.lstrip('1'))) + raw
def p2pkh(address):
    raw = b58decode(address)
    if len(raw) != 25 or raw[0] != 63 or dsha(raw[:-4])[:4] != raw[-4:]:
        raise ValueError('invalid ShuShuCoin P2PKH address')
    return bytes.fromhex('76a914') + raw[1:21] + bytes.fromhex('88ac')
def script_num(n):
    if n == 0: return b''
    out = bytearray()
    while n:
        out.append(n & 0xff); n >>= 8
    if out[-1] & 0x80: out.append(0)
    return bytes(out)
def push(data):
    if len(data) < 76: return bytes([len(data)]) + data
    return b'\x4c' + bytes([len(data)]) + data
def merkle_root(hashes):
    while len(hashes) > 1:
        if len(hashes) & 1: hashes.append(hashes[-1])
        hashes = [dsha(hashes[i] + hashes[i+1]) for i in range(0, len(hashes), 2)]
    return hashes[0]
def make_job(address):
    tpl = json.loads(rpc('getblocktemplate', '{"rules":[]}'))
    height, value = tpl['height'], tpl['coinbasevalue']
    script_sig = push(script_num(height)) + push(secrets.token_bytes(4))
    coinbase = (struct.pack('<I', 1) + b'\x01' + b'\0' * 32 + struct.pack('<I', 0xffffffff) +
                vi(len(script_sig)) + script_sig + struct.pack('<I', 0xffffffff) + b'\x01' +
                struct.pack('<Q', value) + vi(len(p2pkh(address))) + p2pkh(address) + struct.pack('<I', 0))
    txs = [coinbase] + [bytes.fromhex(tx['data']) for tx in tpl['transactions']]
    root = merkle_root([dsha(tx) for tx in txs])
    bits = int(tpl['bits'], 16)
    target = (bits & 0x007fffff) << (8 * ((bits >> 24) - 3))
    ntime = max(int(time.time()), tpl['mintime'], tpl['curtime'])
    prefix = struct.pack('<I', tpl['version']) + bytes.fromhex(tpl['previousblockhash'])[::-1] + root + struct.pack('<II', ntime, bits)
    job_id = uuid.uuid4().hex
    JOBS[job_id] = {'prefix': prefix, 'body': vi(len(txs)) + b''.join(txs), 'target': target, 'created': time.time(), 'height': height}
    return {'job_id': job_id, 'height': height, 'header_prefix': prefix.hex(), 'target': format(target, '064x'), 'bits': tpl['bits'], 'coinbasevalue': value}
def submit(job_id, nonce):
    job = JOBS.pop(job_id, None)
    if job is None or time.time() - job['created'] > 120: return {'accepted': False, 'reason': 'stale-job'}
    if not isinstance(nonce, int) or nonce < 0 or nonce > 0xffffffff: return {'accepted': False, 'reason': 'bad-nonce'}
    header = job['prefix'] + struct.pack('<I', nonce)
    pow_raw = hashlib.scrypt(header, salt=header, n=1024, r=1, p=1, dklen=32)
    if int.from_bytes(pow_raw, 'little') > job['target']: return {'accepted': False, 'reason': 'high-hash'}
    reply = rpc('submitblock', (header + job['body']).hex())
    accepted = reply in ('', 'null')
    return {'accepted': accepted, 'reply': reply or 'null', 'block_hash': dsha(header)[::-1].hex(), 'pow_hash': pow_raw[::-1].hex()}
class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            request = json.loads(self.rfile.readline(65536).decode('utf-8'))
            if request.get('token') != self.server.token: raise ValueError('authentication failed')
            if request.get('method') == 'getjob': response = {'ok': True, 'job': make_job(request['address'])}
            elif request.get('method') == 'submit': response = {'ok': True, 'result': submit(request['job_id'], request['nonce'])}
            else: raise ValueError('unknown method')
        except Exception as exc:
            response = {'ok': False, 'error': str(exc)}
        self.wfile.write((json.dumps(response) + '\n').encode('utf-8'))
class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--bind', default='0.0.0.0'); parser.add_argument('--port', type=int, default=3333); args = parser.parse_args()
    token = os.environ.get('SHUSHU_POOL_TOKEN')
    if not token: raise SystemExit('SHUSHU_POOL_TOKEN is required')
    with Server((args.bind, args.port), Handler) as server:
        server.token = token
        server.serve_forever()
