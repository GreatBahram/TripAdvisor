# Standard library imports
from collections import namedtuple

# Third party imports
import requests
from bs4 import BeautifulSoup


class RestaurantParser:
    def __init__(self, restaurant_link):
        self.restaurant_link = restaurant_link
        self.name = self.get_name()
        self.session = requests.session()

    def open_restaurant_page(self, restaurant_link):
        try:
            response_restaurant_page = self.session.get(restaurant_link).text
            soup = BeautifulSoup(response_restaurant_page, 'lxml')
            review_ids = [review.attrs['data-reviewid'] for review in soup.select('.review-container')]
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

    def _return_rating_code(self, class_):
        rating_code = {
                'bubble_50': '5.0',
                'bubble_45': '4.5',
                'bubble_40': '4.0',
                'bubble_35': '3.5',
                'bubble_30': '3.0',
                'bubble_25': '2.5',
                'bubble_20': '2.0',
                'bubble_15': '1.5',
                'bubble_10': '1.0',
                'bubble_05': '0.5',
                }
        return rating_code.get(class_, 'N/A')

    def get_restaurant_views_in_this_page(self, page):
        output_list = []
        soup = BeautifulSoup(page.text, 'lxml')
        reviews = soup.select('.reviewSelector')
        for review in reviews:
            data = {}
            data['review_text'] = review.select_one('.partial_entry').getText()
            data['rate'] = self._return_rating_code(review.select_one('.ui_bubble_rating').attrs['class'][1])
            data['user_id'] = review.select_one('.avatar').attrs['class'][-1]
            data['title'] = review.select_one('.noQuotes').getText()
            data['date'] = review.select_one('.ratingDate').attrs['title']
            data['restaurant'] = self.get_name()
            output_list.append(data)
        return output_list

    def get_all_reviews(self):
        post_data, get_data = self.open_restaurant_page(self.restaurant_link)
        restaurant_link = self.restaurant_link
        list_views = self.get_restaurant_views_in_this_page(post_data)
        try:
            soup2 = BeautifulSoup(get_data, 'lxml')
            first_page_number = int(soup2.select_one('a.pageNum.first.current').attrs['data-page-number'])
            last_page_number = int(soup2.select_one('a.pageNum.last.taLnk').attrs['data-page-number'])
        except:
            first_page_number = last_page_number = None

        if first_page_number:
            for page_number in range(first_page_number, last_page_number):
                next_page_link = self.restaurant_link.partition('-Reviews-')[0] + '-or' + str(page_number * 10) + '-' + self.restaurant_link.partition('-Reviews-')[2]
                post_data, _ = self.open_restaurant_page(next_page_link)
                list_views += self.get_restaurant_views_in_this_page(post_data)
        return list_views
