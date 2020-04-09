from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
def browse(url, proxy = None):
    #     url = 'https://httpbin.org/ip'
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    if proxy is not None:
        chrome_options.add_argument('--proxy-server=%s' % proxy)
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome('/home/ubuntu/chromedriver',chrome_options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(3) # seconds
    page_source = driver.page_source
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()
    return page_source, soup
    
class CrawlMKListing():
    MONGO_URI = "localhost:27017"
    MONGO_DB = "news"
    MONGO_COLLECTION = "malaysiakini_v1_test1"
    DOMAIN = "https://www.malaysiakini.com"
    NEWS_LISTING_DOMAIN = "https://www.malaysiakini.com/stories/covid19"
    PROXY_LIST = ["socks4://120.50.56.137:40553","socks4://121.122.50.157:4145", 
                  "socks4://1.9.167.36:60489","socks4://1.9.111.145:4145",
                  "socks4://45.117.228.153:4145","socks4://45.117.228.97:4145",
                  "socks4://103.220.6.254:4145"
                 ]
    START_URL = NEWS_LISTING_DOMAIN
    
    def __init__(self):
        pass
    
    def crawl(self):
        CURRENT_PAGE_URL = self.START_URL
        self.init_mongo()
        proxy = random.sample(self.PROXY_LIST,1)[0]
        print("Using proxy:", proxy)
        page_source, soup = browse(url = CURRENT_PAGE_URL, proxy = proxy)
        _check = self.check(soup)
        # if _check is not True, retry the whole crawl for this page
        if _check: 
            to_insert, next_page = self.parse(soup)
            to_insert_2 = self.prevent_duplicate(to_insert)
            if len(to_insert_2) > 0:
                self.coll.insert_many(to_insert_2)
        else:
            print("False check.")
            
    def init_mongo(self):
        client = pymongo.MongoClient(self.MONGO_URI)
        self.coll = client[self.MONGO_DB][self.MONGO_COLLECTION]

    def check(self, soup):
        try:
            x = soup.find("title").get_text()
        except:
            return False
        if x is None:
            return False
        if x.find("Access denied") >= 0:
            return False
        return True

    def parse(self, soup):
        DOMAIN = self.DOMAIN
        NEWS_LISTING_DOMAIN = self.NEWS_LISTING_DOMAIN
        
        x = soup.find("div", "news").find_all("a")[:-1]
        titles = [j.find("h3").getText() for j in x]
        urls = [j.get("href") for j in x]
        urls = [DOMAIN + url.replace(DOMAIN, "") for url in urls]
        df = pd.DataFrame(dict(title = titles, url = urls)) #.sample(30)
        if df.shape[0] == 0:
            raise Exception("shape 0")
        to_insert = df.to_dict(orient="records")
        next_page = NEWS_LISTING_DOMAIN + soup.find("div", "news").find_all("a")[-1].get("href")
        return to_insert, next_page
    
    def prevent_duplicate(self, to_insert):
        url_list = [j.get("url") for j in to_insert]
        exist_url_list = [j.get("url") for j in list(self.coll.find({"url": {"$in": url_list}}, {"url":1}))]
        to_insert_2 = [j for j in to_insert if j.get("url") not in exist_url_list]
        return to_insert_2
    

C = CrawlMKListing()
C.crawl()