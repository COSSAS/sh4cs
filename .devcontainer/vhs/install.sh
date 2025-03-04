#!/bin/bash

set -euxo pipefail

wget https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64
wget https://github.com/tsl0922/ttyd/releases/download/1.7.7/SHA256SUMS

sha256sum --ignore-missing -c SHA256SUMS

install ttyd.x86_64 /usr/local/bin/ttyd

wget https://github.com/charmbracelet/vhs/releases/download/v0.9.0/vhs_0.9.0_amd64.deb
wget https://github.com/charmbracelet/vhs/releases/download/v0.9.0/checksums.txt

sha256sum --ignore-missing -c checksums.txt

apt-get update

apt-get install -y ffmpeg chromium ./vhs_0.9.0_amd64.deb tmux
