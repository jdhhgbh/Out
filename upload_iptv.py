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
        
        # استهداف الزر بدقة باستخدام role="button"
        page.get_by_role("button", name="Express Modification >>").click()
        page.wait_for_load_state("networkidle")

        # الخطوة الثانية
        print("الخطوة 2: الضغط على Upload new playlist...")
        page.get_by_role("button", name="Upload new playlist >>").click()
        page.wait_for_load_state("networkidle")

        # الخطوة الثالثة: تعبئة البيانات
        print("الخطوة 3: تعبئة البيانات والرابط...")
        
        # تعبئة البريد الإلكتروني
        page.locator("input[type='email']").fill("jyfgjufdg@gmail.com")

        # اختيار M3U URL من القائمة المنسدلة
        select_element = page.locator("select").first
        select_element.select_option(label="M3U URL")

        # كتابة رابط M3U في حقل M3U URL
        page.locator("input[type='text']").last.fill(m3u_url)

        # تحديد مربع الموافقة على الشروط
        checkbox = page.locator("input[type='checkbox']").first
        if not checkbox.is_checked():
            checkbox.check()

        # الضغط على زر Upload
        print("الضغط على زر Upload...")
        page.get_by_role("button", name="Upload").click()
        page.wait_for_load_state("networkidle")

        # الخطوة الرابعة: التخطي (Skip الأول والثاني)
        print("الخطوة 4: الضغط على Skip (Cleaning Groups)...")
        page.get_by_role("button", name="Skip").first.click(timeout=10000)
        page.wait_for_load_state("networkidle")

        print("الضغط على Skip (Parental Control)...")
        page.get_by_role("button", name="Skip").first.click(timeout=10000)
        page.wait_for_load_state("networkidle")

        print("تمت العملية بنجاح! 🎉")
        browser.close()

if __name__ == "__main__":
    main()
