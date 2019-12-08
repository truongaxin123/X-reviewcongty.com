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

    def get_link_review(self):
        return self.__link_review

    def get_name(self):
        return self.__name[0:-3]

    def get_reaction(self):
        return self.__reaction

    def get_time(self):
        return self.__time

    def get_content(self):
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
    
    def get_list_comment(self):
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

    def download_image_of_this_company(self, save_at):
        filename = self.__image.split('/')[-1]
        urlretrieve(self.__image, filename=filename)
    
    def get_name(self):
        return self.__name

    def get_type(self):
        return self.__type

    def get_amount_staffs(self):
        return self.__amount_staffs

    def get_address(self):
        return self.__address

    def get_amount_reviews(self):
        return self.__amount_reviews

    def get_amount_page_reviews(self):
        return self.__amount_page_reviews

    def get_review_on_page(self, page) -> list:
        list_reviews = []
        # code here...
        params = {'page': page}
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

    def goto_page_review_of_this_company(self) -> str:
        return self.__link


class Crawler:
    __currentNumberOfCompanies = None
    __numberCompanyOfEachPage = 20
    
    def get_current_number_of_page(self) -> int:
        """Return amount the container page of the website"""
        if self.__currentNumberOfCompanies:
            return self.__currentNumberOfCompanies
        r = requests.get('https://reviewcongty.com/')
        only_pagination_summary = SoupStrainer(class_='pagination-summary')
        soup = BeautifulSoup(r.text, 'lxml', parse_only=only_pagination_summary)
        pagination_summary_ele = soup.find(class_='pagination-summary')
        return int(pagination_summary_ele.find_all('b')[1].string)

    def get_current_number_of_company(self) -> int:
        """Return amount of the current company in the website, chỉ ở mức gần đúng."""
        logging.info('Get current number of companies')
        return self.__numberCompanyOfEachPage * self.get_current_number_of_page()

    @staticmethod
    def get_list_company_from_option(amount_company: object, option: object) -> object:
        """Lấy ra List các company object dựa theo option.\n
        option: latest, best, worst\nReturn a list of Company objects"""
        if option not in ['latest', 'best', 'worst']:
            raise Exception('Option is wrong')

        params = {'tab': option}
        r = requests.get('https://reviewcongty.com/', params=params)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'lxml')
            list_company_element = soup.find_all(class_='company-item', limit=amount_company)

            out = []
            for company in list_company_element:
                link = f"https://reviewcongty.com{company['data-href']}"
                image = company.img['src']
                name = str(company.a.string).strip()
                type_ = str(company.div(class_='company-info__other')[0].span.span.next_sibling).strip()
                amount_reviews = int(str(company.span(class_='company-info__rating-count')[0].string).lstrip('(').rstrip(')'))

                amount_staffs = str(company.div(class_='company-info__other')[0].find_all('span')[2].span.next_sibling).strip()

                address_str = str(company.div(class_='company-info__location')[0].span.span.next_sibling).strip()
                address = ', '.join([i.strip() for i in address_str.split('\n')])

                goto_review_page = requests.get(link)
                # số lượng trang chứa comment review của một công ty
                soup_sub = BeautifulSoup(goto_review_page.text, 'lxml')
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

    @staticmethod
    def get_company_from_link(link: object) -> object:
        """
        @param link: str object
        @return: list of Company object
        """
        r = requests.get(link)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'lxml')
            company = soup.find('section', class_='company-info-company-page')

            image = company.img['src']
            name = str(company.a.string).strip()
            type_ = str(company.div(class_='company-info__other')[0].span.span.next_sibling).strip()
            amount_reviews = int(str(company.span(class_='company-info__rating-count')[0].string).lstrip('(').rstrip(')'))
            
            amount_staffs_str = str(company.div(class_='company-info__other')[0].find_all('span')[2].span.next_sibling).strip()
            amount_staffs = tuple(int(i) for i in amount_staffs_str.split('-'))
            
            address_str = str(company.div(class_='company-info__location')[0].span.span.next_sibling).strip()
            address = ', '.join([i.strip() for i in address_str.split('\n')])
            
            # số lượng trang chứa comment review của một công ty
            if len(soup.find_all(class_='pagination-summary')) > 0:
                amount_page_reviews = int(soup.find_all(class_='pagination-summary')[0].find_all('b')[1].string)
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
        return c

    @staticmethod
    def get_list_company_from_page(page: object) -> object:
        """Lấy ra list company object dựa theo số page, nếu page vượt quá số lượng tối đa, trả về page 1"""
        out = []
        params = {'page': page}
        r = requests.get('https://reviewcongty.com/', params=params)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text,'lxml')
            list_company_ele = soup.find_all(class_='company-item')

            out = []
            for company in list_company_ele:
                link = f"https://reviewcongty.com{company['data-href']}"
                image = company.img['src']
                name = str(company.a.string).strip()
                type_ = str(company.div(class_='company-info__other')[0].span.span.next_sibling).strip()
                amount_reviews = int(str(company.span(class_='company-info__rating-count')[0].string).lstrip('(').rstrip(')'))
                amount_staffs = str(company.div(class_='company-info__other')[0].find_all('span')[2].span.next_sibling).strip()
                address_str = str(company.div(class_='company-info__location')[0].span.span.next_sibling).strip()
                address = ', '.join([i.strip() for i in address_str.split('\n')])

                goto_review_page = requests.get(link)
                # số lượng trang chứa comment review của một công ty
                soup_sub = BeautifulSoup(goto_review_page.text, 'lxml')
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
