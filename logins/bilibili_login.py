# --coding: UTF-8 --
"""
__author__: "Chloe Ji" ji.jie@edhec.com
Update Date: 2020-10-19
"""

import io
from time import sleep, time
from PIL import Image
import configparser
from pprint import pprint
from loguru import logger
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import MoveTargetOutOfBoundsException
from chaojiying import ChaojiyingClient
# 添加参数使得每次不需要打开浏览器就可以完成所有的爬取工作
from selenium.webdriver.firefox.options import Options
import traceback


config = configparser.ConfigParser()
config.read("config.ini")


class Bilibili:
    def __init__(self):
        self.login_url = "https://passport.bilibili.com/login"
        caps = DesiredCapabilities().FIREFOX
        firefox_options = Options()
        firefox_options.headless = True
        self.browser = webdriver.Firefox(
            executable_path="/Users/chloeji/geckodriver",
            capabilities=caps,
            options=firefox_options)
        self.driver_wait = WebDriverWait(self.browser, 60)

        """
        设置超级鹰的用户名、密码以及软件 ID
        """
        CHAOJIYING_CONFIG = "chaojiying_login"
        CHAOJIYING_USERNAME_ = config.get(
            CHAOJIYING_CONFIG, "CHAOJIYING_USERNAME")
        CHAOJIYING_PASSWORD_ = config.get(
            CHAOJIYING_CONFIG, "CHAOJIYING_PASSWORD")
        CHAOJIYING_SOFT_ID_ = config.get(
            CHAOJIYING_CONFIG, "CHAOJIYING_SOFT_ID")
        self.CHAOJIYING_KIND = config.get(CHAOJIYING_CONFIG, "CHAOJIYING_KIND")
        self.chaojiying = ChaojiyingClient(
            CHAOJIYING_USERNAME_,
            CHAOJIYING_PASSWORD_,
            CHAOJIYING_SOFT_ID_)

    def send_infos(self, username, password):
        self.browser.get(self.login_url)
        username_sender = self.driver_wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[@id='login-username']")))
        username_sender.send_keys(username)
        password_sender = self.driver_wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[@id='login-passwd']")))
        password_sender.send_keys(password)

    def get_verify_button(self):
        button = self.driver_wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[@class='btn btn-login']")))
        pprint(button.text)
        sleep(3)
        return button

    def get_verify_elements(self):
        self.driver_wait.until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "geetest_item_img")))
        sleep(2)
        element = self.driver_wait.until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "geetest_table_box")))
        logger.info("成功获取验证码节点。")
        return element

    def get_verify_pos(self):
        element = self.get_verify_elements()
        sleep(2)
        location = element.location
        print(location)
        size = element.size
        print(size)
        top, buttom, left, right = \
            location["y"] * 2, \
            (location["y"] + size["height"]) * 2, \
            location["x"] * 2, \
            (location["x"] + size["width"]) * 2

        return top, buttom, left, right

    def get_screenshoot(self):
        # http://allselenium.info/taking-screenshot-using-python-selenium-webdriver/
        screenshoot = self.browser.get_screenshot_as_png()
        screenshoot = Image.open(io.BytesIO(screenshoot))
        sleep(5)
        screenshoot.save("screenshoot.png")

        return screenshoot

    def get_verify_image(self, name="need_to_verified.png"):
        top, buttom, left, right = self.get_verify_pos()
        logger.info(f"验证码位置：{top, buttom, left, right}")

        screenshoot = self.get_screenshoot()
        verification_area = screenshoot.crop((left, top, right, buttom))
        verification_area.save(name)

        return verification_area

    def get_points(self, verify_result):
        groups = verify_result.get("pic_str").split("|")
        try:
            locations = [[int(number) for number in group.split(",")]
                         for group in groups]
        except ValueError:
            locations = [[int(float(number))
                          for number in group.split(",")] for group in groups]
        return locations

# geckodriver browser issue with viewpoint
    def touch_click_words(self, locations):
        for location in locations:
            print(location)
            X_OFFSET = location[0]
            Y_OFFSET = location[1]
            try:
                ActionChains(self.browser).\
                    move_to_element_with_offset(self.get_verify_elements(),
                                                X_OFFSET, Y_OFFSET).\
                    click().\
                    perform()
                sleep(3)
            except MoveTargetOutOfBoundsException:
                self.browser.execute_script(
                    'window.scrollTo(0, " + str(self.get_verify_elements())");')
            except Exception:
                pprint(traceback.format_exc())

    def touch_click_verify(self):
        button = self.driver_wait.until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, "geetest_commit")))
        button.click()

    def login(self):
        submit = self.driver_wait.until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, "btn btn-login")))
        submit.click()
        sleep(10)
        logger.info("登录成功。")

    def crack(self, user, pswd):
        # self.browser.execute_script("document.body.style.transform='scale(0.9)';")
        self.browser.set_window_size(1024, 768)
        self.send_infos(user, pswd)
        button = self.get_verify_button()
        button.click()
        # 开始识别码
        image = self.get_verify_image()
        bytes_array = io.BytesIO()
        image.save(bytes_array, "PNG")

        sleep(10)
        result = self.chaojiying.PostPic(
            bytes_array.getvalue(), self.CHAOJIYING_KIND)
        pprint(result)

        locations = self.get_points(result)
        self.touch_click_words(locations)
        self.touch_click_verify()
        sleep(3)
        try:
            success = self.driver_wait.until(EC.text_to_be_present_in_element(
                (By.CLASS_NAME, "bilifont bili-icon_dingdao_zhuzhan"), "主站"))
            pprint(success)
        except Exception as e:
            logger.warn("登录失败。", e)
        finally:
            self.browser.quit()


if __name__ == "__main__":
    bilibili_login = "login_info"
    user = config.get(bilibili_login, "user")
    pswd = config.get(bilibili_login, "password")
    Bilibili().crack(user, pswd)
