import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

from configparser import ConfigParser

class scrapper():
    
    def __init__(self) -> None:
        
        configObject = ConfigParser()
        configObject.read('../Config/application.ini')        

        self.flipkartConf = configObject['flipkart']
        print(self.flipkartConf['baseurl'])
        
    def search_text(self, txt):
        
        txt = txt.strip()    ##Remove extra spaces from start & end
        requesturl = self.flipkartConf['baseurl'] + "/search?q=" + '%20'.join(txt.split(' '))
        print(requesturl)
        
        try:
            url_client = uReq(requesturl)
            # print(type(url_client))
            if url_client.status !=200:
                raise Exception('Unable to reach the Flipkart url,  status- {}'.format(url_client.status))
            
            return {
                'status': True, 
                'client': url_client
            }    
        except Exception as e:
            print(e)
            return {'status': False}
    
    def process_all_links(self, requestObj, extractall=False):
        
        flipkart_html = bs(requestObj, "html.parser")
        
        ## Each page has 24 components
        bigboxes = flipkart_html.find_all('div', {'class' : '_1AtVbE col-12-12'})
        print(len(bigboxes))
        
        ## No data on page
        if len(bigboxes)<=1:
            return {'status': False, 'reason':'No Data'}        
        
        total_pages = self._get_pages(bigboxes) 
                
        ## valid boxes div starts from index 3 to 26
        
        
        if extractall:
            pass
            
            # for i in range(1, total_pages+1):
            #     print(i)
        
        else:
            
            ##Extract only first product
            box = bigboxes[2]
            productlink = box.div.div.div.a['href']
            valid_link = self.flipkartConf['baseurl'] + productlink.split('&lid')[0]   ##Spliting link to remove extra query parameters
            print(valid_link)
            
            self._extract_reviews(valid_link)    

    def _extract_reviews(self, product_link: str):
        
        prodRes = requests.get(product_link.replace('/p/', '/product-reviews/'))
        prodRes.encoding='utf-8'         
        # url_client = uReq(product_link.replace('/p/', '/product-reviews/'))
        if prodRes.status_code != 200:
        # if url_client.status != 200:
            print('Unable to extract reviews from -{}'.format(product_link))
            return

        # review_page_html = bs(url_client, "html.parser")
        review_page_html = bs(prodRes.text, "html.parser")
        
        all_reviews = review_page_html.find_all('div', {'class': '_1AtVbE col-12-12'})
        
        ##  starts from element - 5
        for i in range(4, len(all_reviews)-1):
            
            valid_div = all_reviews[i].div.div.div
            # valid_div = valid_div.encode('utf')
            
            rating = valid_div.div.div.text
            rating =rating.encode('utf')
            
            overall_review = valid_div.div.p.text
            overall_review = overall_review.encode('utf')
            
            review = valid_div.find_all('div', {'class':'t-ZTKy'})[0].div.div.text
            review = review.encode('utf')
            
            location = valid_div.find_all('p', {'class': '_2mcZGG'})[0].find_all('span', {'':''})[-1].text
            location= location.encode(encoding='utf-8')
            
            name = valid_div.find_all('p', {'class':'_2sc7ZR _2V5EHH'})[0].text
            name = name.encode('utf-8')
            
            if name.strip()=='Flipkart Customer':
                name = 'Not Available'
    
            print('Comment Head - {}\n, Name - {}\nRating - {}\nReview - {}\nlocation - {}\n'.format(overall_review, name, rating, review, location))
        
        
        
        
    
        

    def _get_pages(self, bigboxes: bs):
        ## Extract number of pages
        PageBox = bigboxes[len(bigboxes)-3-1]     ##Subtracting from 3 beacuse its third last component
        txt = PageBox.div.div.span.text
        
        return int(txt.split()[-1])



if __name__ =='__main__':
    
    s=scrapper()  
    op=s.search_text('iphone 11')
    print(op)
    s.process_all_links(op['client'])

    
    
