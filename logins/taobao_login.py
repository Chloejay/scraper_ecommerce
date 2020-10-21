import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep, time
from datetime import datetime
import logging
import configparser
from loguru import logger
from retrying import retry
import arrow


class TB_Spider:
    def __init__(self, user, pswd, **kw):
        self.user = user
        self.pswd = pswd
        driver_path = "/Users/chloeji/geckodriver"
        self.url = "http://www.taobao.com"
        self.login_url = 'https://login.taobao.com/member/login.jhtml'
        self.browser = webdriver.Firefox(executable_path=driver_path)
        self.wait = WebDriverWait(self.browser, 60)
        # logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # self.logger= logging.getLogger(__name__)

    def login(self, **kw):
        self.browser.get(self.url)
        try:
            button = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 'h')))
            button.click()
            sleep(2)
            username_sender = self.wait.until(
                EC.presence_of_element_located((By.ID, 'fm-login-id')))
            username_sender.send_keys(self.user)
            sleep(1)
            password_sender = self.wait.until(
                EC.presence_of_element_located((By.ID, 'fm-login-password')))
            password_sender.send_keys(self.pswd)
            sleep(2)

            # 检查滑动验证码
            try:
                slider = self.browser.find_element_by_xpath(
                    "//span[contains(@class, 'btn_slide')]")
                if slider.is_displayed():
                    ActionChains(browser).click_and_hold(
                        on_element=slider).perform()
                    ActionChains(browser).move_by_offset(
                        xoffset=258, yoffset=0).perform()
                    ActionChains(browser).pause(0.5).release().perform()
            except Exception as e:
                logger.error(e)
                pass
            login_button = self.wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, 'password-login')))
            login_button.click()
        except Exception as e:
            logger.error(e)
            pass
        finally:
            logger.info(
                f"成功登录。\n登录时间: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
            # self.browser.quit()


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini")
    user = config.get("login_info", "user")
    pswd = config.get("login_info", "password")
    TB_Spider(user, pswd).login()