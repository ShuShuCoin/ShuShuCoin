#!/usr/bin/env python3
"""Generate and mine the ShuShuCoin mainnet genesis block (Scrypt N=1024,r=1,p=1)."""
import hashlib, struct
from datetime import datetime, timezone

MESSAGE = '鼠鼠我啊，开挖！'.encode('utf-8')
TIME = int(datetime(2026, 9, 9, 6, 0, 0, tzinfo=timezone.utc).timestamp())
NBITS = 0x1F0FFFFF
VERSION = 1
GENESIS_REWARD = 0
PUBKEY = bytes.fromhex('040184710fa689ad5023690c80f3a49c8f13f8d45b8c857fbcbc8bc4a8e4d3eb4b10f4d4604fa08dce601aaf0f470216fe1b51850b4acf21b179c45070ac7b03a9')

def dsha(b): return hashlib.sha256(hashlib.sha256(b).digest()).digest()
def vi(n):
    if n < 0xfd: return bytes([n])
    if n <= 0xffff: return b'\xfd' + struct.pack('<H', n)
    return b'\xfe' + struct.pack('<I', n)
def target(bits):
    exponent = bits >> 24; mantissa = bits & 0x007fffff
    return mantissa << (8 * (exponent - 3))

script_sig = b'\x04' + struct.pack('<I', 486604799) + b'\x01\x04' + vi(len(MESSAGE)) + MESSAGE
script_pubkey = bytes([len(PUBKEY)]) + PUBKEY + b'\xac'
tx = (struct.pack('<I', 1) + b'\x01' + b'\x00' * 32 + struct.pack('<I', 0xffffffff) + vi(len(script_sig)) + script_sig + struct.pack('<I', 0xffffffff) + b'\x01' + struct.pack('<Q', GENESIS_REWARD) + vi(len(script_pubkey)) + script_pubkey + struct.pack('<I', 0))
merkle = dsha(tx)
limit = target(NBITS)
for nonce in range(0xffffffff + 1):
    header = struct.pack('<I', VERSION) + b'\x00' * 32 + merkle + struct.pack('<III', TIME, NBITS, nonce)
    pow_hash = hashlib.scrypt(header, salt=header, n=1024, r=1, p=1, dklen=32)
    if int.from_bytes(pow_hash, 'little') <= limit:
        print(f'timestamp={TIME}')
        print(f'nonce={nonce}')
        print(f'nBits=0x{NBITS:08x}')
        print(f'block_hash=0x{dsha(header)[::-1].hex()}')
        print(f'pow_hash=0x{pow_hash[::-1].hex()}')
        print(f'merkle=0x{merkle[::-1].hex()}')
        print(f'tx={tx.hex()}')
        break
