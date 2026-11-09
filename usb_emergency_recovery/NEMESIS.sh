#!/system/bin/sh
# Universal Failsafe Emergency Recovery Script for Gen5W (Pure toolbox compatible)
# Dynamically searches for that vehicle's own backup on USB or internal storage,
# and guarantees a permanent internal backup is always preserved inside the head unit.
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
export LD_LIBRARY_PATH=/vendor/lib:/system/lib

BP=/system/build.prop
GLOBAL_STOCK=/data/nemesis/build.prop.stock
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

find_backup_source() {
    # 1. Check relative OEM_BACKUP on current USB drive
    if [ -s "./OEM_BACKUP/build.prop.stock" ] && verify_prop_file "./OEM_BACKUP/build.prop.stock"; then
        echo "./OEM_BACKUP/build.prop.stock"
        return 0
    fi
    if [ -s "./build.prop" ] && verify_prop_file "./build.prop"; then
        echo "./build.prop"
        return 0
    fi

    # 2. Check all mounted USB locations for this vehicle's OEM_BACKUP
    for _u in /storage/usb0 /storage/usb1 /storage/usb2 /mnt/media_rw/usb* /storage/usbotg*; do
        if [ -s "$_u/OEM_BACKUP/build.prop.stock" ] && verify_prop_file "$_u/OEM_BACKUP/build.prop.stock"; then
            echo "$_u/OEM_BACKUP/build.prop.stock"
            return 0
        fi
        if [ -s "$_u/build.prop" ] && verify_prop_file "$_u/build.prop"; then
            echo "$_u/build.prop"
            return 0
        fi
    done

    # 3. Check internal global stock backup on the car (/data/nemesis/build.prop.stock)
    if [ -s "$GLOBAL_STOCK" ] && verify_prop_file "$GLOBAL_STOCK"; then
        echo "$GLOBAL_STOCK"
        return 0
    fi

    # 4. Check internal package backup on the car
    for _p in /data/nemesis/backup/*/build.prop.stock; do
        if [ -s "$_p" ] && verify_prop_file "$_p"; then
            echo "$_p"
            return 0
        fi
    done

    return 1
}

log "=========================================================="
log "[AR] بدء تشغيل الاسترجاع التلقائي للطوارئ"
log "[EN] Universal Emergency OEM Restore Triggered"
log "=========================================================="
toast "طوارئ: جاري استرجاع نسخة المصنع...
Emergency: Restoring OEM Backup..."

SOURCE="$(find_backup_source)"

if [ -z "$SOURCE" ] || ! verify_prop_file "$SOURCE"; then
    log "[AR] خطأ حرج: لم يتم العثور على نسخة احتياطية صالحة لهذا الجهاز!"
    log "[EN] CRITICAL: No valid OEM backup file found for this vehicle on USB or internal storage!"
    toast "خطأ: لم يتم العثور على نسخة احتياطية!
Error: No OEM Backup Found!"
    exit 1
fi

log "[AR] تم تحديد مسار نسخة المصنع:"
log "[EN] Identified valid OEM vehicle backup: $SOURCE"

if ! sys_rw; then
    log "[AR] خطأ: تعذر فتح نظام الملفات للكتابة"
    log "[EN] FAIL: cannot remount /system rw"
    toast "خطأ: تعذر فتح النظام!
Cannot remount /system rw"
    exit 1
fi

cp -f "$SOURCE" "$BP" || {
    sys_ro
    log "[AR] خطأ: فشل نسخ الملف إلى مسار النظام"
    log "[EN] FAIL: cp failed"
    toast "خطأ: فشل نسخ الملف!
File copy failed!"
    exit 1
}

chmod 644 "$BP" 2>/dev/null || true
chown 0.0 "$BP" 2>/dev/null || chown 0:0 "$BP" 2>/dev/null || true

# GUARANTEE DUAL BACKUP: Save/preserve internal backup inside the head unit's internal storage
mkdir -p /data/nemesis 2>/dev/null || true
if [ ! -s "$GLOBAL_STOCK" ] || ! verify_prop_file "$GLOBAL_STOCK"; then
    cp -f "$SOURCE" "$GLOBAL_STOCK" 2>/dev/null || true
    log "[AR] تم حفظ نسخة احتياطية إضافية داخل ذاكرة الوحدة: $GLOBAL_STOCK"
    log "[EN] Saved permanent internal backup inside head unit storage: $GLOBAL_STOCK"
fi

# Clear persist locale and timezone overrides
rm -f /data/property/persist.sys.language_list 2>/dev/null || true
rm -f /data/property/persist.sys.language 2>/dev/null || true
rm -f /data/property/persist.sys.country 2>/dev/null || true
rm -f /data/property/persist.sys.timezone 2>/dev/null || true

# Restore profile language defaults
settings put system language_type_dr1 en_US 2>/dev/null || true
settings put system language_type_dr2 Unknown 2>/dev/null || true
settings put system language_type Unknown 2>/dev/null || true

sys_ro
sync
log "=========================================================="
log "[AR] اكتمل استرجاع نسخة المصنع بنجاح. جاري إعادة التشغيل..."
log "[EN] OEM RESTORE COMPLETED SUCCESSFULLY. REBOOTING..."
log "=========================================================="
toast "تم استرجاع الوكالة بنجاح! جاري الإقلاع
OEM Restored! Rebooting in 3s..."

sleep 3
/system/bin/reboot 2>/dev/null || reboot 2>/dev/null || true
exit 0
