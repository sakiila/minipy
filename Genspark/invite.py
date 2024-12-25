from time import sleep
from playwright.sync_api import sync_playwright
import re
import requests
import json
import random

# 邮箱系统 域名
myemail = ""
# 自己的邀请链接
invitelink = "https://www.genspark.ai/invite?invite_code=ZDEyNjJhZjlMYzhhZkxlY2Y0TGVjYThMYjhiNDgyMzBhZDQx"

# 注册密码
password = ""

def web():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False,proxy={'server': 'socks5://127.0.0.1:10808'})
        page1 = browser.new_page()
        page1.goto(myemail)
        sleep(5)
        page1.wait_for_selector('i.mail.icon.copyable')
        email_element = page1.locator('i.mail.icon.copyable')
        email = email_element.get_attribute('data-clipboard-text')
        print(email)
        page2 = browser.new_page()
        page2.goto(invitelink)
        sleep(5)
        page2.wait_for_selector('a:has-text("是的，我同意")', timeout=5000)
        page2.click('a:has-text("是的，我同意")')
        print("成功点击同意按钮")
        sleep(5)
        button = page2.locator('button.row4_button.invite_page_content_button')
        button.click()
        page2.wait_for_load_state('networkidle')
        login_button = page2.locator('button#loginWithEmailWrapper')
        login_button.click()
        page2.wait_for_load_state('networkidle')
        print("点击领取会员")
        signup_link = page2.locator('#createAccount')
        signup_link.wait_for(state='visible')
        assert "Sign up now" in signup_link.inner_text()
        with page2.expect_navigation(wait_until='networkidle'):
            signup_link.click()
        print(f"当前页面 URL: {page2.url}")
        email_input = page2.locator('#email')
        email_input.fill(email)
        actual_value = email_input.input_value()
        assert actual_value == email, f"输入验证失败: 期望 {email}, 实际 {actual_value}"
        print("邮箱输入成功")
        send_code_button = page2.locator('button#emailVerificationControl_but_send_code')
        send_code_button.click()
        page1.bring_to_front()
        while True:
            sleep(2)
            ss = page1.content()
            if "Microsoft on behalf" in ss:
                email_row = page1.locator("tr", has_text="Microsoft on behalf of Genspark")
                email_row.click()
                if "Your code is: " in ss:
                    pattern = r"Your code is: (\d{6})"
                    match = re.search(pattern, ss)
                    if match:
                        code = match.group(1)
                        print(f"成功提取验证码: {code}")
                    else:
                        print("未找到验证码")
                    break

        if code:
            page2.bring_to_front()
            code_input = page2.locator('#emailVerificationCode')
            code_input.fill(code)
            verify_button = page2.locator('button#emailVerificationControl_but_verify_code')
            verify_button.click()
            page2.wait_for_load_state('networkidle')
            page2.wait_for_timeout(2000)
            print("验证码验证按钮点击成功")
            newPassword_input = page2.locator('#newPassword')
            reenterPassword_input = page2.locator('#reenterPassword')
            page2.wait_for_selector('#newPassword:not([disabled])', timeout=10000)
            # 输入密码
            newPassword_input.fill(password)
            reenterPassword_input.fill(password)
            create_button = page2.locator('button#continue[type="submit"]')
            with page2.expect_navigation(wait_until='networkidle'):  # 等待页面跳转
                create_button.click()
                print("点击注册成功")
            page2.wait_for_load_state('networkidle')

            # 电话随机
            prefix = "175548022"
            random_suffix = str(random.randint(0, 99)).zfill(2)
            phone_number = prefix + random_suffix
            # 定输入电话
            phone_input = page2.locator('input.vti__input')
            phone_input.fill(f"+49 {phone_number}")
            # 响应
            def handle_response(response):
                return "https://www.genspark.ai/api/phone/sms_send_verification" in response.url
            with page2.expect_response(handle_response) as response_info:
                page2.click('button.row4_button:has-text("获取验证码")')
            response = response_info.value
            if response.ok:
                data = response.json()
                print(f"手机验证码：{data['code']}")
            # 码
            valuecode = data['code']

            # 输入验证码
            verification_code = page2.locator('#verification_code')
            verification_code.fill(valuecode)
            # 点击领取
            page2.wait_for_selector("button.row4_button", state="visible", timeout=5000)
            sleep(2)
            page2.click("button.row4_button:has-text('领取会员权益')")
            print("领取成功！结束啦！！！！！！！！执行保存。")
            page2.wait_for_timeout(1000)
            with open(r'C:\Users\Hebin\Desktop\genspark账号.txt', 'a', encoding='utf-8') as file:
                ndata = f"{email}——{password}"
                file.write('\n' + ndata)
            print(f"保存账号：{ndata}")
            browser.close()


while True:
    sleep(20)
    web()


