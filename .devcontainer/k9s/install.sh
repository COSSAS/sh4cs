#!/bin/bash

set -euxo pipefail

wget https://github.com/derailed/k9s/releases/download/v0.40.4/k9s_Linux_amd64.tar.gz
wget https://github.com/derailed/k9s/releases/download/v0.40.4/checksums.sha256

sha256sum -c --ignore-missing checksums.sha256

tar -xzvf k9s_Linux_amd64.tar.gz k9s
install k9s /usr/local/bin/k9s
