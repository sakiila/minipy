import re
import json
import time
import random
import requests
import phonenumbers
from faker import Faker
from phonenumbers import PhoneNumberFormat
from playwright.sync_api import sync_playwright

invite_url = "https://www.genspark.ai/invite?invite_code=ZDEyNjJhZjlMYzhhZkxlY2Y0TGVjYThMYjhiNDgyMzBhZDQx"

domain = "https://api.mail.cx/api/v1"

def generate_valid_phone_number(country_code):
    try:
        region_code = phonenumbers.region_code_for_country_code(int(country_code.replace('+', '')))
        example_number = phonenumbers.example_number_for_type(region_code, phonenumbers.PhoneNumberType.MOBILE)
        if not example_number:
            raise ValueError(f"No example mobile number found for country code {country_code}")
        formatted_number = phonenumbers.format_number(example_number, PhoneNumberFormat.NATIONAL)
        digits_only = ''.join(filter(str.isdigit, formatted_number))
        prefix = digits_only[:len(digits_only) - 4]
        remaining_digits = ''.join(str(random.randint(0, 9)) for _ in range(len(digits_only) - len(prefix)))
        valid_phone_number = prefix + remaining_digits
        return valid_phone_number
    except Exception as e:
        raise ValueError(f'Error generating valid phone number for country code {country_code}: {str(e)}')

def generate_name():
    fake = Faker('en_US')
    while True:
        name = fake.name().replace(' ', '_')
        if len(name) <= 10:
            return name

def getAuth():
    url = domain + "/auth/authorize_token"
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer undefined',
    }
    response = requests.post(url, headers=headers)
    return str(response.json())

def getMailAddress():
    root_mail = ["nqmo.com"]
    return generate_name() + '@' + random.choice(root_mail)

def getMailId(address, auth):
    url = domain + f"/mailbox/{address}"
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {auth}',
    }
    response = requests.get(url, headers=headers)
    body = response.json()
    return body[0]['id'] if len(body) and len(body[0]['id']) > 0 else None

def register(invite_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            java_script_enabled=True
        )
        page = context.new_page()
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'language', {
                get: () => 'zh-CN'
            });
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32'
            });
            Object.defineProperty(navigator, 'userAgent', {
                get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
            });
        """)
        page.goto(invite_url, wait_until="networkidle", timeout=100000000)
        print("[+]打开邀请链接")
        page.get_by_text("领取会员权益").click()
        page.get_by_text("Login with email").click()
        page.get_by_text("Sign up now").click()
        print("[+]开始注册")
        auth = getAuth()
        address = getMailAddress()
        email = address
        page.fill('xpath=//*[@id="email"]', email)
        print("[+]邮箱地址: " + email)
        page.get_by_text("Send verification code").click()
        page.wait_for_selector('xpath=//*[@id="emailVerificationCode"]')
        id_ = None
        while id_ is None:
            id_ = getMailId(address, auth)
        url = domain + f'/mailbox/{address}/{id_}'
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {auth}',
        }
        body = requests.get(url, headers=headers).json()["body"]["text"]
        pattern = r"Your code is: \s*(\d+)\s*"
        match = re.search(pattern, body)
        if match:
            verification_code = match.group(1)
            print("[+]验证码: " + verification_code)
        page.fill('xpath=//*[@id="emailVerificationCode"]', verification_code)
        page.get_by_text("Verify code").click()
        page.fill('xpath=//*[@id="newPassword"]', "ZXCvbnm0987###")
        page.fill('xpath=//*[@id="reenterPassword"]', "ZXCvbnm0987###")
        page.get_by_text("Create").click()
        print("[+]注册成功，开始填写手机号")
        time.sleep(10)
        country_code = page.locator('xpath=//*[@id="__nuxt"]/div/div/div/div[3]/div[2]/div[2]/div[1]/div/div[1]/div/div/span/span[2]').text_content().replace(" ", "")
        print("[+]国家代码: " + country_code)
        phone_number = generate_valid_phone_number(country_code)
        print("[+]手机号: " + phone_number)
        api_country_code = country_code.replace("+", "")
        response = page.evaluate("""
            async ({ url, headers, payload }) => {
                const response = await fetch(url, {
                    method: "POST",
                    headers: headers,
                    body: JSON.stringify(payload)  // 自动将对象转换为 JSON 字符串
                });
                const responseText = await response.text();
                return {
                    status: response.status,
                    body: responseText
                };
            }
        """, {
            "url": "https://www.genspark.ai/api/phone/sms_send_verification",
            "headers": {
                "Content-Type": "application/json"
            },
            "payload": {
                "country_code": api_country_code,
                "number_without_country_code": phone_number
            }
        })
        response_body = response["body"]
        response_dict = json.loads(response_body)
        verify_code = response_dict.get("code")
        print("[+]验证码: " + verify_code)
        page.fill('xpath=//*[@id="__nuxt"]/div/div/div/div[3]/div[2]/div[2]/div[1]/div/div[1]/div/input', phone_number)
        page.fill('xpath=//*[@id="verification_code"]', verify_code)
        page.get_by_text("领取会员权益").click()
        print("[+]注册完成")
        time.sleep(10)

if __name__ == "__main__":
    for i in range(20):
        register(invite_url)