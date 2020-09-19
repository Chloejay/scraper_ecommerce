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

from multiprocessing import Process, Queue 
from requests.exceptions import ReadTimeout

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
    def __init__(self, file_path: str)-> None:
        self.file_path = file_path

    def read_excel(self)->pd.DataFrame:
        return pd.read_excel(self.file_path) 

    def check(self, row: List[str])->str:
        if "taobao" in row:
            return "taobao"
        elif "tmall" in row:
            return "tmall"
        return "others"

    def extract_item_id(self, file: pd.DataFrame)-> pd.DataFrame:
        file["channel"] = ""
        file["item_id"] = ""
        
        file["channel"]= file.loc[:,"商品链接"].apply(self.check)
        list_ = file.loc[:,"商品链接"].apply(lambda row: row.split("="))
        for i in range(len(list_)):
            if len(list_[i]) >2:
                file["item_id"][i] = list_[i][2].split("&")[0]
            else:
                file["item_id"][i] = list_[i][-1]
                
        return file


class Parse_TB:
    def __init__(self, 
                 from_data: Dict[str, str], 
                 user_agent: str, 
                 login_url:str, 
                 base_url:str,
                 ip: str)-> None:
        
    # IP been blocked
        self._from_data = from_data
        self.user_agent= user_agent
        self.login_url = login_url
        self.base_url= base_url
        self.ip = ip
        self.proxies = {
            'http': 'http://' + self.ip,
            'https': 'https://' + self.ip
            }
        self.content_type ="application/x-www-form-urlencoded"
        self.res = requests.Session()
        self.cookies_text = "cookies.txt"
        self.ajax_refere= "https://detailskip.taobao.com"
    
    def _get_cookie(self)-> Optional[Text]:
        if self._verify_cookies():
            return True
        try:
            response = self.res.post(self.login_url, 
                                     data = self._from_data, 
                                     proxies= self.proxies,
                                     )
            response.raise_for_status()
            redirect = response.json()["needcode"]

        except Exception as e:
            pprint(f"Failed to scrap data, error : {e}")
            raise e
        
        if not redirect:
            pprint("Succeed getting cookies, to save to {}".format(self.cookies_text))
            self._save_cookies()
        else:
            raise RuntimeError("User login FAILED! Error:{}".format(response.text))
    
    # Check if have cookies and if expired
    def _verify_cookies(self)->bool:
        if not os.path.exists(self.cookies_text):
            return False
        # res.cookies = self._load_cookies()
        try:
            self._is_login()
        except Exception as e:
            os.remove(self.cookies_text)
            pprint("Deleted EXPIRED cookies!")
            return False
        pprint("Login Successfully!")
        return True
    
    def _is_login(self)-> bool:
        response= self.res.get(self.login_url, self.ip)
        time.sleep(5)
        username = re.search(r'<input id="mtb-nickname" type="hidden" value="(.*?)"/>', response.text)
        if username:
            pprint(f"UserName: {username.group(1)}")
            return True
        
        raise RuntimeError("Login Failed!")

    def _save_cookies(self):
        # deserialization 反序列化
        cookies_dict = requests.utils.dict_from_cookiejar(self.res.cookies)
        with open(self.cookies_text, "w+", encoding="utf-8") as output:
            json.dump(cookies_dict, output)
            
    # def _load_cookies(self):
        # with open(self.cookies_text, "r+", encoding="utf-8") as input:
            # cookies_dict = json.load(input)
            # serialization 序列化
            # cookies = requests.utils.cookiejar_from_dict(input)
            # return cookies

    def get_static_content(self, file: List[str], timeout: int)->Tuple[str, Union[int,float, Any],int]:
        """
        商品标题, 划线价, 累计评论
        """
        self._get_cookie()
        
        商品标题 = list()
        划线价 = list()
        url= list()
        for i in range(len(file)):
            req = self.res.get(file[i],
                               headers= {'user-agent': self.user_agent,
                                         'Content-Type':self.content_type}, 
                               proxies= self.proxies
                                        )
            time.sleep(timeout)
            HTML_PARSER = 'html.parser'
            soup = bs(req.text, HTML_PARSER)
            pprint(soup)
            try:
                title = soup.find("h3", class_="tb-main-title").get_text().strip()
                line_through_price = soup.find("em", class_="tb-rmb-num").get_text()
                商品标题.append(title)
                划线价.append(line_through_price)
                url.append(file[i])
                
            except Exception as e:
                pprint(str(e))
                title = "-"
                line_through_price = "-"

        return pd.DataFrame({"商品链接": url, "商品标题":商品标题, "划线价": 划线价})

    # parse
    def get_static_content_update(self, url: List[str], wait_time: int)->pd.DataFrame:
        self._get_cookie()
        商品标题 = list()
        划线价 = list()
        累计评论= list()
        url = list()
        try:
            for i in range(len(url)):
                browser.get(url[i],
                            headers= {
                                'user-agent': self.user_agent,
                                'Content-Type':self.content_type}, 
                            proxies= self.proxies,)
                
                browser.implicitly_wait(wait_time)
                meta = browser.find_element_by_xpath("/html/head/meta[9]")
                meta_content = meta.get_attribute("content")
                title = browser.find_element_by_class_name('tb-main-title').text
                line_through_price = browser.find_element_by_id('J_StrPrice').find_element_by_class_name('tb-rmb-num').text
                comment_count = browser.find_element_by_id("J_RateCounter").text

                商品标题.append(title)
                划线价.append(line_through_price)
                累计评论.append(comment_count)
                url.append(url[i])
            
        except Exception as e:
            pprint(str(e))
            pass

        return pd.DataFrame({"商品链接": url, "商品标题":商品标题, "划线价": 划线价, "累计评论": 累计评论})

               
    #parse https://detailskip.taobao.com/ for ajax-rendered page 加载渲染页面
    def get_ajax_content(self, file:pd.DataFrame, timeout: int)->List:
        self._get_cookie()
        total_res = list()
        
        for i in range(len(file.index))[:]:
            ajax_url = "https://detailskip.taobao.com/service/getData/1/p1/item/detail/sib.htm?itemId={}&modules=dynStock,qrcode,viewer,\
                price,duty,xmpPromotion,delivery,activity,fqg,zjys,couponActivity,soldQuantity,page,originalPrice,tradeContract"\
                    .format(file["item_id"][i])
            try:
                req = self.res.get(ajax_url,
                                   headers= {
                                       'user-agent': self.user_agent,
                                       'Content-Type':self.content_type,
                                       "refere":self.ajax_refere},
                                   verify= False, 
                                   proxies= self.proxies,)
                time.sleep(timeout)
                total_res.append(req.text) #TODO
                return total_res
            
            except ReadTimeout:
                pprint("Timeout!")
            

