#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
LOG="/data/nemesis/arabic.locale.log"

log() {
    echo "$1"
    mkdir -p /data/nemesis 2>/dev/null || true
    echo "$1" >> "$LOG" 2>/dev/null || true
}

log "=========================================================="
log " DISCLAIMER / إخلاء مسؤولية "
log " This package modifies system properties at user risk. "
log " Author holds no liability for device failure or damage. "
log " Proceeding with installation of minimal Arabic & ME mod. "
log "=========================================================="
exit 0
