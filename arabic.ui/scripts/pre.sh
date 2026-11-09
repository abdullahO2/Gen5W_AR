#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
LOG="/data/nemesis/arabic.ui.log"

log() {
    echo "$1"
    mkdir -p /data/nemesis 2>/dev/null || true
    echo "$1" >> "$LOG" 2>/dev/null || true
}

log "=========================================================="
log " DISCLAIMER / إخلاء مسؤولية "
log " Installing Arabic UI Language (Safe Profile Mode). "
log " This package modifies persist.sys.language_list only. "
log " System region and navigation engine remain untouched. "
log " Author holds no liability for device failure or damage. "
log "=========================================================="
exit 0
