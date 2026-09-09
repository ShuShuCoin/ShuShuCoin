# ShuShuCoin Chain Specification v0.1

## Identity

| Field | Value |
|---|---|
| Chinese name | 鼠鼠 |
| English name | ShuShuCoin |
| Ticker | SHUSHU |
| Internal code name | `shushucoin` |
| Atomic unit | `shu` |
| Decimal places | 8 |
| Logo | `assets/logo/shushucoin-logo.png` |

## Consensus and issuance

| Field | Value |
|---|---|
| Source baseline | Dogecoin Core `v1.14.9` |
| Ledger | UTXO |
| Proof of work | Scrypt (`N=1024`, `r=1`, `p=1`) |
| Target spacing | 60 seconds |
| Difficulty | Digishield, every block |
| Mining | Direct Scrypt and AuxPoW merged mining |
| Coinbase maturity | 60 blocks |
| Premine / team tax | 0 / 0% |
| Supply | No hard cap |

| Block height | SHUSHU subsidy |
|---|---:|
| 1–99,999 | 1,000,000 |
| 100,000–199,999 | 500,000 |
| 200,000–299,999 | 250,000 |
| 300,000–399,999 | 125,000 |
| 400,000–499,999 | 62,500 |
| 500,000–599,999 | 31,250 |
| 600,000 onward | 10,000 permanently |

## Mainnet identity

- P2P/RPC ports: `31177` / `31176`
- AuxPoW chain ID: `0x5355`
- Data directory: `%APPDATA%\\ShuShuCoin` (Windows), `~/.shushucoin` (Linux)
- Mainnet seeds: deliberately empty until public infrastructure is published.

## Verified genesis block

| Parameter | Value |
|---|---|
| Message | `鼠鼠我啊，开挖！` |
| Time | `1788933600` (`2026-09-09 06:00:00 UTC`) |
| Version | `1` |
| nBits | `0x1f0fffff` |
| Nonce | `5386` |
| Reward | `0 SHUSHU` |
| Block hash | `6ed642616b1d4f1fddb96bb72a8bca15ac9c24a4ffd4e6e5eb063193c2460a6d` |
| Merkle root | `085d05e3efb99ec83ee23622b569aed31349e900e75a348c7d915ad9419a7cdb` |
| Scrypt PoW hash | `000c89a32f7990dcd0225da10cb1997e80312530ca2f84b511b1ad38ffac8e27` |

The block-hash placeholder above is replaced by the startup-verified value recorded in `docs/verification/server-build-20260909.md`.
## First mined mainnet block

Block 1 was accepted at 2026-09-09 09:06:51 UTC with hash 7c87255bd09be09338bccf8c55788ba34b09f5d6bbeaf7a795855a72539c55c9 and a 1,000,000 SHUSHU subsidy. See docs/verification/block-1-20260909.md.
