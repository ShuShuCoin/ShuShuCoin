# ShuShuCoin 节点运行指南 / Node operator guide

ShuShuCoin is mainnet by default. Do not pass `-testnet` or `-regtest` for a public mainnet node.

## Network settings / 网络参数

| Setting | Value |
|---|---|
| P2P port | `31177/TCP` |
| RPC port | `31176/TCP` (local only) |
| Bootstrap peer | `106.13.140.227:31177` |
| Default data directory | Windows: `%APPDATA%\ShuShuCoin`; Linux: `~/.shushucoin` |

A public node needs inbound TCP `31177` allowed by the host firewall and, when applicable, the router/security group. Keep RPC `31176` bound to loopback; it is not a public service.

## Windows node bundle

1. Download and extract `ShuShuCoin-Node-v0.1.0-mainnet-win64.zip` from the GitHub Release.
2. Edit `shushucoin.conf` in the extracted `ShuShuCoin-Node` directory if you need a different data directory or connection limit.
3. Double-click `启动节点.bat`. The console stays open while the node runs.
4. Open a second PowerShell in the same directory and check the node:

```powershell
.\shushucoin-cli.exe -datadir="$PSScriptRoot\data" getblockchaininfo
.\shushucoin-cli.exe -datadir="$PSScriptRoot\data" getnetworkinfo
```

5. Stop gracefully:

```powershell
.\shushucoin-cli.exe -datadir="$PSScriptRoot\data" stop
```

The bundled configuration connects to the current bootstrap node and listens on P2P port `31177`. Do not copy wallet data into a public node directory unless that machine is intended to hold private keys.

## Linux node from source

On Debian/Ubuntu, install the build dependencies:

```bash
sudo apt update
sudo apt install -y build-essential libtool autotools-dev automake pkg-config python3 \
  libevent-dev libboost-system-dev libboost-filesystem-dev libboost-program-options-dev \
  libboost-thread-dev libzmq3-dev
```

Build the daemon without a GUI or wallet:

```bash
git clone https://github.com/ShuShuCoin/ShuShuCoin.git
cd ShuShuCoin
./autogen.sh
./configure --without-gui --disable-wallet --disable-tests --disable-bench
make -j"$(nproc)"
```

Create `~/.shushucoin/shushucoin.conf`:

```ini
server=1
listen=1
port=31177
rpcport=31176
rpcbind=127.0.0.1
rpcallowip=127.0.0.1
addnode=106.13.140.227:31177
dnsseed=0
maxconnections=64
```

Start and check it:

```bash
./src/shushucoind -daemon
./src/shushucoin-cli getblockchaininfo
./src/shushucoin-cli getnetworkinfo
```

Stop it cleanly:

```bash
./src/shushucoin-cli stop
```

## Operations / 运维建议

- Back up `wallet.dat` only on machines used as wallets; a non-wallet node does not need wallet keys.
- Monitor disk usage, peer count, block height, and the debug log.
- Upgrade by stopping the daemon first, replacing binaries, then starting it again.
- Verify the Genesis hash and release SHA-256 before joining the network.
- Do not expose RPC credentials, cookie files, `wallet.dat`, private keys, or mining-pool tokens.
