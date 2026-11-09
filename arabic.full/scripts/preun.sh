#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
. ./scripts/common.sh

log "=== Uninstalling arabic.full package ==="

if ! restore_all; then
    log "ABORT: Restore failed. Keeping backup for safety."
    toast "Arabic Mod: Restore failed! Check log."
    exit 1
fi

rm -rf "$BACKUP_DIR" 2>/dev/null || true
sync

# Re-enable installer on USB if USB is still plugged in
rename_usb_data "NEMESIS.data.installed" "NEMESIS.data"

log "=== arabic.full uninstalled successfully ==="
toast "Arabic Full: Restored to stock OEM! Rebooting in 3 seconds..."
reboot_system
exit 0
