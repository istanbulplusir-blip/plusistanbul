"""
Management command to create test data for StaticPage model (Privacy & Terms).
"""

from django.core.management.base import BaseCommand
from django.utils.translation import activate
from shared.models import StaticPage


class Command(BaseCommand):
    help = 'Create test data for Privacy and Terms static pages'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating test data for Static Pages...'))

        # Privacy Page
        self.stdout.write('Creating Privacy page...')
        privacy_page, created = StaticPage.objects.get_or_create(
            page_type='privacy',
            defaults={
                'slug': 'privacy-policy',
                'is_active': True,
                'meta_description': 'Privacy Policy - How we collect, use, and protect your personal information',
                'meta_keywords': 'privacy, policy, data protection, GDPR, personal information',
            }
        )

        # Set Persian translation
        activate('fa')
        privacy_page.set_current_language('fa')
        privacy_page.title = 'سیاست حفظ حریم خصوصی'
        privacy_page.excerpt = 'نحوه جمع‌آوری، استفاده و محافظت از اطلاعات شخصی شما'
        privacy_page.content = '''
<h2>مقدمه</h2>
<p>در پیکان توریسم، ما به حفظ حریم خصوصی شما متعهد هستیم. این سیاست حفظ حریم خصوصی نحوه جمع‌آوری، استفاده و محافظت از اطلاعات شخصی شما را توضیح می‌دهد.</p>

<h2>جمع‌آوری اطلاعات</h2>
<p>ما اطلاعات شخصی شما را هنگام ثبت‌نام، رزرو تور یا استفاده از خدمات ما جمع‌آوری می‌کنیم. این اطلاعات شامل نام، ایمیل، شماره تلفن و اطلاعات پرداخت می‌شود. ما همچنین ممکن است اطلاعات مربوط به استفاده شما از وب‌سایت ما را از طریق کوکی‌ها و فناوری‌های مشابه جمع‌آوری کنیم.</p>

<h2>استفاده از اطلاعات</h2>
<p>ما از اطلاعات شما برای ارائه و بهبود خدمات خود، پردازش رزروها، ارسال اطلاعات مربوط به سفارشات شما و ارتباط با شما در مورد محصولات و خدمات جدید استفاده می‌کنیم. ما همچنین ممکن است از اطلاعات شما برای تحلیل روندها و بهبود تجربه کاربری استفاده کنیم.</p>

<h2>امنیت اطلاعات</h2>
<p>ما از اقدامات امنیتی مناسب برای محافظت از اطلاعات شخصی شما در برابر دسترسی غیرمجاز، تغییر، افشا یا تخریب استفاده می‌کنیم. ما از رمزگذاری SSL برای محافظت از اطلاعات حساس شما در طول انتقال استفاده می‌کنیم.</p>

<h2>حقوق کاربران</h2>
<p>شما حق دارید به اطلاعات شخصی خود دسترسی داشته باشید، آن‌ها را تصحیح کنید یا حذف کنید. شما همچنین می‌توانید از پردازش اطلاعات خود انصراف دهید یا درخواست محدودیت پردازش کنید. برای اعمال این حقوق، لطفاً با ما تماس بگیرید.</p>

<h2>تماس با ما</h2>
<p>اگر سوالی در مورد این سیاست حفظ حریم خصوصی دارید، لطفاً از طریق ایمیل یا تلفن با ما تماس بگیرید. ما خوشحال خواهیم شد که به سوالات شما پاسخ دهیم.</p>
'''
        privacy_page.save()

        # Set English translation
        activate('en')
        privacy_page.set_current_language('en')
        privacy_page.title = 'Privacy Policy'
        privacy_page.excerpt = 'How we collect, use, and protect your personal information'
        privacy_page.content = '''
<h2>Introduction</h2>
<p>At Peykan Tourism, we are committed to protecting your privacy. This Privacy Policy explains how we collect, use, and protect your personal information.</p>

<h2>Information Collection</h2>
<p>We collect your personal information when you register, book a tour, or use our services. This information includes your name, email, phone number, and payment information. We may also collect information about your use of our website through cookies and similar technologies.</p>

<h2>Use of Information</h2>
<p>We use your information to provide and improve our services, process bookings, send you information about your orders, and communicate with you about new products and services. We may also use your information to analyze trends and improve user experience.</p>

<h2>Information Security</h2>
<p>We use appropriate security measures to protect your personal information from unauthorized access, alteration, disclosure, or destruction. We use SSL encryption to protect your sensitive information during transmission.</p>

<h2>User Rights</h2>
<p>You have the right to access, correct, or delete your personal information. You can also opt-out of processing your information or request restrictions on processing. To exercise these rights, please contact us.</p>

<h2>Contact Us</h2>
<p>If you have any questions about this Privacy Policy, please contact us via email or phone. We will be happy to answer your questions.</p>
'''
        privacy_page.save()

        # Set Turkish translation
        activate('tr')
        privacy_page.set_current_language('tr')
        privacy_page.title = 'Gizlilik Politikası'
        privacy_page.excerpt = 'Kişisel bilgilerinizi nasıl topladığımız, kullandığımız ve koruduğumuz'
        privacy_page.content = '''
<h2>Giriş</h2>
<p>Peykan Turizm olarak gizliliğinizi korumaya kararlıyız. Bu Gizlilik Politikası, kişisel bilgilerinizi nasıl topladığımızı, kullandığımızı ve koruduğumuzu açıklar.</p>

<h2>Bilgi Toplama</h2>
<p>Kayıt olduğunuzda, tur rezervasyonu yaptığınızda veya hizmetlerimizi kullandığınızda kişisel bilgilerinizi toplarız. Bu bilgiler adınızı, e-postanızı, telefon numaranızı ve ödeme bilgilerinizi içerir. Ayrıca çerezler ve benzer teknolojiler aracılığıyla web sitemizi kullanımınızla ilgili bilgileri toplayabiliriz.</p>

<h2>Bilgilerin Kullanımı</h2>
<p>Bilgilerinizi hizmetlerimizi sağlamak ve geliştirmek, rezervasyonları işlemek, siparişlerinizle ilgili bilgileri size göndermek ve yeni ürün ve hizmetler hakkında sizinle iletişim kurmak için kullanırız. Ayrıca trendleri analiz etmek ve kullanıcı deneyimini geliştirmek için bilgilerinizi kullanabiliriz.</p>

<h2>Bilgi Güvenliği</h2>
<p>Kişisel bilgilerinizi yetkisiz erişim, değiştirme, ifşa veya imhadan korumak için uygun güvenlik önlemleri kullanırız. İletim sırasında hassas bilgilerinizi korumak için SSL şifrelemesi kullanırız.</p>

<h2>Kullanıcı Hakları</h2>
<p>Kişisel bilgilerinize erişme, düzeltme veya silme hakkına sahipsiniz. Ayrıca bilgilerinizin işlenmesinden vazgeçebilir veya işleme kısıtlamaları talep edebilirsiniz. Bu hakları kullanmak için lütfen bizimle iletişime geçin.</p>

<h2>Bize Ulaşın</h2>
<p>Bu Gizlilik Politikası hakkında herhangi bir sorunuz varsa, lütfen e-posta veya telefon yoluyla bizimle iletişime geçin. Sorularınızı yanıtlamaktan mutluluk duyarız.</p>
'''
        privacy_page.save()

        if created:
            self.stdout.write(self.style.SUCCESS('✓ Privacy page created successfully'))
        else:
            self.stdout.write(self.style.WARNING('✓ Privacy page already exists, updated translations'))

        # Terms Page
        self.stdout.write('Creating Terms page...')
        terms_page, created = StaticPage.objects.get_or_create(
            page_type='terms',
            defaults={
                'slug': 'terms-of-service',
                'is_active': True,
                'meta_description': 'Terms of Service - Rules and conditions for using our services',
                'meta_keywords': 'terms, conditions, service, rules, agreement',
            }
        )

        # Set Persian translation
        activate('fa')
        terms_page.set_current_language('fa')
        terms_page.title = 'شرایط خدمات'
        terms_page.excerpt = 'قوانین و شرایط استفاده از خدمات ما'
        terms_page.content = '''
<h2>مقدمه</h2>
<p>با استفاده از خدمات پیکان توریسم، شما با این شرایط و ضوابط موافقت می‌کنید. لطفاً این شرایط را با دقت بخوانید.</p>

<h2>پذیرش شرایط</h2>
<p>با دسترسی یا استفاده از خدمات ما، شما تأیید می‌کنید که این شرایط خدمات را خوانده و درک کرده‌اید و موافقت می‌کنید که به آن‌ها پایبند باشید. اگر با این شرایط موافق نیستید، لطفاً از خدمات ما استفاده نکنید.</p>

<h2>خدمات</h2>
<p>ما خدمات رزرو تور، رویداد، انتقال و اجاره خودرو را ارائه می‌دهیم. تمام خدمات ما مشمول در دسترس بودن و تأیید هستند. ما حق داریم هر زمان که لازم باشد خدمات خود را تغییر دهیم یا متوقف کنیم.</p>

<h2>سیاست رزرو</h2>
<p>تمام رزروها باید از طریق وب‌سایت یا تماس مستقیم با ما انجام شوند. پرداخت کامل یا پیش‌پرداخت ممکن است برای تأیید رزرو شما لازم باشد. ما حق داریم رزروهایی را که پرداخت نشده‌اند لغو کنیم.</p>

<h2>سیاست لغو</h2>
<p>سیاست لغو ما بسته به نوع خدمت و زمان لغو متفاوت است. لغو رایگان معمولاً تا 48 ساعت قبل از تاریخ خدمت امکان‌پذیر است. لغوهای دیرهنگام ممکن است مشمول هزینه لغو شوند. لطفاً سیاست لغو خاص هر خدمت را بررسی کنید.</p>

<h2>محدودیت مسئولیت</h2>
<p>ما تلاش می‌کنیم تا خدمات با کیفیت بالا ارائه دهیم، اما نمی‌توانیم تضمین کنیم که خدمات ما بدون خطا یا وقفه باشند. ما مسئولیتی در قبال خسارات غیرمستقیم، تصادفی یا تبعی ناشی از استفاده از خدمات ما نداریم.</p>

<h2>تغییرات در شرایط</h2>
<p>ما حق داریم این شرایط خدمات را در هر زمان تغییر دهیم. تغییرات در این صفحه منتشر خواهند شد و تاریخ "آخرین به‌روزرسانی" در بالای صفحه به‌روزرسانی خواهد شد. استفاده مداوم شما از خدمات ما پس از تغییرات به معنای پذیرش شرایط جدید است.</p>
'''
        terms_page.save()

        # Set English translation
        activate('en')
        terms_page.set_current_language('en')
        terms_page.title = 'Terms of Service'
        terms_page.excerpt = 'Rules and conditions for using our services'
        terms_page.content = '''
<h2>Introduction</h2>
<p>By using Peykan Tourism services, you agree to these terms and conditions. Please read these terms carefully.</p>

<h2>Acceptance of Terms</h2>
<p>By accessing or using our services, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service. If you do not agree with these terms, please do not use our services.</p>

<h2>Services</h2>
<p>We provide tour booking, event, transfer, and car rental services. All our services are subject to availability and confirmation. We reserve the right to modify or discontinue our services at any time as necessary.</p>

<h2>Booking Policy</h2>
<p>All bookings must be made through our website or by direct contact with us. Full payment or deposit may be required to confirm your booking. We reserve the right to cancel bookings that have not been paid.</p>

<h2>Cancellation Policy</h2>
<p>Our cancellation policy varies depending on the type of service and cancellation time. Free cancellation is usually possible up to 48 hours before the service date. Late cancellations may be subject to cancellation fees. Please review the specific cancellation policy for each service.</p>

<h2>Limitation of Liability</h2>
<p>We strive to provide high-quality services, but we cannot guarantee that our services will be error-free or uninterrupted. We are not liable for any indirect, incidental, or consequential damages arising from the use of our services.</p>

<h2>Changes to Terms</h2>
<p>We reserve the right to change these Terms of Service at any time. Changes will be posted on this page and the "Last Updated" date at the top of the page will be updated. Your continued use of our services after changes constitutes acceptance of the new terms.</p>
'''
        terms_page.save()

        # Set Turkish translation
        activate('tr')
        terms_page.set_current_language('tr')
        terms_page.title = 'Hizmet Şartları'
        terms_page.excerpt = 'Hizmetlerimizi kullanmak için kurallar ve koşullar'
        terms_page.content = '''
<h2>Giriş</h2>
<p>Peykan Turizm hizmetlerini kullanarak bu şart ve koşulları kabul etmiş olursunuz. Lütfen bu şartları dikkatlice okuyun.</p>

<h2>Şartların Kabulü</h2>
<p>Hizmetlerimize erişerek veya kullanarak, bu Hizmet Şartlarını okuduğunuzu, anladığınızı ve bunlara bağlı kalmayı kabul ettiğinizi onaylarsınız. Bu şartları kabul etmiyorsanız, lütfen hizmetlerimizi kullanmayın.</p>

<h2>Hizmetler</h2>
<p>Tur rezervasyonu, etkinlik, transfer ve araç kiralama hizmetleri sunuyoruz. Tüm hizmetlerimiz müsaitlik ve onaya tabidir. Gerektiğinde hizmetlerimizi değiştirme veya durdurma hakkını saklı tutarız.</p>

<h2>Rezervasyon Politikası</h2>
<p>Tüm rezervasyonlar web sitemiz üzerinden veya bizimle doğrudan iletişim kurarak yapılmalıdır. Rezervasyonunuzu onaylamak için tam ödeme veya depozito gerekebilir. Ödenmemiş rezervasyonları iptal etme hakkını saklı tutarız.</p>

<h2>İptal Politikası</h2>
<p>İptal politikamız hizmet türüne ve iptal zamanına bağlı olarak değişir. Ücretsiz iptal genellikle hizmet tarihinden 48 saat öncesine kadar mümkündür. Geç iptaller iptal ücretine tabi olabilir. Lütfen her hizmet için özel iptal politikasını inceleyin.</p>

<h2>Sorumluluk Sınırlaması</h2>
<p>Yüksek kaliteli hizmetler sunmaya çalışıyoruz, ancak hizmetlerimizin hatasız veya kesintisiz olacağını garanti edemeyiz. Hizmetlerimizin kullanımından kaynaklanan dolaylı, tesadüfi veya sonuç olarak ortaya çıkan zararlardan sorumlu değiliz.</p>

<h2>Şartlarda Değişiklikler</h2>
<p>Bu Hizmet Şartlarını istediğimiz zaman değiştirme hakkını saklı tutarız. Değişiklikler bu sayfada yayınlanacak ve sayfanın üst kısmındaki "Son Güncelleme" tarihi güncellenecektir. Değişikliklerden sonra hizmetlerimizi kullanmaya devam etmeniz yeni şartları kabul ettiğiniz anlamına gelir.</p>
'''
        terms_page.save()

        if created:
            self.stdout.write(self.style.SUCCESS('✓ Terms page created successfully'))
        else:
            self.stdout.write(self.style.WARNING('✓ Terms page already exists, updated translations'))

        self.stdout.write(self.style.SUCCESS('\n✅ Test data creation completed!'))
        self.stdout.write(self.style.SUCCESS('\nYou can now:'))
        self.stdout.write('1. Visit Django Admin: http://127.0.0.1:8000/admin/shared/staticpage/')
        self.stdout.write('2. Test API endpoints:')
        self.stdout.write('   - GET http://127.0.0.1:8000/api/shared/pages/')
        self.stdout.write('   - GET http://127.0.0.1:8000/api/shared/pages/privacy/')
        self.stdout.write('   - GET http://127.0.0.1:8000/api/shared/pages/terms/')
        self.stdout.write('3. Edit content in Admin panel and see changes in API')
