from crawler import Crawler

if __name__ == '__main__':
    start_point = ['https://docs.microsoft.com/en-us/power-bi/developer/visuals/power-bi-custom-visuals']
    black_list = ["https://account.microsoft.com/", "https://choice.microsoft.com"]
    crawler = Crawler(urls=start_point, blacklist=black_list, url_count_limit=150)
    crawler.run()
