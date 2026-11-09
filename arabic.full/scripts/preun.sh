#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
. ./scripts/common.sh

log "=== [AR] بدء إزالة تهيئة خرائط الشرق الأوسط والتعريب ==="
log "=== [EN] Uninstalling arabic.full ==="

_err=0
restore_build_prop || _err=1
restore_profile_language || _err=1

if [ "$_err" -ne 0 ]; then
    log "[AR] فشل الاسترجاع الكامل! تم الاحتفاظ بالنسخ الاحتياطية للأمان."
    log "[EN] ABORT: Restore failed. Keeping backup for safety."
    toast "فشل الاسترجاع! راجع السجل
Restore failed! Check log"
    exit 1
fi

rm -rf "$BACKUP_DIR" 2>/dev/null || true
sync

# Re-enable installer on USB if USB is still plugged in
rename_usb_data "NEMESIS.data.installed" "NEMESIS.data"

log "=== [AR] تم استرجاع نسخة المصنع وإزالة الحزمة بنجاح ==="
log "=== [EN] arabic.full uninstalled successfully ==="
toast "تم استرجاع وضع المصنع الافتراضي!
OEM Restored! Rebooting..."

# Spawns detached reboot subshell and exits 0 immediately so NEMESIS removes package cleanly
reboot_system
exit 0
