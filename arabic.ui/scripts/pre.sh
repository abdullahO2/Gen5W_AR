#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
LOG="/data/nemesis/arabic.ui.log"

log() {
    echo "$1"
    mkdir -p /data/nemesis 2>/dev/null || true
    echo "$1" >> "$LOG" 2>/dev/null || true
}

log "=========================================================="
log "[AR] تفعيل تعريب البروفايل (الوضع الآمن - عام لسيارات Gen5W)"
log "[EN] Activating Arabic Profile UI (Safe Mode - Universal Gen5W)"
log ""
log "[AR] إخلاء مسؤولية: استخدامك للحزمة يتم على مسؤوليتك الشخصية."
log "[EN] DISCLAIMER: Use at your own risk. Author holds no liability."
log ""
log "[AR] التعديل في بيانات المستخدم فقط، ولا يمس نظام /system أو ملف build.prop."
log "[EN] Modifies user profile data only. ZERO /system or build.prop changes."
log "=========================================================="
exit 0
