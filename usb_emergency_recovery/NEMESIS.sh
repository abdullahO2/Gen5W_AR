#!/system/bin/sh
# Failsafe Emergency Recovery Script for Gen5W (Pure toolbox compatible)
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
export LD_LIBRARY_PATH=/vendor/lib:/system/lib

BP=/system/build.prop
BACKUP1=/data/nemesis/backup/arabic.locale/build.prop.stock
BACKUP2=/data/nemesis/build.prop.stock
USB_BACKUP=./build.prop
LOG=./emergency-recover.log

log() {
    echo "$1"
    mkdir -p /data/nemesis 2>/dev/null || true
    echo "$1" >> "$LOG" 2>/dev/null || true
}

sys_rw() {
    /system/xbin/nemesis remount rw >/dev/null 2>&1 && return 0
    mount -o remount,rw /system 2>/dev/null && return 0
    mount -o rw,remount /system 2>/dev/null && return 0
    return 1
}

sys_ro() {
    /system/xbin/nemesis remount ro >/dev/null 2>&1 || true
    mount -o remount,ro /system 2>/dev/null || true
}

log "=== EMERGENCY RESTORATION TRIGGERED ==="

SOURCE=""
if [ -s "$USB_BACKUP" ]; then
    SOURCE="$USB_BACKUP"
    log "Using USB backup: $SOURCE"
elif [ -s "$BACKUP1" ]; then
    SOURCE="$BACKUP1"
    log "Using package backup: $SOURCE"
elif [ -s "$BACKUP2" ]; then
    SOURCE="$BACKUP2"
    log "Using global backup: $SOURCE"
else
    log "CRITICAL: No valid backup file found!"
    exit 1
fi

if ! sys_rw; then
    log "FAIL: cannot remount /system rw"
    exit 1
fi

cp -f "$SOURCE" "$BP" || {
    sys_ro
    log "FAIL: cp failed"
    exit 1
}

chmod 644 "$BP" 2>/dev/null || true
chown 0.0 "$BP" 2>/dev/null || chown 0:0 "$BP" 2>/dev/null || true

# Clear persist locale overrides
rm -f /data/property/persist.sys.language_list 2>/dev/null || true
rm -f /data/property/persist.sys.timezone 2>/dev/null || true

sys_ro
sync
log "=== EMERGENCY RESTORE COMPLETED SUCCESSFULLY. REBOOTING ==="
reboot
exit 0
