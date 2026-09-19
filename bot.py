import imaplib
import email
import re
import os
import random
import string
import time
from playwright.sync_api import sync_playwright

# --- 1. الإعدادات والبيانات السرية ---
IMAP_SERVER = "outlook.office365.com"
EMAIL_USER = os.getenv("EMAIL_USER", "zwri@outlook.sa")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# رقم الـ Device ID الخاص بالتلفزيون
DEVICE_ID = os.getenv("DEVICE_ID", "d2ae-801d-d2f7-94d5-9398")

# الرابط الأساسي لبداية العملية
TARGET_URL = f"https://mytv.best/qr-code/?action=modification&cc=sa&utm_source=app&utm_medium=organic&utm_campaign=upload&tvid={DEVICE_ID}&lang=ar-SA"

def generate_random_email():
    """توليد بريد إلكتروني عشوائي ينتهي بـ gmail.com"""
    rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
    return f"user_{rand_str}@gmail.com"

def fetch_m3u_from_email():
    """الاتصال بـ Outlook واستخراج رابط M3U من آخر إيميل"""
    try:
        print("📧 جاري الاتصال بالبريد الإلكتروني...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        status, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()

        if not email_ids:
            print("❌ لا توجد رسائل في البريد الوارد.")
            return None

        # جلب أحدث إيميل
        latest_id = email_ids[-1]
        status, data = mail.fetch(latest_id, '(RFC822)')
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

        # البحث عن رابط M3U
        match = re.search(r'https?://[^\s<>"]+?\.m3u[^\s<>"]*', body, re.IGNORECASE)
        if not match:
            match = re.search(r'https?://[^\s<>"]+', body)

        if match:
            url = match.group(0)
            print(f"✅ تم استخراج رابط M3U: {url}")
            return url
        else:
            print("❌ لم يتم العثور على رابط M3U في الإيميل.")
            return None

    except Exception as e:
        print(f"❌ خطأ في قراءة البريد: {e}")
        return None

def submit_to_mytv(m3u_url):
    """تنفيذ خطوات الانتقال بين الصفحات الثلاث وتعبئة البيانات"""
    random_email = generate_random_email()
    print(f"🌐 بدء العملية بـ Device ID: {DEVICE_ID} وحساب: {random_email}")

    with sync_playwright() as p:
        # تشغيل المتصفح بوضع الخفاء
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
        )
        page = context.new_page()

        try:
            # 📍 الصفحة الأولى: الانتقال إلى رابط التعديل
            print("1️⃣ فتح الصفحة الأولى...")
            page.goto(TARGET_URL, wait_until="networkidle")
            time.sleep(2)

            # الضغط على زر "Express Modification >>"
            print("👆 الضغط على Express Modification >>")
            express_btn = page.locator("text=Express Modification").first
            express_btn.click()
            page.wait_for_load_state("networkidle")
            time.sleep(2)

            # 📍 الصفحة الثانية: اختيار رفع قائمة جديدة
            print("2️⃣ الصفحة الثانية: الضغط على Upload new playlist >>...")
            upload_playlist_btn = page.locator("text=Upload new playlist").first
            upload_playlist_btn.click()
            page.wait_for_load_state("networkidle")
            time.sleep(2)

            # 📍 الصفحة الثالثة: تعبئة الاستمارة
            print("3️⃣ الصفحة الثالثة: تعبئة البيانات...")

            # أ) التحقق من Device ID وإدخاله إن لم يكن مكتوباً
            device_input = page.locator("input[name*='device'], input[placeholder*='device'], input[value*='d2ae']").first
            if device_input.is_visible():
                device_input.fill("")
                device_input.fill(DEVICE_ID)

            # ب) كتابة الإيميل العشوائي (ينتهي بـ gmail.com)
            email_input = page.locator("input[type='email'], input[placeholder*='email']").first
            email_input.fill(random_email)
            print(f"   - تم إدخال البريد: {random_email}")

            # ج) اختيار مصدر القائمة (M3U URL)
            print("   - اختيار M3U URL...")
            try:
                page.select_option("select", label="M3U URL")
            except:
                page.click("text=Choose playlist source")
                time.sleep(0.5)
                page.click("text=M3U URL")

            time.sleep(1)

            # د) إدخال رابط M3U المستخرج من الإيميل
            url_input = page.locator("input[name*='url'], input[placeholder*='http']").first
            url_input.fill(m3u_url)
            print(f"   - تم إدخال رابط M3U.")

            # هـ) تحديد مربع الموافقة على الشروط
            checkbox = page.locator("input[type='checkbox']").first
            if checkbox.is_visible() and not checkbox.is_checked():
                checkbox.check()
                print("   - تم الموافقة على الشروط.")

            time.sleep(1)

            # و) الضغط على زر Upload السفلي لإتمام العملية
            print("🚀 الضغط على زر Upload النهائي...")
            final_upload_btn = page.locator("button:has-text('Upload'), input[value='Upload']").last
            final_upload_btn.click()

            time.sleep(5)
            print("🎉 تم إرسال التحديث بنجاح إلى التلفزيون!")

        except Exception as e:
            print(f"❌ حدث خطأ أثناء التنقل في الموقع: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    m3u_link = fetch_m3u_from_email()
    if m3u_link:
        submit_to_mytv(m3u_link)
    else:
        print("⚠️ تم الإلغاء لعدم توفر رابط M3U.")
