#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
. ./scripts/common.sh

log "=== [AR] بدء إزالة حزمة التعريب ==="
log "=== [EN] Uninstalling arabic.ui ==="

restore_profile_language
rm -rf "$BACKUP_DIR" 2>/dev/null || true
sync

# Re-enable installer on USB if USB is still plugged in
rename_usb_data "NEMESIS.data.installed" "NEMESIS.data"

log "=== [AR] تمت الإزالة واسترجاع الإعدادات بنجاح ==="
log "=== [EN] arabic.ui uninstalled successfully ==="
toast "تمت الإزالة والعودة للوضع الافتراضي
Restored to default! Rebooting..."

# Spawns detached reboot subshell and exits 0 immediately so NEMESIS removes package cleanly
reboot_system
exit 0
