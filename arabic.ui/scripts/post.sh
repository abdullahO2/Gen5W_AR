#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
. ./scripts/common.sh

log "=== [AR] بدء تثبيت تعريب البروفايل ==="
log "=== [EN] Installing arabic.ui ==="

# 1. Universal OEM backup to USB & local storage
backup_vehicle_oem

# 2. Apply Arabic settings to Driver Profile and persist properties (No /system write!)
if ! apply_profile_arabic; then
    log "[AR] خطأ: فشل تفعيل لغة البروفايل"
    log "[EN] ERROR: apply_profile_arabic failed."
    restore_profile_language
    toast "خطأ في التفعيل! تم الإلغاء
Error! Installation Aborted"
    exit 1
fi

sync
log "=== [AR] اكتمل التفعيل بنجاح (دون لمس ملفات النظام) ==="
log "=== [EN] Completed successfully (Zero /system changes) ==="

# 3. Rename USB installer descriptor to prevent re-install prompts on future boots
rename_usb_data "NEMESIS.data" "NEMESIS.data.installed"

# 4. Notify user on screen with bilingual toast and trigger detached reboot
toast "تم تفعيل التعريب! جاري إعادة التشغيل...
Arabic Activated! Rebooting in 4s..."
reboot_system
exit 0
