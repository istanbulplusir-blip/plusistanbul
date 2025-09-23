# سیاست امنیتی پروژه Peykan Tourism

## 📋 فهرست مطالب
- [گزارش آسیب‌پذیری‌ها](#گزارش-آسیب‌پذیری‌ها)
- [زمان‌بندی پاسخ](#زمان‌بندی-پاسخ)
- [اقدامات امنیتی](#اقدامات-امنیتی)
- [تست‌های امنیتی](#تست‌های-امنیتی)
- [پاسخ به حوادث](#پاسخ-به-حوادث)
- [تماس‌های اضطراری](#تماس‌های-اضطراری)

## 🚨 گزارش آسیب‌پذیری‌ها

### نحوه گزارش
اگر آسیب‌پذیری امنیتی کشف کرده‌اید، لطفاً آن را به صورت محرمانه گزارش دهید:

1. **ایجاد Issue خصوصی**: در GitHub یک private issue ایجاد کنید
2. **ایمیل مستقیم**: security@peykantravelistanbul.com
3. **تلگرام**: @PeykanSecurity

### اطلاعات مورد نیاز
لطفاً اطلاعات زیر را در گزارش خود قرار دهید:

```markdown
## خلاصه آسیب‌پذیری
توضیح کوتاه از مشکل امنیتی

## نوع آسیب‌پذیری
- SQL Injection
- XSS (Cross-Site Scripting)
- CSRF (Cross-Site Request Forgery)
- Authentication Bypass
- Authorization Flaw
- Information Disclosure
- Other

## مراحل تکرار
1. مرحله اول
2. مرحله دوم
3. مرحله سوم

## تأثیر
توضیح تأثیرات احتمالی این آسیب‌پذیری

## پیشنهادات
راه‌حل‌های پیشنهادی (اختیاری)

## اطلاعات تماس
- نام: [اختیاری]
- ایمیل: [اختیاری]
- GitHub: [اختیاری]
```

### قوانین گزارش
- **محرمانه بودن**: آسیب‌پذیری‌ها را در انظار عمومی منتشر نکنید
- **جزئیات کافی**: اطلاعات کافی برای درک و تکرار مشکل ارائه دهید
- **عدم سوء استفاده**: از آسیب‌پذیری برای دسترسی غیرمجاز استفاده نکنید
- **همکاری**: در صورت نیاز، برای رفع مشکل همکاری کنید

## ⏰ زمان‌بندی پاسخ

### جدول زمانی پاسخ
| نوع آسیب‌پذیری | زمان پاسخ اولیه | زمان رفع |
|----------------|-----------------|----------|
| Critical (9.0-10.0) | 24 ساعت | 7 روز |
| High (7.0-8.9) | 48 ساعت | 14 روز |
| Medium (4.0-6.9) | 72 ساعت | 30 روز |
| Low (0.1-3.9) | 1 هفته | 90 روز |

### مراحل پاسخ
1. **تأیید دریافت**: تأیید دریافت گزارش در 24 ساعت
2. **بررسی اولیه**: بررسی و تأیید آسیب‌پذیری
3. **اولویت‌بندی**: تعیین اولویت بر اساس CVSS score
4. **توسعه راه‌حل**: توسعه و تست راه‌حل
5. **استقرار**: استقرار راه‌حل در محیط تولید
6. **اعلام عمومی**: اعلام رفع مشکل (در صورت نیاز)

## 🔒 اقدامات امنیتی

### امنیت کد
- **Code Review**: بررسی امنیتی تمام تغییرات کد
- **Static Analysis**: استفاده از ابزارهای تحلیل استاتیک
- **Dependency Scanning**: بررسی آسیب‌پذیری‌های dependencies
- **Secret Scanning**: بررسی نشت اطلاعات حساس

### امنیت زیرساخت
- **Network Security**: فایروال و segmentation
- **Access Control**: کنترل دسترسی‌های سرور
- **Monitoring**: نظارت بر فعالیت‌های مشکوک
- **Backup Security**: امنیت فایل‌های backup

### امنیت اپلیکیشن
- **Input Validation**: اعتبارسنجی تمام ورودی‌ها
- **Output Encoding**: رمزگذاری خروجی‌ها
- **Authentication**: احراز هویت قوی
- **Authorization**: کنترل دسترسی دقیق

### امنیت داده
- **Encryption**: رمزگذاری داده‌های حساس
- **Data Minimization**: حداقل‌سازی داده‌های جمع‌آوری شده
- **Access Logging**: ثبت تمام دسترسی‌ها
- **Data Retention**: سیاست نگهداری داده‌ها

## 🧪 تست‌های امنیتی

### تست‌های خودکار
```bash
# تست dependencies
npm audit
pip-audit

# تست کد
bandit -r backend/
semgrep --config=auto backend/

# تست API
zap-baseline.py -t https://api.peykantravelistanbul.com
```

### تست‌های دستی
- **Penetration Testing**: تست نفوذ منظم
- **Security Code Review**: بررسی امنیتی کد
- **Configuration Review**: بررسی تنظیمات امنیتی
- **Access Control Testing**: تست کنترل دسترسی

### تست‌های عملکرد
- **Load Testing**: تست بار برای جلوگیری از DoS
- **Stress Testing**: تست استرس سیستم
- **Security Performance**: تست عملکرد ویژگی‌های امنیتی

## 🚨 پاسخ به حوادث

### مراحل پاسخ به حادثه
1. **تشخیص**: شناسایی و تأیید حادثه
2. **ارزیابی**: ارزیابی تأثیر و دامنه
3. **کنترل**: کنترل و محدود کردن آسیب
4. **حذف**: حذف علت ریشه‌ای
5. **بازیابی**: بازیابی سیستم
6. **یادگیری**: تحلیل و بهبود فرآیندها

### تیم پاسخ به حادثه
- **Incident Commander**: مسئول کلی پاسخ
- **Technical Lead**: مسئول جنبه‌های فنی
- **Communications Lead**: مسئول ارتباطات
- **Legal Advisor**: مشاور حقوقی (در صورت نیاز)

### مستندسازی
- **Incident Report**: گزارش کامل حادثه
- **Timeline**: جدول زمانی رویدادها
- **Lessons Learned**: درس‌های آموخته شده
- **Action Items**: اقدامات بهبود

## 📞 تماس‌های اضطراری

### تماس‌های فوری
- **ایمیل امنیتی**: security@peykantravelistanbul.com
- **تلگرام امنیتی**: @PeykanSecurity
- **شماره اضطراری**: +90 XXX XXX XXXX

### ساعات کاری
- **شنبه تا چهارشنبه**: 9:00 - 18:00 (GMT+3)
- **پنجشنبه**: 9:00 - 17:00 (GMT+3)
- **جمعه**: تعطیل (فقط موارد اضطراری)

### خارج از ساعات کاری
برای موارد اضطراری خارج از ساعات کاری:
1. ارسال ایمیل با موضوع "URGENT"
2. تماس تلگرامی با @PeykanSecurity
3. در صورت عدم پاسخ، تماس تلفنی

## 🛡️ بهترین شیوه‌ها

### برای توسعه‌دهندگان
- **Secure Coding**: پیروی از اصول کدنویسی امن
- **Regular Updates**: به‌روزرسانی منظم dependencies
- **Security Testing**: تست امنیتی قبل از استقرار
- **Documentation**: مستندسازی ویژگی‌های امنیتی

### برای کاربران
- **Strong Passwords**: استفاده از رمزهای قوی
- **2FA**: فعال‌سازی احراز هویت دو مرحله‌ای
- **Regular Updates**: به‌روزرسانی نرم‌افزارها
- **Phishing Awareness**: آگاهی از حملات فیشینگ

### برای ادمین‌ها
- **Access Control**: کنترل دقیق دسترسی‌ها
- **Monitoring**: نظارت مداوم بر سیستم
- **Backup Security**: امنیت فایل‌های backup
- **Incident Response**: آمادگی برای پاسخ به حوادث

## 📚 منابع مفید

### مستندات امنیتی
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [ISO 27001](https://www.iso.org/isoiec-27001-information-security.html)

### ابزارهای امنیتی
- **Static Analysis**: SonarQube, CodeQL
- **Dynamic Analysis**: OWASP ZAP, Burp Suite
- **Dependency Scanning**: Snyk, Dependabot
- **Secret Scanning**: GitGuardian, TruffleHog

### آموزش‌های امنیتی
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [HackerOne Hacktivity](https://hackerone.com/hacktivity)

---

## 🔄 به‌روزرسانی سیاست

این سیاست امنیتی به‌طور منظم بررسی و به‌روزرسانی می‌شود. آخرین به‌روزرسانی: **ژانویه 2024**

### تاریخچه تغییرات
- **ژانویه 2024**: ایجاد سیاست امنیتی اولیه
- **فوریه 2024**: اضافه کردن بخش تست‌های امنیتی
- **مارس 2024**: بهبود فرآیند پاسخ به حوادث

**تیم امنیتی Peykan Tourism**
- ایمیل: security@peykantravelistanbul.com
- تلگرام: @PeykanSecurity
- GitHub: [PeykanTravel/peykan-tourism](https://github.com/PeykanTravel/peykan-tourism) 