# generate remote servers
class Proxy:
    def __init__(self):
        pass

    @staticmethod
    def get_proxy(proxy_url):
        html = requests.get(proxy_url).text
        proxies_= list()
        if html:
            result = json.loads(html)
            proxies = result.get('RESULT')
            for proxy in proxies:
                ip = proxy.get('ip') + ':' + proxy.get('port')
                proxies_.append(ip)
                
        return proxies_


# TODO for JD
class Parse_TM:
    def __init__(self):
        pass
    
            
if __name__== "__main__":
    
    df_instance = DataSource(DATA_SOURCE_PATH)
    excel= df_instance.extract_item_id(df_instance.read_excel())
    tb_excel= excel[excel["channel"] == "taobao"]
    ajax_url= "https://detailskip.taobao.com/service/getData/1/p1/item/detail/sib.htm?itemId={}&modules=price,xmpPromotion,viewer,price,duty,xmpPromotion,activity,fqg,zjys,couponActivity,soldQuantity,page,originalPrice".format(tb_excel["item_id"])

    proxy_ips = Proxy().get_proxy(proxy_url)
    ip = random.choice(proxy_ips)
    pprint(f"Get IP: {ip}")
    
    tb_parser= Parse_TB(from_data, USER_AGENT, LOGIN_URL, BASE_URL, ip)
    test= tb_parser.get_static_content(tb_excel.loc[:,"商品链接"][:12].values, TIMEOUT)
    test.to_csv("static_fields.csv", index= False)

    #get ajax =>"rgv587_flag":"sm" blocked error freq is high, esp with few remote proxies.
    # get_ajax= tb_parser.get_ajax_content(tb_excel, TIMEOUT)
    # print(get_ajax)