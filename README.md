# NEMESIS Arabic Localization Mod for Gen5W
### حزم تفعيل اللغة العربية وضبط توافق خرائط الشرق الأوسط لشاشات هيونداي وكيا وجينيسيس (Gen5W)

[![Platform](https://img.shields.io/badge/Platform-Gen5W%20(Android%204.4.2)-blue.svg)](#)
[![Compatibility](https://img.shields.io/badge/Framework-NEMESIS%20v1.1+-green.svg)](#)
[![License: Unlicense](https://img.shields.io/badge/License-Unlicense%20(Public%20Domain)-lightgrey.svg)](LICENSE)

---

> [!IMPORTANT]
> **[AR] تنبيه هام جداً بخصوص الخرائط:**  
> هذه الحزمة **لا تحتوي على ملفات الخرائط إطلاقاً ولا تقوم بتحميلها**، بل تقوم فقط بـ **التهيئة البرمجية اللازمة للنظام (System Adaptation)** لتمكين محرك الملاحة الأصلي في الشاشة من قبول وتشغيل خرائط الشرق الأوسط (والتي يتم توفيرها بشكل منفصل عبر بطاقة الذاكرة SD أو التحديث الرسمي).
>
> **[EN] CRITICAL NOTICE REGARDING NAVIGATION MAPS:**  
> This package **does NOT contain or download map files**. It only provides the **system-level adaptation** required for the vehicle's native navigation engine to recognize, accept, and run Middle East map data (which must be supplied separately via an SD card or official map update).

> [!NOTE]
> **[AR] ميزة الأمان المزدوج للنسخ الاحتياطي (USB + ذاكرة الشاشة):**  
> عند تشغيل الحزمة أو استخدام فلاشة الطوارئ، يقوم النظام تلقائياً وبشكل فوري بحفظ نسخة احتياطية من ملفات المصنع الأصلية لسيارتك في **مكانين مستقلين**:  
> 1. داخل الفلاش ميموري (USB) في مجلد `OEM_BACKUP`.  
> 2. داخل الذاكرة الداخلية لوحدة الشاشة نفسها في مسار محمي `/data/nemesis/build.prop.stock`.  
> وبذلك تضمن بقاء نسخة الوكالة الأصلية محفوظة دائماً حتى لو ضاع الفلاش ميموري!
>
> **[EN] Dual Backup Redundancy Feature (USB + Head Unit Storage):**  
> During installation or when using the Emergency Recovery Stick, the system automatically saves a genuine OEM backup of your vehicle's factory files to **two independent locations**:  
> 1. Onto your USB drive inside the `OEM_BACKUP` folder.  
> 2. Internally inside your head unit's permanent storage at `/data/nemesis/build.prop.stock`.  
> This guarantees your factory state is always safely retained even if the USB drive is detached or lost.

---

## 📦 حزم التحميل الجاهزة / Ready-to-Use Release Packages

يمكنك تحميل الحزم الجاهزة للنسخ المباشر من مجلد [`releases/`](releases/):
* 💾 **[`Gen5W_Arabic_USB_Package.zip`](releases/Gen5W_Arabic_USB_Package.zip)**:  
  **[AR]** ملف مضغوط يحتوي على كافة ملفات التثبيت الجاهزة (`NEMESIS.data` و `packages/`). فقط فك الضغط مباشرة داخل الفلاش ميموري (FAT32).  
  **[EN]** Pre-packaged zip containing ready-to-use installer files. Extract directly to the root of your FAT32 USB drive.
* 🆘 **[`Gen5W_Emergency_Recovery_USB.zip`](releases/Gen5W_Emergency_Recovery_USB.zip)**:  
  **[AR]** فلاشة الطوارئ الشاملة الجاهزة للفك المباشر.  
  **[EN]** Universal emergency recovery package ready to extract to a USB drive.

---

## 📊 مقارنة الخيارات المتاحة / Available Options Comparison

| وجه المقارنة / Feature | الخيار الأول: تعريب البروفايل (الآمن 100%)<br>Mode 1: Safe Profile UI (`arabic.ui`) | الخيار الثاني: توافق خرائط الشرق الأوسط والتعريب<br>Mode 2: ME Map Compatibility & Arabic (`arabic.full`) |
| :--- | :--- | :--- |
| **طبيعة التعديل**<br>Scope of Changes | **في بيانات المستخدم فقط (`/data`)**<br>User Data Partition Only | **في ملف النظام (`/system/build.prop`)**<br>System Partition Modification |
| **المساس بملف `build.prop`**<br>`build.prop` Alteration | **لا يمس ملف `build.prop` نهائياً (0% تعديل)**<br>Zero modifications, 100% factory intact | **يعدل سطر المنطقة إلى `ro.product.locale.region=ME`**<br>Sets Middle East region code |
| **حالة حماية النظام**<br>System Mount Status | **يبقى النظام مقفلاً للقراءة فقط (Read-Only)**<br>Remains 100% Read-Only | **يُعاد قفله فوراً بعد تعديل السطر**<br>Temporarily remounted RW, then locked RO |
| **لغات السيارة الأصلية**<br>Original Vehicle Languages | **يحتفظ بلغات سيارتك أياً كانت ويضيف العربية**<br>Preserves native languages & appends Arabic | **يحتفظ بلغات سيارتك أياً كانت ويضيف العربية**<br>Preserves native languages & appends Arabic |
| **التوافق مع التعديلات الكورية**<br>Korean Mods Compatibility | **متوافق 100% (لا يؤثر على CarPlay/AA أو Tilepad)**<br>100% Compatible with Wireless CarPlay/AA | **قد يعطل بعض التعديلات المخصصة لكوريا فقط**<br>May affect Korean-only features (`REGION=0`) |
| **خرائط الملاحة الأصلية**<br>Native Navigation Maps | **تبقى خرائط الوكالة (مثالي لمستخدمي خرائط الهاتف)**<br>Retains factory maps (ideal for Google Maps / Waze) | **يهيئ الشاشة لقبول خرائط الشرق الأوسط (SD Card)**<br>Enables ME navigation engine compatibility |
| **لمن نوصي به؟**<br>Recommended For | **لجميع المستخدمين ومستخدمي CarPlay و Android Auto**<br>Everyone using CarPlay, AA, or third-party mods | **لمن يريد تشغيل الخرائط الأصلية للشرق الأوسط**<br>Users requiring native Middle East offline navigation |

---

## 🚀 خطوات التثبيت / Installation Steps

### [AR] المتطلبات:
1. شاشة Gen5W مثبت عليها نظام **NEMESIS**.
2. فلاش ميموري بنظام تهيئة **FAT32** أو **exFAT**.

### [EN] Prerequisites:
1. Gen5W head unit running **NEMESIS**.
2. USB flash drive formatted as **FAT32** or **exFAT**.

---

### [AR] خطوات التركيب:
1. انسخ محتويات مجلد [`usb_package`](usb_package/) (أو فك ضغط ملف [`Gen5W_Arabic_USB_Package.zip`](releases/Gen5W_Arabic_USB_Package.zip)) كاملة إلى جذر الفلاش ميموري (Root):
   ```text
   USB Drive (Root)
   ├── NEMESIS.data
   └── packages/
       ├── arabic.ui.zip         (خيار البروفايل الآمن)
       └── arabic.full.zip       (خيار توافق خرائط الشرق الأوسط)
   ```
2. شغّل السيارة وانتظر اكتمال إقلاع الشاشة.
3. أدخل الفلاش ميموري في منفذ USB الخاص بالوسائط في السيارة.
4. ستظهر لك نافذة متجر الحزم على الشاشة تعرض الخيارين:
   - اختر **Arabic Profile (Safe Mode)** لتعريب البروفايل بأعلى درجات الأمان.
   - أو اختر **ME Map & Arabic** لتهيئة النظام لتشغيل خرائط الشرق الأوسط.
5. اضغط **Install**.
6. سيقوم النظام بحفظ نسخة احتياطية لسيارتك في مجلد `OEM_BACKUP` على الفلاش وداخل ذاكرة الشاشة، وتطبيق التعديل، ثم إعادة تشغيل الشاشة تلقائياً.
7. بعد إعادة التشغيل، ادخل على:
   **الإعدادات (Settings) ⬅️ عام (General) ⬅️ اللغة (Language)**، واختر **العربية**.

---

### [EN] Installation Procedure:
1. Copy all contents from [`usb_package`](usb_package/) (or extract [`Gen5W_Arabic_USB_Package.zip`](releases/Gen5W_Arabic_USB_Package.zip)) directly to the USB drive root:
   ```text
   USB Drive (Root)
   ├── NEMESIS.data
   └── packages/
       ├── arabic.ui.zip         (Safe Profile Mode)
       └── arabic.full.zip       (ME Map Compatibility Mode)
   ```
2. Turn on the vehicle and wait for the head unit to fully boot.
3. Insert the USB flash drive into the media USB port.
4. The NEMESIS Package Store popup will appear offering both packages:
   - Select **Arabic Profile (Safe Mode)** for safe UI localization.
   - Or select **ME Map & Arabic** to enable Middle East offline map support.
5. Press **Install**.
6. The system automatically creates a per-vehicle backup in `OEM_BACKUP` on your USB and inside head unit storage, applies the mod, and reboots automatically.
7. After reboot, navigate to:
   **Settings ➡️ General ➡️ Language**, and select **العربية (Arabic)**.

---

## 🔄 إزالة الحزمة والعودة لوضع الوكالة / Uninstallation

### [AR] خطوات الإلغاء:
1. افتح تطبيق **NEMESIS Manager** من شاشة السيارة.
2. ادخل على قائمة الحزم المثبتة (**My Packages**).
3. اختر الحزمة المثبتة واضغط على **Uninstall**.
4. ستقوم الحزمة بحذف الإعدادات، واسترجاع نسخة المصنع الأصلية، وحذف الحزمة بالكامل من الشاشة وقاعدة البيانات، ثم إعادة تشغيل الشاشة تلقائياً.

### [EN] Uninstallation Procedure:
1. Open **NEMESIS Manager** on the vehicle display.
2. Go to **My Packages**.
3. Select the installed package and tap **Uninstall**.
4. The package restores factory settings, cleans package registration from the database and UI, and reboots automatically.

---

## 🆘 فلاشة الطوارئ الشاملة / Universal Emergency Recovery Stick

### [AR] الاسترجاع عند الطوارئ:
1. انسخ محتويات مجلد [`usb_emergency_recovery`](usb_emergency_recovery/) (أو فك ضغط [`Gen5W_Emergency_Recovery_USB.zip`](releases/Gen5W_Emergency_Recovery_USB.zip)) إلى فلاش ميموري FAT32.
2. أدخل الفلاش في السيارة.
3. بفضل ملف `NEMESIS.emergency`، سيبحث سكربت الطوارئ تلقائياً عن نسخة المصنع الأصلية لسيارتك المحفوظة مسبقاً في مجلد `OEM_BACKUP` على الفلاش أو في ذاكرة السيارة الداخلية، ويسترجعها فوراً ويعيد تشغيل الشاشة تلقائياً.

### [EN] Emergency Restoration:
1. Copy contents of [`usb_emergency_recovery`](usb_emergency_recovery/) (or extract [`Gen5W_Emergency_Recovery_USB.zip`](releases/Gen5W_Emergency_Recovery_USB.zip)) onto a FAT32 USB drive.
2. Insert the USB drive into the car.
3. Triggered by `NEMESIS.emergency`, the recovery script dynamically discovers your vehicle's stock backup from `OEM_BACKUP` or internal storage, restores it, and restarts the system.

---

## 📁 هيكل المستودع / Folder Structure

```text
nemesis-arabic-package/
├── releases/                         <-- [AR] ملفات التثبيت المضغوطة الجاهزة للتحميل
│   │                                 <-- [EN] Ready-to-download pre-packaged archives
│   ├── Gen5W_Arabic_USB_Package.zip  (Ready to extract to FAT32 USB root)
│   └── Gen5W_Emergency_Recovery_USB.zip (Emergency recovery stick package)
│
├── usb_package/                      <-- [AR] مجلد التثبيت الجاهز للنسخ المباشر
│   │                                 <-- [EN] Ready to copy directly to USB
│   ├── NEMESIS.data                  (Package Store multi-installer)
│   └── packages/
│       ├── arabic.ui.zip             (Safe Profile Mode: Zero /system modification)
│       └── arabic.full.zip           (ME Map Compatibility Mode)
│
├── arabic.ui/                        <-- [AR] السورس كود لخيار تعريب البروفايل
│   │                                 <-- [EN] Source code for Safe Profile Mode
│   ├── NEMESIS.data
│   ├── bin/status.sh
│   └── scripts/ (pre.sh, common.sh, post.sh, preun.sh)
│
├── arabic.full/                      <-- [AR] السورس كود لخيار توافق الخرائط
│   │                                 <-- [EN] Source code for ME Map Compatibility
│   ├── NEMESIS.data
│   ├── bin/status.sh
│   └── scripts/ (pre.sh, common.sh, post.sh, preun.sh)
│
├── usb_emergency_recovery/           <-- [AR] فلاشة الطوارئ الشاملة لكافة السيارات
│   │                                 <-- [EN] Universal emergency recovery stick
│   ├── NEMESIS.emergency
│   ├── NEMESIS.data
│   └── NEMESIS.sh
│
├── build_package.py                  <-- Build automation & descriptor validation
├── create_package_files.py           <-- Source files generator
├── README.md                         <-- Bilingual documentation
└── LICENSE                           <-- The Unlicense (Public Domain)
```

---

## ⚠️ إخلاء مسؤولية / Disclaimer

> [!CAUTION]
> **[AR]** هذا العمل متاح للجميع مجاناً كمنفعة عامة دون أي حقوق ملكية أو احتكار. استخدامك لهذه الحزم يتم على مسؤوليتك الشخصية الكاملة دون أدنى مسؤولية أو ضمان على المطورين في حال حدوث أي عطل أو تلف للشاشة نتيجة سوء الاستخدام.
>
> **[EN]** This project is released into the public domain as free software for community benefit. Use of this package is entirely at your own risk without warranty of any kind. Authors and contributors hold no liability for device failure, damage, or data loss.

---

## 📄 الترخيص / License

هذا المشروع متاح تحت رخصة **[The Unlicense](LICENSE)** (ملكية عامة بالكامل - Public Domain)، مما يتيح لأي شخص نسخه، تعديله، نشره، أو استخدامه بحرية تامة دون أي قيود أو حقوق.
