# Run a ShuShuCoin Mainnet Node

ShuShuCoin runs on mainnet by default. Do not pass `-testnet` or `-regtest` when operating a public mainnet node.

## Network values

| Setting | Value |
|---|---|
| P2P port | `31177/TCP` |
| RPC port | `31176/TCP`, local only |
| Bootstrap peer | `106.13.140.227:31177` |
| Windows data directory | `%APPDATA%\ShuShuCoin` |
| Linux data directory | `~/.shushucoin` |

Open inbound TCP port `31177` in the host firewall and any cloud security group if you want to accept public peers. Keep RPC port `31176` private and bound to localhost.

## Windows node bundle

1. Download and extract `ShuShuCoin-Node-v0.1.0-mainnet-win64.zip`.
2. Open the `ShuShuCoin-Node` directory.
3. Review `shushucoin.conf`; it already has the mainnet bootstrap peer and local-only RPC settings.
4. Run `Start-Node.bat`. Keep its console window open while the node runs.
5. In a second PowerShell window in that same directory, check status:

```powershell
.\shushucoin-cli.exe -datadir="$PSScriptRoot\data" -conf="$PSScriptRoot\shushucoin.conf" getblockchaininfo
.\shushucoin-cli.exe -datadir="$PSScriptRoot\data" -conf="$PSScriptRoot\shushucoin.conf" getnetworkinfo
```

6. Stop the node with `Stop-Node.bat`, or run:

```powershell
.\shushucoin-cli.exe -datadir="$PSScriptRoot\data" -conf="$PSScriptRoot\shushucoin.conf" stop
```

The bundle contains the daemon, CLI, transaction tool, configuration file, and every required runtime DLL. It runs without a separate compilation step.

## Linux node from source

Install build dependencies on Debian or Ubuntu:

```bash
sudo apt update
sudo apt install -y build-essential libtool autotools-dev automake pkg-config python3 \
  libevent-dev libboost-system-dev libboost-filesystem-dev libboost-program-options-dev \
  libboost-thread-dev libzmq3-dev
```

Build a daemon-only node:

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

Start, inspect, and stop the node:

```bash
./src/shushucoind -daemon
./src/shushucoin-cli getblockchaininfo
./src/shushucoin-cli getnetworkinfo
./src/shushucoin-cli stop
```

## Operational notes

- A node-only machine does not need a wallet. Do not copy wallet data onto it unless that machine is deliberately used to hold private keys.
- Verify the release SHA-256, Genesis hash, and source before use.
- Monitor disk usage, peer count, block height, and `debug.log`.
- Stop the daemon before an upgrade, replace the binaries, then start it again.
- Never expose RPC cookies, RPC credentials, wallet files, private keys, or mining-pool tokens.
