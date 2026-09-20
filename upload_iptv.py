import os
import sys
from playwright.sync_api import sync_playwright

def main():
    m3u_url = os.environ.get("M3U_URL")
    if not m3u_url:
        print("خطأ: لم يتم تزويد رابط M3U!")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        )
        page = context.new_page()

        # الخطوة الأولى
        print("الخطوة 1: فتح الموقع والضغط على Express Modification...")
        target_url = "https://mytv.best/qr-code/?action=modification&cc=sa&utm_source=app&utm_medium=organic&utm_campaign=upload&tvid=d2ae-801d-d2f7-94d5-9398&lang=ar-SA"
        page.goto(target_url, wait_until="networkidle")
        
        # استخدام exact text للابتعاد عن مشاكل الرموز
        page.get_by_text("Express Modification", exact=False).click()
        page.wait_for_load_state("networkidle")

        # الخطوة الثانية
        print("الخطوة 2: الضغط على Upload new playlist...")
        page.get_by_text("Upload new playlist", exact=False).click()
        page.wait_for_load_state("networkidle")

        # الخطوة الثالثة: تعبئة البيانات
        print("الخطوة 3: تعبئة البيانات والرابط...")
        
        # التأكد من Device ID
        device_input = page.locator("input").filter(has_text="").first
        # البحث عن حقل البريد الإلكتروني وتعبئته
        page.locator("input[type='email']").fill("jyfgjufdg@gmail.com")

        # اختيار M3U URL من القائمة المنسدلة
        selects = page.locator("select")
        if selects.count() > 0:
            # تحديد الخيار الأول الخاص بالـ M3U URL
            selects.last.select_option(index=1)

        # كتابة رابط M3U في حقل النص الخاص به
        page.locator("input[type='text']").last.fill(m3u_url)

        # تحديد مربع الموافقة على الشروط
        page.locator("input[type='checkbox']").check()

        # الضغط على Upload
        print("الضغط على زر Upload...")
        page.get_by_role("button", name="Upload").click()
        page.wait_for_load_state("networkidle")

        # الخطوة الرابعة: التخطي (Skip الأول والثاني)
        print("الخطوة 4: الضغط على Skip (Cleaning Groups)...")
        page.get_by_text("Skip", exact=True).first.click(timeout=10000)
        page.wait_for_load_state("networkidle")

        print("الضغط على Skip (Parental Control)...")
        page.get_by_text("Skip", exact=True).first.click(timeout=10000)
        page.wait_for_load_state("networkidle")

        print("تمت العملية بنجاح! 🎉")
        browser.close()

if __name__ == "__main__":
    main()
