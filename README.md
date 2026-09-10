# ShuShuCoin Core [SHUSHU]

<p align="center"><img src="share/pixmaps/shushucoin.png" alt="ShuShuCoin logo" width="220"></p>

> 鼠鼠我啊，开挖！ / Let the mice mine.

**鼠鼠（ShuShuCoin，`SHUSHU`）** 是一条独立主网区块链，基于 Dogecoin Core `v1.14.9` 开发。它使用 UTXO 账本、Scrypt 工作量证明和 60 秒目标出块时间，支持原生 Scrypt 挖矿与 AuxPoW 合并挖矿。

**ShuShuCoin (`SHUSHU`)** is an independent mainnet blockchain derived from Dogecoin Core `v1.14.9`. It uses a UTXO ledger, Scrypt proof of work, a 60-second target block interval, native Scrypt mining, and AuxPoW merged mining.

## Mainnet parameters / 主网参数

| Item | Value |
|---|---|
| Ticker | `SHUSHU` |
| Proof of work | Scrypt (`N=1024`, `r=1`, `p=1`) |
| Block target | 60 seconds |
| Difficulty | Digishield, every block |
| Mining | Native Scrypt + AuxPoW |
| Coinbase maturity | 60 blocks |
| Premine / team tax | 0 / 0% |
| Supply | No hard cap |
| P2P / RPC ports | `31177` / `31176` |
| AuxPoW chain ID | `0x5355` |
| Bootstrap peer | `106.13.140.227:31177` |

## Issuance / 发行规则

| Height | Subsidy (SHUSHU) |
|---|---:|
| 1–99,999 | 1,000,000 |
| 100,000–199,999 | 500,000 |
| 200,000–299,999 | 250,000 |
| 300,000–399,999 | 125,000 |
| 400,000–499,999 | 62,500 |
| 500,000–599,999 | 31,250 |
| 600,000 onward | 10,000 permanently |

## Genesis / 创世区块

- Message: `鼠鼠我啊，开挖！`
- Genesis hash: `6ed642616b1d4f1fddb96bb72a8bca15ac9c24a4ffd4e6e5eb063193c2460a6d`
- Genesis Scrypt PoW hash: `000c89a32f7990dcd0225da10cb1997e80312530ca2f84b511b1ad38ffac8e27`

## Downloads / 下载

The current Windows Qt wallet and node-tool release is available from [GitHub Releases](https://github.com/ShuShuCoin/ShuShuCoin/releases/latest).

Windows Qt wallet: extract `ShuShuCoin-Qt-v0.1.0-mainnet-win64.zip`, run `ShuShuCoin-Qt/shushucoin-qt.exe`, create a receiving address with **Much Receive**, then back up through **File → Backup Wallet…**.

Before use, verify the published SHA-256 checksum. A `wallet.dat` file contains private keys: keep it offline and never publish it, share it, or commit it to a repository.

## Mine locally / 本机挖矿

Use a receiving address created by the Qt wallet:

```powershell
cd E:\ShuShuCoin
py -3 .\tools\shushu_cpu_miner.py --host 106.13.140.227 --address YOUR_SHUSHU_ADDRESS --probe
py -3 .\tools\shushu_cpu_miner.py --host 106.13.140.227 --address YOUR_SHUSHU_ADDRESS
```

Rewards are paid to the specified address and become spendable after 60 confirmations.

## Run a node / 运行节点

A node-tool ZIP is provided in the GitHub Release. It contains `shushucoind`, `shushucoin-cli`, a configuration template, and Windows start/stop scripts. See the full guide: [docs/run-a-node.md](docs/run-a-node.md).

For a public node, open **TCP port 31177** for P2P traffic. Keep RPC port `31176` private: bind it to localhost and do not expose its cookie or credentials.

## Source and license / 源码与许可

- Full chain specification: [docs/shushucoin-chain-spec.md](docs/shushucoin-chain-spec.md)
- Node guide: [docs/run-a-node.md](docs/run-a-node.md)
- Upstream: [Dogecoin Core](https://github.com/dogecoin/dogecoin), `v1.14.9`
- License: MIT. Preserve the upstream `COPYING` file and copyright notices.

This is an early mainnet release. Verify source code, binary checksums, and consensus parameters independently before use.
