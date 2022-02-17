from crawler import Crawler

if __name__ == '__main__':
    url = 'https://docs.microsoft.com/en-us/power-bi/developer/visuals/power-bi-custom-visuals'
    start_point = 'https://docs.microsoft.com/en-us/power-bi/developer/visuals/'
    crawler = Crawler(urls=[url])
    crawler.run()
