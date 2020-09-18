import pandas as pd 
import re
import requests
from bs4 import BeautifulSoup as bs
import time
import random
import json
import os 
import logging
import urllib
from pprint import pprint
from typing import List, Tuple, Any, Dict, Text, Union, Callable, Optional

from config import * 

# from selenium import webdriver
# from pycookiecheat import chrome_cookies
# from webdriver_manager.chrome import ChromeDriverManager
# browser = webdriver.Chrome(ChromeDriverManager().install())

import warnings
warnings.simplefilter("ignore")

logger = logging.getLogger(__name__)

#=========================
# GET DATA SOURCE FILE
#=========================

class DataSource:
    def __init__(self, file_path: str)-> pd.DataFrame:
        self.file_path = file_path

    def read_excel(self):
        return pd.read_excel(self.file_path) 

    def check(self, row: List[str])->str:
        if "taobao" in row:
            return "taobao"
        elif "tmall" in row:
            return "tmall"
        return "others"

    def extract_item_id(self, file: pd.DataFrame)-> pd.DataFrame:
        # Init the null value; 
        file["channel"] = ""
        file["item_id"] = ""
        
        file["channel"]= file["商品链接"].apply(self.check)
        
        list_ = file["商品链接"].apply(lambda row: row.split("="))
        
        for i in range(len(list_)):
            if len(list_[i]) >2:
                file["item_id"][i] = list_[i][2].split("&")[0]
            else:
                file["item_id"][i] = list_[i][-1]
                
        return file


class Parser_TB:
    def __init__(self, 
                 from_data: Dict[str, str], 
                 user_agent: str, 
                 login_url:str, 
                 base_url:str)-> None:
        
    # IP been blocked after several runs
        self._from_data = from_data
        self.login_url = login_url
        self.base_url= base_url
        self.headers = {
            'user-agent': user_agent,
            'Content-Type': 'application/x-www-form-urlencoded',
            # 'Referer':base_url,
        }
        self.res = requests.Session()
        self.cookies_text = "cookies.text"
    
    def _get_cookie(self)-> Optional[Text]:
        """
        LOGIN to get Cookies and save to local dir
        """
        if self._verify_cookies():
            return True
        try:
            response = self.res.post(self.login_url, data = self._from_data)
            response.raise_for_status()

        except Exception as e:
            print(f"Failed to scrap data, error : {e}")
            raise e

        redirect = response.json()['content']['data']['redirect']

        if redirect == True:
            print('Succeed getting cookies, to save')
            self._save_cookies()

        else:
            raise RuntimeError(f"User login FAILED! Error:{response.text}")
    
    # Check if have cookies and if expired
    def _verify_cookies(self)->bool:
        if not os.path.exists(self.cookies_text):
            return False
        res.cookies = self._load_cookies()

        try:
            self._is_login()

        except Exception as e:
            os.remove(cookie_text)
            print('Deleted EXPIRED cookies!')
            return False
        print('Login Successfully!')
        return True
    
    def _is_login(self)-> bool:
        response= res.get(self.login_url)
        username = re.search(r'<input id="mtb-nickname" type="hidden" value="(.*?)"/>', response.text)
        if username:
            print(f"UserName: {username.group(1)}")
            return True
        
        raise RuntimeError("Login Failed!")

    # Save cookies locally
    def _save_cookies(self):
        # deserialization 反序列化
        cookies_dict = requests.utils.dict_from_cookiejar(res.cookies)
        with open(cookie_text,"w+", encoding="utf-8") as output:
            json.dump(cookies_dict, output)
            
    def _load_cookies(self):
        with open(cookie_text, "r+", encoding="utf-8") as input:
            cookies_dict = json.load(input)
            # serialization 序列化
            cookies = requests.utils.cookiejar_from_dict(input)
            return cookies

    def get_static_content(self, file: pd.DataFrame)->Tuple[str, Union[int,float, Any],int]:
        """
        get_static_content for 商品标题, 划线价, 累计评论
        """
        self._get_cookie()
        
        商品标题 = list()
        划线价 = list()
        try:
            for i in range(len(file.index)):
                req= self.res.get(file["商品链接"][i], 
                                  headers= self.headers,)
                if res.status_code == 200:
                    # statics={}
                    HTML_PARSER= 'html.parser'
                    soup = bs(res.text, HTML_PARSER)
                    # res.json() #to get json

                    try:
                        title = soup.find("h3", class_="tb-main-title").get_text().strip()
                        line_through_price = soup.find("em", class_="tb-rmb-num").get_text()
                        time.sleep(9)

                    except Exception as e:
                        print(str(e))
                        title = "-"
                        line_through_price = "-"
                        

                        商品标题.append(title)
                        划线价.append(line_through_price)

                        statics["商品标题"]= soup.find("h3", class_="tb-main-title").get_text().strip()
                        statics["划线价"]= soup.find("em", class_="tb-rmb-num").get_text()
                # return statics 
            return pd.DataFrame({"商品标题":商品标题, "划线价": 划线价})

        except Exception as e:
            print(e)
            pass 

    # parse
    def get_static_comment_update(self, url: str)->pd.DataFrame:
        self._get_cookie()
        
        商品标题 = list()
        划线价 = list()
        累计评论= list()
        
        try:
            browser.get(url)
            browser.implicitly_wait(10)
            meta = browser.find_element_by_xpath("/html/head/meta[9]")
            meta_content = meta.get_attribute("content")
            title = browser.find_element_by_class_name('tb-main-title').text
            line_through_price = browser.find_element_by_id('J_StrPrice').find_element_by_class_name('tb-rmb-num').text
            comment_count = browser.find_element_by_id("J_RateCounter").text

            商品标题.append(title)
            划线价.append(line_through_price)
            累计评论.append(comment_count)
            
        except Exception as e:
            pprint(str(e))
            pass

        return pd.DataFrame({"商品标题":商品标题, "划线价": 划线价, "累计评论": 累计评论})
                
    #parser https://detailskip.taobao.com/ for ajax rendered page 加载渲染页面
    def get_ajax_content(self, file:pd.DataFrame)->List:
        self._get_cookie()
        total_res = list()
        
        # Load taobao url
        for i in range(len(file.index)):
            ajax_url = "https://detailskip.taobao.com/service/getData/1/p1/item/detail/sib.htm?itemId={}&modules=dynStock,qrcode,viewer,\
                price,duty,xmpPromotion,delivery,activity,fqg,zjys,couponActivity,soldQuantity,page,originalPrice,tradeContract"\
                    .format(df["item_id"][i])

            req = res.get(ajax_url, headers= self.headers,)
            total_res.append(req) #TODO
            print(total_res)


