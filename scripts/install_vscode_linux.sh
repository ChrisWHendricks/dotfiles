#!/usr/bin/env bash
# Install the official Microsoft build of Visual Studio Code on Debian,
# Ubuntu, Pop!_OS, and other apt-based Linux distributions.

set -euo pipefail

if command -v code >/dev/null 2>&1; then
    echo "Visual Studio Code is already installed"
    exit 0
fi

echo "Installing prerequisites..."
sudo apt-get update
sudo apt-get install -y wget gpg apt-transport-https

echo "Adding Microsoft's signing key..."
wget -qO- https://packages.microsoft.com/keys/microsoft.asc \
    | sudo gpg --dearmor --yes -o /usr/share/keyrings/microsoft.gpg

echo "Adding Microsoft's Visual Studio Code repository..."
sudo tee /etc/apt/sources.list.d/vscode.sources >/dev/null <<'EOF'
Types: deb
URIs: https://packages.microsoft.com/repos/code
Suites: stable
Components: main
Architectures: amd64 arm64 armhf
Signed-By: /usr/share/keyrings/microsoft.gpg
EOF

# Pop!_OS provides its own package named "code". Prefer Microsoft's official
# repository so installs and upgrades consistently use the official build.
sudo tee /etc/apt/preferences.d/code >/dev/null <<'EOF'
Package: code
Pin: origin "packages.microsoft.com"
Pin-Priority: 9999
EOF

echo "Installing Visual Studio Code..."
sudo apt-get update
sudo apt-get install -y code

echo "Visual Studio Code installed successfully"
