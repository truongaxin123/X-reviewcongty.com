from bs4 import BeautifulSoup, SoupStrainer
from urllib.request import urlretrieve
import requests
import logging

class Comment:

    def __init__(self, link_review, name, reaction, time, content):
        self.__link_review = link_review
        self.__name = name
        self.__reaction = reaction
        self.__time = time
        self.__content = content

    def getLinkReview(self):
        return self.__link_review

    def getName(self):
        return self.__name[0:-3]

    def getReaction(self):
        return self.__reaction

    def getTime(self):
        return self.__time

    def getContent(self):
        return self.__content

class Review:

    def __init__(self, link_company, company, name, content, time, like, dislike, delete, link):
        self.__link_company = link_company
        self.__company = company
        self.__name = name
        self.__content = content
        self.__time = time
        self.__like = like
        self.__dislike = dislike
        self.__delete_rq = delete
        self.__link = link
    
    def __str__(self):
        return f'<Review {self.__name}>'
        
    def __repr__(self):
        return f'<Review {self.__name}>'
    
    def getListComment(self):
        pass

class Company:

    def __init__(self, link, image, name, type_, amount_staffs, address, amount_reviews, amount_page_reviews):
        self.__link = link
        self.__image = image
        self.__name = name
        self.__type = type_
        self.__amount_staffs = amount_staffs
        self.__address = address
        self.__amount_reviews = amount_reviews
        self.__amount_page_reviews = amount_page_reviews

    def __repr__(self):
        return f'<Company {self.__name}>'

    def __str__(self):
        return f'<Company {self.__name}>'

    def downloadImageOfThisCompany(self, save_at):
        filename = self.__image.split('/')[-1]
        urlretrieve(self.__image, filename=filename)
    
    def getName(self):
        return self.__name

    def getType(self):
        return self.__type

    def getAmountStaffs(self):
        return self.__amount_staffs

    def getAddress(self):
        return self.__address

    def getAmountReviews(self):
        return self.__amount_reviews

    def getAmountPageReview(self):
        return self.__amount_page_reviews

    def getPageReviews(self, page)->list:
        list_reviews = []
        # code here...
        params = {'page':page}
        r = requests.get(self.__link, params=params)
        soup = BeautifulSoup(r.text, 'lxml')
        for review_card in soup(class_='review card'):
            name = [i for i in review_card.p.stripped_strings][0]
            time = str(review_card.time.string)
            link = f"https://reviewcongty.com{review_card.find(class_='review__share')['href']}"
            content = str(review_card.find(class_='content text-500').string).strip()
            like = list(review_card.find('span',{'data-reaction':'LIKE'}).stripped_strings)[0]
            dislike = list(review_card.find('span',{'data-reaction':'HATE'}).stripped_strings)[0]
            delete = list(review_card.find('span',{'data-reaction':'DELETE'}).stripped_strings)[0]

            rv = Review(link_company=self.__link, company=self.__name, name=name, time=time, content=content, like=like, dislike=dislike, delete=delete, link=link)
            list_reviews.append(rv)
        return list_reviews


    def gotoPageReviewOfThisCompany(self)->str:
        return self.__link


class Crawler:
    __currentNumberOfCompanies = None
    __numberCompanyOfEachPage = 20
    
    def getCurrentNumberOfPages(self):
        if self.__currentNumberOfCompanies != None:
            return
        r = requests.get('https://reviewcongty.com/')
        onlyPaginationSummary = SoupStrainer(class_='pagination-summary')
        soup = BeautifulSoup(r.text, 'lxml', parse_only=onlyPaginationSummary)
        paginationSummaryEle = soup.find(class_='pagination-summary')
        return int(paginationSummaryEle.find_all('b')[1].string)

    def getCurrentNumberOfCompanies(self):
        logging.info('Get current number of companies')
        return self.__numberCompanyOfEachPage * self.getCurrentNumberOfPages()
        
    def getListCompany(self, amount_company:int, option:str)->list:
        '''`option`: latest, best, worst\nReturn a list of Company objects'''
        if option not in ['latest','best','worst']:
            raise 'Option is wrong'

        params = {'tab':option}
        r = requests.get('https://reviewcongty.com/',params=params)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text,'lxml')
            listCompanyEle = soup.find_all(class_='company-item', limit=amount_company)
            
            out = []
            for company in listCompanyEle:
                link = f"https://reviewcongty.com{company['data-href']}"
                image = company.img['src']
                name = str(company.a.string).strip()
                type_ = str(company.div(class_='company-info__other')[0].span.span.next_sibling).strip()
                amount_reviews = int(str(company.span(class_='company-info__rating-count')[0].string).lstrip('(').rstrip(')'))
                amount_staffs_str = str(company.div(class_='company-info__other')[0].find_all('span')[2].span.next_sibling).strip()
                amount_staffs = tuple(int(i) for i in amount_staffs_str.split('-'))
                address_str = str(company.div(class_='company-info__location')[0].span.span.next_sibling).strip()
                address = ', '.join([i.strip() for i in address_str.split('\n')])

                gotoReviewPage = requests.get(link)
                # số lượng trang chứa comment review của một công ty
                soup_sub = BeautifulSoup(gotoReviewPage.text, 'lxml')
                if len(soup_sub.find_all(class_='pagination-summary')) > 0:
                    amount_page_reviews = int(soup_sub.find_all(class_='pagination-summary')[0].find_all('b')[1].string)
                else:
                    amount_page_reviews = 1

                c = Company(
                        link=link,
                        image=image,
                        name=name, type_=type_,
                        amount_reviews=amount_reviews,
                        amount_staffs=amount_staffs,
                        address=address,
                        amount_page_reviews=amount_page_reviews)

                out.append(c)
        return out

c = Crawler()
print(c.getCurrentNumberOfCompanies())
print(a:= c.getListCompany(3,'worst'))
print(a[0].getPageReviews(1))