# TODO for JD
class Parser_TM:
    def __init__(self):
        pass

            
if __name__== "__main__":
    base_url= 'https://item.taobao.com/item.htm'
    login_url = 'https://login.taobao.com/member/request_nick_check.do?_input_charset=utf-8'
    
    from_data= {
        "loginId": login_id, 
        "password2": password_,
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
        "fromSite:": "0"
    }
    
    df_instance= DataSource("爬取链接.xlsx")
    excel = df_instance.read_excel()
    excel= df_instance.extract_item_id(excel)
    tb_excel= excel[excel["channel"] == "taobao"]
    ajax_url= "https://detailskip.taobao.com/service/getData/1/p1/item/detail/sib.htm?itemId={}&modules=price,xmpPromotion,viewer,price,duty,xmpPromotion,activity,fqg,zjys,couponActivity,soldQuantity,page,originalPrice".format(excel["item_id"])
    # user_agent= "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"

    ua_list = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.991",
           "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36 OPR/42.0.2393.94",
           "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36 OPR/47.0.2631.39",
           "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
           "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
           "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
           "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) Gecko/20100101 Firefox/54.0",
           "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) Gecko/20100101 Firefox/54.0",
           "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) Gecko/20100101 Firefox/56.0",
           "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) like Gecko"]
    user_agent = random.choice(ua_list)
    # referer= "https://item.taobao.com/item.htm"
    
    with open("cookies.txt") as f:
        cookies= f.read()
    tb_parser= Parser_TB(from_data, user_agent, login_url, base_url)
    test= tb_parser.get_static_content(tb_excel["商品链接"].values)
    test.to_csv("static_fields.csv", index= False)