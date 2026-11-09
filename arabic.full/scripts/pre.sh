#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
LOG="/data/nemesis/arabic.full.log"

log() {
    echo "$1"
    mkdir -p /data/nemesis 2>/dev/null || true
    echo "$1" >> "$LOG" 2>/dev/null || true
}

log "=========================================================="
log " DISCLAIMER / إخلاء مسؤولية "
log " Installing Arabic & Middle East Region (Full Mod). "
log " NOTICE: Modifies system region to ME for native map engine. "
log " May deactivate Korean-market specific features/mods. "
log " Author holds no liability for device failure or damage. "
log "=========================================================="
exit 0
