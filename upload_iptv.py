import os
import sys
from playwright.sync_api import sync_playwright

def main():
    # الحصول على رابط M3U من المدخلات
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

        # الخطوة الأولى: الذهاب إلى الرابط والضغط على Express Modification
        print("الخطوة 1: فتح الموقع والضغط على Express Modification...")
        target_url = "https://mytv.best/qr-code/?action=modification&cc=sa&utm_source=app&utm_medium=organic&utm_campaign=upload&tvid=d2ae-801d-d2f7-94d5-9398&lang=ar-SA"
        page.goto(target_url, wait_until="networkidle")
        page.click("text=Express Modification >>")
        page.wait_for_load_state("networkidle")

        # الخطوة الثانية: الضغط على Upload new playlist
        print("الخطوة 2: الضغط على Upload new playlist...")
        page.click("text=Upload new playlist >>")
        page.wait_for_load_state("networkidle")

        # الخطوة الثالثة: تعبئة البيانات
        print("الخطوة 3: تعبئة البيانات والرابط...")
        
        # التأكد من إدخال Device ID
        device_id_input = page.locator("input[placeholder='Device Id'], input[name='device_id']").first
        if device_id_input.is_visible():
            device_id_input.fill("d2ae-801d-d2f7-94d5-9398")

        # تحديد الدولة (تخطي إن كانت محددة أو خيار افتراضي)
        country_select = page.locator("select").first
        if country_select.is_visible():
            country_select.select_option(index=1)

        # كتابة البريد الإلكتروني
        email_input = page.locator("input[type='email'], input[placeholder*='email']").first
        email_input.fill("jyfgjufdg@gmail.com")

        # اختيار M3U URL من القائمة المنسدلة
        source_select = page.locator("select").nth(1) if page.locator("select").count() > 1 else page.locator("select").first
        # الضغط أو التحديد بناءً على خيارات القائمة
        try:
            source_select.select_option(label="M3U URL")
        except:
            page.select_option("select", label="M3U URL")

        # إدخال رابط M3U
        m3u_input = page.locator("input[placeholder*='M3U'], input[name*='m3u']").first
        m3u_input.fill(m3u_url)

        # تحديد مربع الموافقة على الشروط
        checkbox = page.locator("input[type='checkbox']").first
        if not checkbox.is_checked():
            checkbox.check()

        # الضغط على زر Upload
        print("الضغط على زر Upload...")
        page.click("button:has-text('Upload'), input[value='Upload']")
        page.wait_for_load_state("networkidle")

        # الخطوة الرابعة: التخطي (Skip الأول والثاني)
        print("الخطوة 4: الضغط على Skip (Cleaning Groups)...")
        page.click("text=Skip", timeout=10000)
        page.wait_for_load_state("networkidle")

        print("الضغط على Skip (Parental Control)...")
        page.click("text=Skip", timeout=10000)
        page.wait_for_load_state("networkidle")

        # التحقق من إتمام العملية
        if "successfully modified" in page.content().lower():
            print("تم تحديث القنوات بنجاح! 🎉")
        else:
            print("تمت العملية، يُرجى التأكد من التلفزيون.")

        browser.close()

if __name__ == "__main__":
    main()
