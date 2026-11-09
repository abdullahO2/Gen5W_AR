#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
. ./scripts/common.sh

log "=== [AR] بدء تثبيت تهيئة خرائط الشرق الأوسط والتعريب ==="
log "=== [EN] Installing arabic.full (ME Map Compatibility) ==="

# 1. Dual OEM backup: to USB (OEM_BACKUP folder) AND internal head unit storage
if ! backup_vehicle_oem; then
    log "[AR] خطأ: فشل النسخ الاحتياطي! تم إلغاء العملية."
    log "[EN] ABORT: Per-vehicle OEM backup failed! System untouched."
    toast "فشل النسخ الاحتياطي! تم الإلغاء
Backup Failed! Aborted"
    exit 1
fi

# 2. Remount system partition rw
if ! sys_rw; then
    log "[AR] خطأ: تعذر فتح نظام الملفات للكتابة"
    log "[EN] ABORT: Cannot remount /system rw"
    toast "فشل فتح نظام الملفات!
Cannot remount /system rw"
    exit 1
fi

# 3. Apply properties to build.prop
_fail=0

# A) Set Middle East region for Native Navigation Engine (BuildInfo.REGION = 6)
set_prop_line "$BP" ro.product.locale.region ME || _fail=1

# B) Universal language list: preserves vehicle native languages + adds ar_EG
_langs="$(get_universal_language_list)"
set_prop_line "$BP" persist.sys.language_list "$_langs" || _fail=1

if [ "$_fail" -ne 0 ]; then
    log "[AR] خطأ أثناء تعديل الخصائص. جاري استرجاع نسخة المصنع..."
    log "[EN] ERROR occurred during build.prop updates. Rolling back..."
    restore_build_prop
    sys_ro
    toast "خطأ في التثبيت! تم استرجاع الوكالة
Error! Restored OEM"
    exit 1
fi

# 4. Lock system filesystem
sys_ro
sync

# 5. Apply Driver Profile settings
apply_profile_arabic

log "=== [AR] اكتمل التثبيت والتهيئة بنجاح ==="
log "=== [EN] Full installation completed successfully ==="

# 6. Rename USB installer descriptor to prevent re-install prompts on future boots
rename_usb_data "NEMESIS.data" "NEMESIS.data.installed"

# 7. Notify user on screen and trigger detached reboot
toast "تم تفعيل توافق خرائط الشرق الأوسط!
ME Map Compatibility Enabled! Rebooting..."
reboot_system
exit 0
