#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
echo "[A5 Pro Installer] Termux-First"
pkg update -y || true
pkg install -y python frida-tools sqlite termux-tools 2>/dev/null || pkg install -y python
pip install --upgrade pip
pip install frida frida-tools 2>/dev/null || echo "[!] pip frida optional"
mkdir -p ~/a5_evidence
echo "[+] frida: $(python3 -c 'import frida; print(frida.__version__)' 2>&1 || echo 'not installed yet, stub mode ok')"
echo "[+] done – A5 ready, keine Binaries im Repo, alles zur Laufzeit"
