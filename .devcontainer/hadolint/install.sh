#!/bin/bash

set -euxo pipefail

wget https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64
wget https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64.sha256

sha256sum --ignore-missing -c hadolint-Linux-x86_64.sha256

install hadolint-Linux-x86_64 /usr/local/bin/hadolint
