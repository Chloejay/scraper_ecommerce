import io
import time
import base64
import selenium
import numpy as np
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from chaojiying import ChaojiyingClient
# 这个需要有图片识别,OCR的基础
import configparser


class bilibili:
    def __init__(self):
        self.login_url= 'https://passport.bilibili.com/login'
        self.browser= webdriver.Firefox(executable_path="/Users/chloeji/geckodriver")
        self.driver_wait= WebDriverWait(self.browser, 30)
        """
        超级鹰的用户名、密码以及软件 ID
        """
        config = configparser.ConfigParser() 
        config.read("config.ini")
        CHAOJIYING_CONFIG= "chaojiying_login"
        CHAOJIYING_USERNAME_ = config.get(CHAOJIYING_CONFIG, "CHAOJIYING_USERNAME")
        CHAOJIYING_PASSWORD_ = config.get(CHAOJIYING_CONFIG, "CHAOJIYING_PASSWORD")
        CHAOJIYING_SOFT_ID_  = config.get(CHAOJIYING_CONFIG, "CHAOJIYING_SOFT_ID")
        self.CHAOJIYING_KIND = config.get(CHAOJIYING_CONFIG, "CHAOJIYING_KIND")
        self.chaojiying = ChaojiyingClient(CHAOJIYING_USERNAME_, CHAOJIYING_PASSWORD_, CHAOJIYING_SOFT_ID_)
        
    def send_infos(self, username, password):
        self.browser.get(self.login_url)
        username_sender= self.driver_wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='login-username']")))
        username_sender.send_keys(username)
        password_sender= self.driver_wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='login-passwd']")))
        password_sender.send_keys(password)

    def get_chapcha_button(self):
        button= self.driver_wait.until(EC.presence_of_element_located((By.XPATH, '//a[@class="btn btn-login"]')))
        print(button.text)
        time.sleep(3)
        return button 

    def get_chapcha_elements(self):
        self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_item_img')))
        element= self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME,'geetest_item_img')))
        print('成功获取验证码节点')

        return element 

    def get_chapcha_pos(self):
        element= self.get_chapcha_elements()
        time.sleep(2)
        location= element.location 
        print(location)
        size= element.size 
        print(size)
        top, buttom, left, right= \
            location["y"]+40, \
                location["y"] + size["height"]+40, \
                    location["x"], \
                        location["x"] + size["width"]

        return top, buttom, left, right 

    def get_screenshoot(self):
        # http://allselenium.info/taking-screenshot-using-python-selenium-webdriver/
        screenshoot= self.browser.get_screenshot_as_png()
        screenshoot= Image.open(io.BytesIO(screenshoot))
        time.sleep(2)
        screenshoot.save("screenshoot.png")

        return screenshoot 


    def get_chapcha_image(self, name= "chapcha.png"):
        top, buttom, left, right= self.get_chapcha_pos()
        print(f"验证码位置：{top, buttom, left, right}")

        screenshoot = self.get_screenshoot() 
        chapcha= screenshoot.crop((left, top, right, buttom))
        chapcha.save(name)

        return chapcha 

    def get_points(self, chapcha_result):
        groups= chapcha_result.get("pic_str").split("|")
        locations= [[int(number) for number in group.split(",")] for group in groups]
        return locations 

    def touch_click_words(self, locations):
        for location in locations:
            print(location)
            ActionChains(self.browser).move_to_element_with_offset(self.get_chapcha_elements(),\
                location[0], \
                    location[1]).\
                        click().\
                            perform()
            time.sleep(3)

    def touch_click_verify(self):
        button= self.driver_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "")))
        button.click()

    def login(self):
        submit= self.driver_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "")))
        submit.click()
        time.sleep(10)
        print("登录成功。")

    def crack(self, user, pswd):
        self.send_infos(user, pswd)
        button= self.get_chapcha_button() 
        button.click() 
        # 开始识别码
        image= self.get_chapcha_image()
        bytes_array= io.BytesIO()
        image.save(bytes_array, "PNG")

        result= self.chaojiying.PostPic(bytes_array.getvalue(), self.CHAOJIYING_KIND)
        print(result)

        locations= self.get_points(result)
        self.touch_click_words(locations)
        self.touch_click_verify() 
        time.sleep(10)
        try:
            success= self.browser.driver_wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h2"), "登录成功"))
            print(success)
        except Exception as e:
            print(e)
            



if __name__ == '__main__':
    username= "chloejiy"
    password= "pswd12345678"
    bilibili().crack(username, password)