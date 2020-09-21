import pandas as pd 
import re
import requests
from bs4 import BeautifulSoup as bs
import os 
from pprint import pprint
from typing import List, Any, Dict, Text, Union, Optional


class DataSource:
    def __init__(self, url: str, headers:Dict[str, str])-> None:
        self.url= url 
        self.headers= headers
    
    def get_html(self)-> Text:
        try:
            req= requests.get(self.url, headers= self.headers)
            if req.status_code== 200:
                html = req.text
                soup = bs(html, "html.parser")
            return soup 
        except Exception as e:
            pprint(e)
            
class Parser:
    def __init__(self, soup: Text)-> None:
        self.soup = soup
        self.table =self.tranform_dict()
    
    def get_top_left_content(self)-> pd.DataFrame:
        average_rating= list()
        total_votes= list()
        
        for distillery in self.soup.find_all(id="distillery-average"):
            average_rating.append(distillery.find(id="distillery-average-num").text)
            total_votes.append(distillery.find(id="distillery-votes").text.strip())
        
        return pd.DataFrame({"平均分": average_rating, "投票数":total_votes})


    def get_top_right_content(self)->pd.DataFrame:
        top5_tags= list()
        top5_rates= list()

        for items in self.soup.find_all('li', {'class': 'small-top5-item'}):
            for tag in items.find_all('a'):
                for rate in items.find_all(class_="small-top5-rating"):
                    top5_tags.append(tag.text)
                    top5_rates.append(rate.text)
        return pd.DataFrame({"top5_rates": top5_rates, "top5_tags": top5_tags})
    
    # get table column names 
    def get_columns_name(self)->List[str]:
        columns= list()
        for sort in self.soup.find_all("tr"):
           for i in sort.find_all(class_="sort"):
               columns.append(i.text.strip())
        return columns

    def parse(self,row)->Union[List, Any]:
        if row:
            return row
        else:
            return "-"
        
    def get_data(self)->List:
        data = []
        table=self.soup.find("table")
        tbody = table.find('tbody')
        rows = tbody.find_all('tr')
        for row in rows:
            cols=row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append(list(map(self.parse, cols)))
        return data

    def tranform_dict(self)->Dict:
        table= list() 
        for k,x in enumerate(self.get_data()):
            if len(x) <1:
                table.append({"index": k, "value": "-"})
            table.append({"index":k, "value":x})
        return table


    def parse_main_table(self)->pd.DataFrame:
        name= list()
        started_age=list()
        strength_list=list()
        size_list=list()
        bottled_list=list()
        casknumber_list=list()
        rating_list=list()
        versions_list=list()
        shoplinks_list=list()
        
        for i in range(len(self.table)):
            if len(self.table[i]["value"])>2:
                try:
                    name.append(self.table[i]["value"][2])
                    started_age.append(self.table[i]["value"][3])
                    strength_list.append(self.table[i]["value"][4])
                    size_list.append(self.table[i]["value"][5])
                    bottled_list.append(self.table[i]["value"][6])
                    casknumber_list.append(self.table[i]["value"][7])
                    rating_list.append(self.table[i]["value"][8])
                    versions_list.append(self.table[i]["value"][9])
                    shoplinks_list.append(self.table[i]["value"][10])
                
                except ValueError as e:
                    pass 
            else:
                name.append(self.table[i]["value"][0])
                started_age.append(" ")
                strength_list.append(" ")
                size_list.append(" ")
                bottled_list.append(" ")
                casknumber_list.append(" ")
                rating_list.append(" ")
                versions_list.append(" ")
                shoplinks_list.append(" ")

#     return name, started_age, strength_list, size_list, bottled_list, casknumber_list, rating_list, versions_list, shoplinks_list
        return pd.DataFrame({"名称":name, 
                             "规定的年份": started_age,
                             "酒精度": strength_list, 
                             "容量": size_list, 
                             "装瓶": bottled_list, 
                             "桶号": casknumber_list, 
                             "评分": rating_list, 
                             "版本":versions_list, 
                             "商店链接": shoplinks_list})
