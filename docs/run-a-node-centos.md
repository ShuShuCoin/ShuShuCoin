# ShuShuCoin CentOS 8 x86_64 Node

This is a prebuilt ShuShuCoin mainnet node package for **CentOS 8 x86_64**. No source compilation is required.

## Install

```bash
tar -xzf ShuShuCoin-Node-v0.1.0-mainnet-centos8-x86_64.tar.gz
cd ShuShuCoin-Node-CentOS8-x86_64
sudo ./install-centos-node.sh
```

The installer installs runtime dependencies, creates the `shushucoin` system user, installs binaries under `/opt/shushucoin/bin`, writes configuration to `/etc/shushucoin/shushucoin.conf`, creates `/var/lib/shushucoin`, and starts `shushucoind.service`.

## Verify

```bash
sudo systemctl status shushucoind
sudo -u shushucoin /opt/shushucoin/bin/shushucoin-cli \
  -datadir=/var/lib/shushucoin -conf=/etc/shushucoin/shushucoin.conf getblockchaininfo
```

## Public P2P access

Open only the P2P port if you want to accept public peers:

```bash
sudo firewall-cmd --permanent --add-port=31177/tcp
sudo firewall-cmd --reload
```

RPC port `31176` stays bound to `127.0.0.1` and must not be exposed publicly.

## Service operations

```bash
sudo systemctl restart shushucoind
sudo systemctl stop shushucoind
sudo journalctl -u shushucoind -f
```

## Included files

- `bin/shushucoind` — mainnet daemon
- `bin/shushucoin-cli` — local node control client
- `bin/shushucoin-tx` — transaction utility
- `shushucoin.conf` — local-RPC mainnet configuration
- `systemd/shushucoind.service` — systemd service definition
- `install-centos-node.sh` — installer

Verify this archive against the SHA-256 value published in the GitHub Release before installation.
