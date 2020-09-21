from scraper.scrap_whisky import *
from scraper.scrap_graph_data import *
from config import * 


def main():
    URL= "https://www.whiskybase.com/whiskies/brand/81362/ardbeg"
    URL_2 = "https://www.rarewhisky101.com/indices/market-performance-indices/rw-apex-indices"
    SAVE_PATH= "whisky_data"
    
    datasource= DataSource(URL, headers)
    soup= datasource.get_html()
    parser= Parser(soup)
    left_section_data= parser.get_top_left_content()
    right_section_data= parser.get_top_right_content()
    # Save to CSV locally 
    left_section_data.to_csv(os.path.join(SAVE_PATH, "average_vote.csv"), index= False)
    right_section_data.to_csv(os.path.join(SAVE_PATH, "top5_votes.csv"), index= False)
    # product details table
    parse_main_table= parser.parse_main_table()
    parse_main_table.to_csv(os.path.join(SAVE_PATH, "product.csv"), index= False)

    datasource_graph= DataSource(URL, headers_2)
    soup_2= datasource_graph.get_html()
    parser_graph= Parser_graph(soup_2)

    RW_Apex_1000_Performance_Summary, RW_Apex_250_Performance_Summary, RW_Apex_100_Performance_Summary = parser_graph.get_graph_table() 
    # Save to local dir
    RW_Apex_1000_Performance_Summary.to_csv(os.path.join(SAVE_PATH, "RW_Apex_1000_Performance_Summary1.csv"))
    RW_Apex_250_Performance_Summary.to_csv(os.path.join(SAVE_PATH, "RW_Apex_250_Performance_Summary1.csv"))
    RW_Apex_100_Performance_Summary.to_csv(os.path.join(SAVE_PATH, "RW_Apex_100_Performance_Summary1.csv"))


if __name__== "__main__":
    main()