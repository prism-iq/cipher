#!/bin/bash
# Cipher Activation - Part of Pantheon

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export CIPHER_ROOT="$SCRIPT_DIR"

case "${1:-cli}" in
    cli)
        python3 "$SCRIPT_DIR/cli.py" "${@:2}"
        ;;
    daemon)
        python3 "$SCRIPT_DIR/cli.py" --daemon &
        echo "[+] Cipher daemon started (PID: $!)"
        ;;
    stop)
        pkill -f "cipher.*cli.py"
        echo "[*] Cipher stopped"
        ;;
    status)
        pgrep -f "cli.py" && echo "[+] Cipher running" || echo "[-] Cipher not running"
        ;;
    *)
        echo "Usage: $0 {cli|daemon|stop|status}"
        ;;
esac
