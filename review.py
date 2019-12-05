from bs4 import BeautifulSoup, SoupStrainer
from urllib.request import urlretrieve
import requests


class Review:

    def __init__(self, company, name, stars, content, time, like, dislike, delete_rq, link):
        self.__company = company
        self.__name = name
        self.__stars = stars
        self.__content = content
        self.__time = time
        self.__like = like
        self.__dislike = dislike
        self.__delete_rq = delete_rq
        self.__link = link

class Company:

    def __init__(self, link, image, name, type_, amount_staffs, address, amount_reviews):
        self.__link = link
        self.__image = image
        self.__name = name
        self.__type = type_
        self.__amount_staffs = amount_staffs
        self.__address = address
        self.__amount_reviews = amount_reviews

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

    def getAllReviews(self)->list:
        list_reviews = []
        # code here...
        return list_reviews

    def gotoPageReviewOfThisCompany(self)->str:
        name = self.__image.split('/')[-1][0:-4]
        return f'https://reviewcongty.com/companies/{name}'


class Crawler:
    __currentNumberOfCompanies = None
    
    def getCurrentNumberOfCompanies(self):
        if self.__currentNumberOfCompanies != None:
            return
        r = requests.get('https://reviewcongty.com/')
        onlyPaginationSummary = SoupStrainer(class_='pagination-summary')
        soup = BeautifulSoup(r.text, 'lxml', parse_only=onlyPaginationSummary)
        paginationSummaryEle = soup.find(class_='pagination-summary')
        return int(paginationSummaryEle.find_all('b')[1].string)
        


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
                
                c = Company(link=link, image=image, name=name, type_=type_, amount_reviews=amount_reviews, amount_staffs=amount_staffs, address=address)
                out.append(c)
        return out

c = Crawler()
print(c.getCurrentNumberOfCompanies())
print(c.getListCompany(3,'best'))