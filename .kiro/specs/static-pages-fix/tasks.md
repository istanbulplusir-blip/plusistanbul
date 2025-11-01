# Implementation Plan

- [x] 1. اضافه کردن کلیدهای ترجمه برای Privacy





  - اضافه کردن بخش `privacy` به `frontend/messages/fa.json` با تمام کلیدهای مورد نیاز
  - اضافه کردن بخش `privacy` به `frontend/messages/en.json` با ترجمه انگلیسی
  - اضافه کردن بخش `privacy` به `frontend/messages/tr.json` با ترجمه ترکی
  - شامل: title, description, content sections, cta
  - _Requirements: 1.1, 1.2, 1.3, 1.5, 4.1, 4.2, 4.3_

- [x] 2. اضافه کردن کلیدهای ترجمه برای Terms





  - اضافه کردن بخش `terms` به `frontend/messages/fa.json` با تمام کلیدهای مورد نیاز
  - اضافه کردن بخش `terms` به `frontend/messages/en.json` با ترجمه انگلیسی
  - اضافه کردن بخش `terms` به `frontend/messages/tr.json` با ترجمه ترکی
  - شامل: title, description, content sections, cta
  - _Requirements: 1.1, 1.2, 1.4, 1.5, 4.1, 4.2, 4.3_

- [x] 3. اضافه کردن Footer به StaticPageLayout





  - Import کردن Footer component در `StaticPageLayout.tsx`
  - اضافه کردن Footer به انتهای layout
  - اضافه کردن prop اختیاری `showFooter` (پیش‌فرض: true)
  - تست کردن که Footer در تمام صفحات Static نمایش داده می‌شود
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4. بروزرسانی صفحه Privacy با محتوای کامل و متناسب با سایر صفحات پروژه و دیزاین سیستم





  - اضافه کردن بخش‌های محتوایی به `privacy/page.tsx`
  - استفاده از کلیدهای ترجمه جدید
  - اضافه کردن sections: intro, dataCollection, dataUsage, dataSecurity, userRights, contact
  - استایل دهی مناسب با Tailwind CSS
  - _Requirements: 1.1, 1.3, 1.5_

- [x] 5. بروزرسانی صفحه Terms با محتوای کامل و متناسب با سایر صفحات پروژه و دیزاین سیستم





  - اضافه کردن بخش‌های محتوایی به `terms/page.tsx`
  - استفاده از کلیدهای ترجمه جدید
  - اضافه کردن sections: intro, acceptance, services, bookingPolicy, cancellationPolicy, liability, changes
  - استایل دهی مناسب با Tailwind CSS
  - _Requirements: 1.1, 1.4, 1.5_

- [x] 6. بررسی و رفع مشکلات سایر صفحات Static





  - بررسی صفحه FAQ برای خطاهای ترجمه
  - بررسی صفحه About برای خطاهای ترجمه
  - بررسی صفحه Contact برای خطاهای ترجمه
  - بررسی سایر صفحات استفاده شده در پروژه خصوصا صفحات مرتبط با اپ shared مثل catalog 
  - اضافه کردن کلیدهای ترجمه گمشده در صورت نیاز
  - تست کردن Footer در تمام صفحات
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 7. تست نهایی و اعتبارسنجی





  - تست Privacy page در سه زبان (fa, en, tr)
  - تست Terms page در سه زبان (fa, en, tr)
  - بررسی console برای خطاهای IntlError
  - تست Footer در تمام صفحات Static
  - تست در مرورگرهای مختلف (Chrome, Firefox, Safari)
  - بررسی ui/ux terms , privacy متناسب با سایر صفحات مثل contact about cataloge جهت حفط یکپارچکی ظاهری
  - بررسی دارک مود و لایت مود برای صفحات terms , privacy برای متن ها و بک گراند 
  - تست responsive design (Desktop, Tablet, Mobile)
  - اضافه کردن تسک ۸ برای مدیریت محتوای صفحات از طریق بک اند (بررسی مدل shared و صفحات مرتبط با ان و اپدیت ادمین برای مدیریت محتوای دینامیک)
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
