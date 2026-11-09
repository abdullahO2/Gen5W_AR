#!/system/bin/sh
# Failsafe Emergency Recovery Script for Gen5W (Pure toolbox compatible)
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
export LD_LIBRARY_PATH=/vendor/lib:/system/lib

BP=/system/build.prop
GLOBAL_STOCK=/data/nemesis/build.prop.stock
BACKUP_UI=/data/nemesis/backup/arabic.ui/build.prop.stock
BACKUP_FULL=/data/nemesis/backup/arabic.full/build.prop.stock
USB_BACKUP=./build.prop
LOG=./emergency-recover.log

log() {
    echo "$1"
    mkdir -p /data/nemesis 2>/dev/null || true
    echo "$1" >> "$LOG" 2>/dev/null || true
}

toast() {
    local _msg="$1"
    am broadcast -a com.hkmc.intent.action.TOAST \
        -e com.hkmc.intent.extra.TOAST_MESSAGE "$_msg" \
        --ez com.hkmc.intent.extra.TOAST_POPUPSHOWING true >/dev/null 2>&1 || true
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

verify_prop_file() {
    local _f="$1"
    if [ ! -f "$_f" ] || [ ! -s "$_f" ]; then
        return 1
    fi
    if ! grep "ro.build." "$_f" >/dev/null 2>&1; then
        return 1
    fi
    return 0
}

log "=== EMERGENCY RESTORATION TRIGGERED ==="
toast "NEMESIS: Emergency Recovery Triggered..."

SOURCE=""
if [ -s "$USB_BACKUP" ] && verify_prop_file "$USB_BACKUP"; then
    SOURCE="$USB_BACKUP"
    log "Using USB backup: $SOURCE"
elif [ -s "$GLOBAL_STOCK" ] && verify_prop_file "$GLOBAL_STOCK"; then
    SOURCE="$GLOBAL_STOCK"
    log "Using permanent stock backup: $SOURCE"
elif [ -s "$BACKUP_UI" ] && verify_prop_file "$BACKUP_UI"; then
    SOURCE="$BACKUP_UI"
    log "Using UI package backup: $SOURCE"
elif [ -s "$BACKUP_FULL" ] && verify_prop_file "$BACKUP_FULL"; then
    SOURCE="$BACKUP_FULL"
    log "Using Full package backup: $SOURCE"
else
    log "CRITICAL: No valid factory backup file found!"
    toast "Recovery Error: No backup found!"
    exit 1
fi

if ! sys_rw; then
    log "FAIL: cannot remount /system rw"
    toast "Recovery Error: Cannot remount rw!"
    exit 1
fi

cp -f "$SOURCE" "$BP" || {
    sys_ro
    log "FAIL: cp failed"
    toast "Recovery Error: File copy failed!"
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
toast "Recovery: Stock restored! Rebooting in 3 seconds..."

sleep 2
/system/bin/reboot 2>/dev/null || reboot 2>/dev/null || true
exit 0
