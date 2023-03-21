# -*- coding:utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By

import PySimpleGUI as sg


def login_website(email):
    option = webdriver.ChromeOptions()
    option.add_experimental_option("detach", True)
    option.add_experimental_option('useAutomationExtension', False)
    option.add_experimental_option('excludeSwitches', ['enable-automation'])

    browser = webdriver.Chrome(options=option)
    browser.maximize_window()
    browser.implicitly_wait(5)

    browser.get("https://go.moego.pet/sign_in")

    browser.find_element(By.ID, "email").send_keys(email.strip())
    browser.find_element(By.ID, "password").send_keys("")
    browser.find_element(By.XPATH, "//button[@type='submit']").click()


# login_website(sys.argv[1])


if __name__ == '__main__':
    # Define the window's contents
    layout = [[sg.Text(text='Business Email :', font='Helvetica 14')],
              [sg.Input(key='-IN-', font='Helvetica 16', tooltip='Press ENTER to login')],
              [sg.Button(key='-GO-', button_text='Login', font='Helvetica 14', bind_return_key=True)]]

    # Create the window
    window = sg.Window('MoeGo Login Tool', layout)

    # Display and interact with the Window
    event, values = window.read()

    # Finish up by removing from the screen
    window.close()

    if event == sg.WIN_CLOSED:
        pass
    elif event in ('-GO-'):
        email = values['-IN-']
        if email == None:
            pass
        login_website(email.strip())
    else:
        pass
