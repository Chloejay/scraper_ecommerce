from scrap_whisky import * 
from config import * 


class Parser_graph:
    def __init__(self, soup: Text)-> None:
        self.soup = soup

    def get_column(self):
        index_= list()
    
        for table in self.soup.find_all(class_="index-performance"):
            for index in table.find_all('th', class_="side-header"):
                index_.append(index.text.strip())
        return index_

    def get_td(self)->List:
        all_tds= list()
    
        for table in self.soup.find_all(class_="index-performance"):
            for rows in table.find_all('tr'):
                for index in rows.find_all("td"):
                    all_tds.append(index.text)
        return all_tds

    def get_whole_table(self)->pd.DataFrame:
        start_val=list()
        middle_col= list()
        change= list()

        for i in range(len(self.get_td()))[::3]:
            start_val.append(self.get_td()[i])
            middle_col.append(self.get_td()[i+1])
            change.append(self.get_td()[i+2])

        return pd.DataFrame({"start_val":start_val, "31/08/2020":middle_col, "change":change})

    def get_graph_table(self)->List[pd.DataFrame]:
        tables_list =list()

        for i in range(3):
            table = [None] *3
            table[i]= self.get_whole_table().iloc[6*i: 6*(i+1), :]
            table[i]["index"]= self.get_column()
            table[i] = table[i].set_index("index")
            tables_list.append(table[i])
            print(tables_list)

        return tables_list


if __name__ =="__main__":
    
    URL = "https://www.rarewhisky101.com/indices/market-performance-indices/rw-apex-indices"
    headers ={
    "accept":"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "cookies": WHISKY_COOKIES2,
    "user-agent":"User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"  
    }

    datasource= DataSource(URL, headers)
    soup= datasource.get_html()
    parser= Parser_graph(soup)
    # test= parser.get_whole_table() 
    # print(test)

    
    RW_Apex_1000_Performance_Summary, RW_Apex_250_Performance_Summary, RW_Apex_100_Performance_Summary = parser.get_graph_table() 
    # Save to local dir
    RW_Apex_1000_Performance_Summary.to_csv(os.path.join(SAVE_PATH, "RW_Apex_1000_Performance_Summary.csv"))
    RW_Apex_250_Performance_Summary.to_csv(os.path.join(SAVE_PATH, "RW_Apex_250_Performance_Summary.csv"))
    RW_Apex_100_Performance_Summary.to_csv(os.path.join(SAVE_PATH, "RW_Apex_100_Performance_Summary.csv"))