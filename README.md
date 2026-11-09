# NEMESIS Arabic & Middle East Localization Mod (Gen5W)
### حزمة تفعيل اللغة العربية وضبط توافق الشرق الأوسط لشاشات هيونداي وكيا وجينيسيس (Gen5W)

[![Platform](https://img.shields.io/badge/Platform-Gen5W%20(Android%204.4.2)-blue.svg)](#)
[![Compatibility](https://img.shields.io/badge/Framework-NEMESIS%20v1.1+-green.svg)](#)
[![License: Unlicense](https://img.shields.io/badge/License-Unlicense%20(Public%20Domain)-lightgrey.svg)](LICENSE)

---

## 📖 English Overview

This repository provides an official, clean, and completely reversible **NEMESIS package** (`arabic.locale`) designed to enable **Arabic language support** and **Middle East regional compatibility** on **Hyundai, Kia, and Genesis Gen5W** head units.

The package adheres to the **Minimal Safe Modifications** principle: it applies only the essential properties needed for daily use without altering or corrupting core system files.

### Key Features
- **Native Arabic Selection:** Unlocks the Arabic language option (`ar_EG`) in the standard system settings (`Settings ➡️ General ➡️ Language`).
- **Middle East Regional Profile:** Configures `ro.product.locale.region=ME` (`BuildInfo.REGION = 6`) to enable Middle East regional services and navigation engine compatibility.
- **Riyadh Timezone (GMT+3):** Aligns the hardware clock and GPS time synchronization with Saudi Arabia / Gulf standard time (`Asia/Riyadh`).
- **Anti-Brick Safeguards:** 
  - Standard Android 4.4 KitKat toolbox compatibility.
  - Automatic creation of a protected OEM factory backup before applying changes.
  - Atomic configuration verification (line-count check prevents corrupted writes).
- **Fully Reversible:** Can be cleanly uninstalled at any time via **NEMESIS Manager** to restore stock factory settings.
- **Emergency Recovery Stick:** Includes a dedicated offline recovery kit to restore the factory state under any circumstances.

---

## 🇸🇦 نظرة عامة باللغة العربية

توفر هذه الحزمة حلاً مبسطاً وآمناً وقابلاً للإلغاء بالكامل لإتاحة **اللغة العربية** وضبط **منطقة الشرق الأوسط** على شاشات **Gen5W** الخاصة بسيارات هيونداي وكيا وجينيسيس عبر نظام **NEMESIS**.

تعتمد الحزمة مبدأ **الحد الأدنى الحتمي من التعديلات (Minimal Safe Modifications)**؛ حيث تكتفي بضبط 3 خصائص أساسية فقط دون المساس بملفات المصنع الزائدة لضمان أقصى درجات الأمان وسلاسة التشغيل.

### 🎯 التعديلات المعتمدة في الحزمة:
```properties
# 1. إتاحة خيار اللغة العربية في قائمة لغات الشاشة
persist.sys.language_list=ko_KR,en_US,ar_EG

# 2. تعريف هوية الشرق الأوسط للنظام والملاحة (BuildInfo.REGION = 6)
ro.product.locale.region=ME

# 3. ضبط التوقيت الافتراضي للرياض (GMT+3) لمنع قفز الساعة مع الـ GPS
tcc.default.timezone=Asia/Riyadh
persist.sys.timezone=Asia/Riyadh
```

---

## 📁 Repository Structure / هيكل المستودع

```text
nemesis-arabic-package/
├── usb_package/                      <-- جاهز للنسخ المباشر إلى الفلاش ميموري (FAT32)
│   ├── NEMESIS.data                  (مُعرّف التثبيت التلقائي type=install)
│   └── packages/
│       └── arabic.locale.zip         (حزمة التثبيت الجاهزة)
│
├── arabic.locale/                    <-- السورس كود المصدري للحزمة
│   ├── NEMESIS.data                  (بيانات الحزمة وإصدارها)
│   ├── bin/status.sh                 (أداة فحص الحالة عبر NEMESIS Manager)
│   └── scripts/
│       ├── pre.sh                    (فحص مبدئي وتسجيل إخلاء المسؤولية)
│       ├── common.sh                 (مكتبة الدوال الآمنة لنظام كيت كات)
│       ├── post.sh                   (سكربت تطبيق التعديلات وحفظ الباك آب)
│       └── preun.sh                  (سكربت الاسترجاع الكامل لحالة الوكالة)
│
├── usb_emergency_recovery/           <-- مجلد فلاشة الطوارئ المستقلة
│   ├── NEMESIS.emergency             (ملف إجبار التنفيذ في حال تعطل واجهة الشاشة)
│   ├── NEMESIS.data                  (type=execute)
│   ├── NEMESIS.sh                    (سكربت الاسترجاع التلقائي)
│   └── build.prop                    (نسخة المصنع الأصلية للاسترجاع الفوري)
│
├── build_package.py                  <-- سكربت بايثون لإعادة فحص وبناء الحزمة
├── README.md                         <-- هذا التوثيق
└── LICENSE                           <-- ترخيص الملكية العامة (The Unlicense)
```

---

## 🚀 Installation / خطوات التثبيت

### المتطلبات (Prerequisites)
1. شاشة Gen5W مثبت عليها نظام **NEMESIS**.
2. فلاش ميموري (USB) مفورمت بنظام **FAT32**.

### الخطوات (Steps)
1. افتح مجلد [`usb_package`](usb_package/) وانسخ محتوياته كاملة إلى جذر الفلاش ميموري:
   ```text
   USB Drive (Root)
   ├── NEMESIS.data
   └── packages/
       └── arabic.locale.zip
   ```
2. شغّل السيارة وانتظر حتى تعمل الشاشة بالكامل.
3. أدخل الفلاش ميموري في منفذ USB الخاص بنظام الوسائط.
4. ستظهر رسالة تأكيد على الشاشة من مدير الحزم: **Install "Arabic & ME Localization"?**
5. اضغط **Yes**.
6. بعد اكتمال التثبيت، أعد تشغيل الشاشة أو دورة تشغيل السيارة.
7. اذهب إلى: **الإعدادات (Settings) ⬅️ عام (General) ⬅️ اللغة (Language)**، وستجد **العربية** متاحة في القائمة مباشرة للاختيار!

---

## 🔄 Uninstallation & Rollback / إلغاء التثبيت واسترجاع الوكالة

إذا أردت في أي وقت إزالة الحزمة والعودة إلى وضع المصنع:
1. من شاشة السيارة، افتح تطبيق **NEMESIS Manager**.
2. اذهب إلى **My Packages**.
3. اختر حزمة **Arabic & ME Localization**.
4. اضغط على **Uninstall**.
5. ستقوم الحزمة تلقائياً باسترجاع ملف `build.prop` الأصلي من النسخة الاحتياطية وحذف الإعدادات، ثم ستعود الشاشة كما كانت من المصنع 100%.

---

## 🆘 Emergency Recovery Kit / فلاشة الطوارئ المستقلة

إذا حدث أي طارئ أو انقطاع مفاجئ للكهرباء:
1. انسخ محتويات مجلد [`usb_emergency_recovery`](usb_emergency_recovery/) إلى فلاش ميموري (FAT32).
2. تأكد من وجود ملف `build.prop` الأصلي لسيارتك في جذر الفلاش.
3. ضع الفلاش في السيارة.
4. بفضل وجود ملف `NEMESIS.emergency`، سيتعرف نظام NEMESIS على الفلاش ويقوم بنسخ ملف الوكالة فوراً وإعادة تشغيل الشاشة تلقائياً دون الحاجة للمس الشاشة أو انتظار واجهة أندرويد.

---

## ⚠️ Disclaimer / إخلاء مسؤولية

> [!CAUTION]
> هذا العمل متاح للجميع بشكل مجاني وحر تماماً كمنفعة عامة.
> استخدامك لهذه الحزمة يتم على مسؤوليتك الشخصية الكاملة دون أي مسؤولية أو ضمان من أي نوع على المطورين في حال حدوث أي عطل أو تلف للشاشة نتيجة سوء الاستخدام. احرص دائماً على الاحتفاظ بنسخة احتياطية لملف نظامك الأصلي.

---

## 📄 License / الترخيص

هذا المشروع متاح تحت ترخيص **[The Unlicense](LICENSE)** (ملكية عامة بالكامل - Public Domain)، مما يتيح لأي شخص نسخه، تعديله، استخدامه، نشره، أو دمجه في أي مشروع دون أي قيود ودون الحاجة لذكر حقوق أو أسماء.
