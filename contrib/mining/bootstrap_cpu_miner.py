#!/usr/bin/env python3
"""Mine one direct-Scrypt ShuShuCoin block through local getblocktemplate RPC."""
import argparse, hashlib, json, struct, subprocess, time
from pathlib import Path

CLI = ['/opt/shushucoin/v1.14.9/bin/shushucoin-cli', '-datadir=/root/.shushucoin']
ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def rpc(method, *params):
    return subprocess.check_output(CLI + [method] + list(params), universal_newlines=True).strip()

def dsha(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def varint(n):
    if n < 0xfd: return bytes([n])
    if n <= 0xffff: return b'\xfd' + struct.pack('<H', n)
    if n <= 0xffffffff: return b'\xfe' + struct.pack('<I', n)
    return b'\xff' + struct.pack('<Q', n)

def b58decode(text):
    n = 0
    for ch in text:
        n = n * 58 + ALPHABET.index(ch)
    raw = n.to_bytes((n.bit_length() + 7) // 8, 'big')
    return b'\0' * (len(text) - len(text.lstrip('1'))) + raw

def p2pkh_script(address):
    raw = b58decode(address)
    if len(raw) != 25 or raw[0] != 63 or dsha(raw[:-4])[:4] != raw[-4:]:
        raise ValueError('expected a valid ShuShuCoin P2PKH address')
    return bytes.fromhex('76a914') + raw[1:21] + bytes.fromhex('88ac')

def coinbase(height, value, script_pubkey):
    # Height 1 uses OP_1 OP_0. The script is two bytes, satisfying coinbase-size rules.
    script_sig = b'\x51\x00' if height == 1 else b'\x02' + struct.pack('<H', height)
    return (struct.pack('<I', 1) + b'\x01' + b'\0' * 32 + struct.pack('<I', 0xffffffff) +
            varint(len(script_sig)) + script_sig + struct.pack('<I', 0xffffffff) +
            b'\x01' + struct.pack('<Q', value) + varint(len(script_pubkey)) + script_pubkey + struct.pack('<I', 0))

def mine(address):
    tpl = json.loads(rpc('getblocktemplate', '{"rules":[]}'))
    height = tpl['height']
    value = tpl['coinbasevalue']
    bits = int(tpl['bits'], 16)
    target = (bits & 0x007fffff) << (8 * ((bits >> 24) - 3))
    tx = coinbase(height, value, p2pkh_script(address))
    merkle = dsha(tx)
    version = tpl['version']
    prev = bytes.fromhex(tpl['previousblockhash'])[::-1]
    ntime = max(int(time.time()), tpl['mintime'], tpl['curtime'])
    prefix = struct.pack('<I', version) + prev + merkle + struct.pack('<II', ntime, bits)
    started = time.time()
    for nonce in range(0x100000000):
        header = prefix + struct.pack('<I', nonce)
        pow_raw = hashlib.scrypt(header, salt=header, n=1024, r=1, p=1, dklen=32)
        if int.from_bytes(pow_raw, 'little') <= target:
            block = header + varint(1) + tx
            response = rpc('submitblock', block.hex())
            if response not in ('', 'null'):
                raise RuntimeError('submitblock returned: ' + response)
            result = {
                'height': height, 'address': address, 'nonce': nonce,
                'bits': tpl['bits'], 'target': tpl['target'],
                'block_hash': dsha(header)[::-1].hex(),
                'pow_hash': pow_raw[::-1].hex(),
                'elapsed_seconds': round(time.time() - started, 3),
            }
            print(json.dumps(result, indent=2))
            return result
    raise RuntimeError('nonce space exhausted')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--address', required=True)
    parser.add_argument('--record', default='/root/.shushucoin/bootstrap-block-record.json')
    args = parser.parse_args()
    record = mine(args.address)
    Path(args.record).write_text(json.dumps(record, indent=2) + '\n')
