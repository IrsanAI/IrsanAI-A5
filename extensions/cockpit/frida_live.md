# Frida Live für a5crackme2 (Termux)

Termux (non-root):
pkg install frida
pip install frida-tools
frida --version

Test target native (kein Android nötig):
frida -f ~/a5_targets/a5_crackme_v2 -l providers/frida_a5crackme2.js -- A5-Pro-Cockpit-2026!

Wenn das geht, schreibt Provider observed Evidence.

Im Cockpit siehst du dann A3 FRIDA live grün.
