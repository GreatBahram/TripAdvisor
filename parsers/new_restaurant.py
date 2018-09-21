# Standard library imports
from collections import namedtuple

# Third party imports
import requests
from bs4 import BeautifulSoup
from lxml import html
from lxml.etree import tostring

Review = namedtuple('Review', 'user_id date title review_text restaurant')


class RestaurantParser:
    def __init__(self, restaurant_link):
        self.restaurant_link = restaurant_link
        self.name = self.get_name()
        self.result = []
        self.session = requests.session()
        if not self.name:
            return None

    def get_link_data(self, restaurant_link):
        try:
            response_restaurant_page = self.session.get(restaurant_link).text
            tree = html.fromstring(response_restaurant_page)
            review_ids = list(set(tree.xpath(
                '//*[contains(concat( " ", @class, " " ), concat( " ", "review-container", " " ))]/@data-reviewid')))
            data_val = {'reviews': ','.join(review_ids)}
            headers = {'Referer': restaurant_link}
            return self.session.post(
                'https://www.tripadvisor.ca/OverlayWidgetAjax?Mode=EXPANDED_HOTEL_REVIEWS_RESP&metaReferer=',
                data=data_val,
                headers=headers), response_restaurant_page
        except Exception as e:
            return None, None

    def get_name(self):
        try:
            return self.restaurant_link.partition('-Reviews-')[2].split('-')[0]
        except Exception as e:
            return None

    def parse_reviews(self, reviews):
        for review in reviews:
            review_rext = review.select_one('.partial_entry').getText()
            review_user_id = review.select_one('.avatar').attrs['class'][-1]
            review_title = review.select_one('.noQuotes').getText()
            review_date = review.select_one('.ratingDate').attrs['title']
            review = Review(user_id=review_user_id, date=review_date, title=review_title, review_text=review_rext, restaurant=self.get_name())
            self.result.append(review)

    def get_all_reviews(self):
        post_data, get_data = self.get_link_data(self.restaurant_link)
        soup = BeautifulSoup(post_data.text, 'lxml')
        reviews = soup.select('.reviewSelector')
        if reviews:
            self.parse_reviews(reviews)
        try:
            soup2 = BeautifulSoup(get_data, 'lxml')
            first_page_number = int(soup2.select_one('a.pageNum.first.current').attrs['data-page-number'])
            last_page_number = int(soup2.select_one('a.pageNum.last.taLnk').attrs['data-page-number'])
        except:
            first_page_number = last_page_number = None

        if first_page_number:
            for page_number in range(first_page_number, last_page_number):
                next_page_link = self.restaurant_link.partition('-Reviews-')[0] + '-or' + str(page_number * 10) + '-' + self.restaurant_link.partition('-Reviews-')[2]
                post_data, _ = self.get_link_data(next_page_link)
                soup = BeautifulSoup(post_data.text, 'lxml')
                reviews = soup.select('.reviewSelector')
                if reviews:
                    self.parse_reviews(reviews)
        return self.result
