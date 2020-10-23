# config
from configparser import ConfigParser

config = ConfigParser()
config.read("../config/config.ini")

LOGIN_INI = "login_info"
user = config.get(LOGIN_INI, "user")
pswd = config.get(LOGIN_INI, "password")

ua = config.get("header_info", "ua")
# WHISKY_COOKIES = config.get("header_info", "WHISKY_COOKIES")
# WHISKY_COOKIES2 = config.get("header_info", "WHISKY_COOKIES2")

CHAOJIYING_CONFIG = "chaojiying_login"
CHAOJIYING_USERNAME_ = config.get(
    CHAOJIYING_CONFIG, "CHAOJIYING_USERNAME")
CHAOJIYING_PASSWORD_ = config.get(
    CHAOJIYING_CONFIG, "CHAOJIYING_PASSWORD")
CHAOJIYING_SOFT_ID_ = config.get(
    CHAOJIYING_CONFIG, "CHAOJIYING_SOFT_ID")
CHAOJIYING_KIND = config.get(CHAOJIYING_CONFIG, "CHAOJIYING_KIND")

# FILE_PATH
DATA_SOURCE_PATH = "source/爬取链接.xlsx"
BASE_URL = 'https://item.taobao.com/item.htm'
LOGIN_URL = 'https://login.taobao.com/member/request_nick_check.do?_input_charset=utf-8'

# Time config
TIMEOUT = 9
WAIT_TIME = 10
SLEEP = 5

# headers, UA=> to monitor the web engine to deal with ajax data;
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
ACCEPT = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"

from_data = {
    "loginId": user,
    "password2": pswd,
    "keepLogin": "false",
    "ua": ua,
    "umidGetStatusVal": "255",
    "screenPixel": "1440x900",
    "navlanguage": "en-US",
    "navUserAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
    "navPlatform": "MacIntel",
    "appName": "taobao",
    "appEntrance": "taobao_pc",
    "_csrf_token": "PIN6AHPsVKcsqZTpW3sdk6",
    "umidToken": "94940210f70c92b572d4da58c7375087f72b3f21",
    "hsiz": "1731074d1f202a3ea2ceeb58b45f73cd",
    "bizParams": "",
    "style": "default",
    "appkey": "00000000",
    "from": "tbTop",
    "isMobile": "false",
    "lang": "zh_CN",
    "returnUrl": "https://www.taobao.com/",
    "fromSite:": "0"}

# headers = {"cookie": WHISKY_COOKIES,
#    "referer": "https://www.whiskybase.com/whiskies/brand/81362/ardbeg",
#    "user-agent": USER_AGENT}

# headers_2 = {
# "Accept": ACCEPT,
# "cookies": WHISKY_COOKIES2,
# "user-agent": USER_AGENT}
#
# set up for proxy server to prevent IP being blocked.
proxy_url = "http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=c671e46bf2ae4092bd03a8ed3566c952&orderno=YZ20209194777fbU1ls&returnType=2&count=20"