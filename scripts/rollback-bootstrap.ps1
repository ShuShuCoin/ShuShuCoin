param([switch]$WhatIf)
$ErrorActionPreference = 'Stop'
$core = Split-Path -Parent $PSScriptRoot
$tracked = @(
  'Makefile.am', 'README.md', 'build-aux/m4/ax_boost_base.m4', 'configure.ac',
  'src/Makefile.am', 'src/Makefile.qt.include', 'src/Makefile.qttest.include',
  'src/amount.cpp', 'src/bitcoin-cli-res.rc', 'src/bitcoin-cli.cpp', 'src/bitcoin-tx-res.rc',
  'src/bitcoind-res.rc', 'src/bitcoind.cpp', 'src/chainparams.cpp', 'src/chainparamsbase.cpp',
  'src/clientversion.cpp', 'src/init.cpp', 'src/qt/bitcoin.cpp', 'src/qt/res/bitcoin-qt-res.rc',
  'src/secp256k1/Makefile.am', 'src/univalue/Makefile.am', 'src/util.cpp', 'src/util.h'
)
$added = @(
  'contrib/genesis', 'contrib/mining', 'docs/upstream-baseline.md', 'docs/shushucoin-chain-spec.md',
  'docs/verification/branding-baseline.sha256', 'docs/verification/bootstrap-modified.sha256',
  'scripts/rollback-bootstrap.ps1', 'share/pixmaps/shushucoin.png'
)
if ($WhatIf) { $tracked | ForEach-Object { "RESTORE  $_" }; $added | ForEach-Object { "REMOVE   $_" }; exit 0 }
git -C $core restore --source upstream/dogecoin-core-v1.14.9 -- $tracked
foreach ($relative in $added) { $path = Join-Path $core $relative; if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Recurse -Force } }
Write-Output 'Rollback complete: core source restored to upstream/dogecoin-core-v1.14.9 for recorded ShuShuCoin files.'