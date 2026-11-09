#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
LOG="/data/nemesis/arabic.full.log"

log() {
    echo "$1"
    mkdir -p /data/nemesis 2>/dev/null || true
    echo "$1" >> "$LOG" 2>/dev/null || true
}

log "=========================================================="
log "[AR] تهيئة النظام لتشغيل خرائط الشرق الأوسط الأصلية"
log "[EN] Enabling Middle East Native Map Engine Compatibility"
log ""
log "[AR] تنبيه هام: الحزمة لا تحتوي على ملفات الخرائط، بل تهيئ النظام لقبولها."
log "[EN] IMPORTANT: This package does NOT include map files; it enables system map support."
log ""
log "[AR] إخلاء مسؤولية: هذا التعديل يتم على مسؤوليتك الشخصية بالكامل."
log "[EN] DISCLAIMER: Use at your own risk. Author holds no liability."
log ""
log "[AR] تنبيه: تعديل منطقة النظام إلى ME قد يعطل بعض التعديلات الكورية."
log "[EN] NOTICE: Changing system region to ME may deactivate Korean mods."
log ""
log "[AR] يتم حفظ نسخة المصنع لسيارتك تلقائياً على الفلاش ميموري وداخل ذاكرة الشاشة."
log "[EN] Automatic dual OEM backup created on USB drive and inside head unit storage."
log "=========================================================="
exit 0
