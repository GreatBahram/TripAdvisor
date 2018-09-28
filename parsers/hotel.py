# Third party imports
import requests
from bs4 import BeautifulSoup


class HotelParser:
    def __init__(self, hotel_link):
        self.hotel_link = hotel_link
        self.name = self.get_name()
        self.session = requests.session()

    def __repr__(self):
        return "<HotelParser: {}>".format(self.name)

    def open_hotel_page(self, hotel_link):
        try:
            response_hotel_page = self.session.get(hotel_link).text
            soup = BeautifulSoup(response_hotel_page, 'lxml')
            review_ids = [review.attrs['data-reviewid'] for review in soup.select('.review-container')]
            data_val = {'reviews': ','.join(review_ids)}
            headers = {'Referer': hotel_link}
            return self.session.post(
                'https://www.tripadvisor.ca/OverlayWidgetAjax?Mode=EXPANDED_HOTEL_REVIEWS_RESP&metaReferer=',
                data=data_val,
                headers=headers), response_hotel_page
        except Exception as e:
            return None, None

    def get_name(self):
        try:
            return self.hotel_link.partition('-Reviews-')[2].split('-')[0]
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

    def _optional_information(self, uls_list):
        optional_dict = {
                'Service': 'N/A',
                'Cleanliness': 'N/A',
                'SleepQuality': 'N/A',
                }
        if uls_list:
            for ul in uls_list:
                for li in ul:
                    li_text = li.getText().replace(' ', '')  
                    if li_text in optional_dict:
                        optional_dict[li_text] = self._return_rating_code(li.select_one('div').attrs['class'][-1])
        return optional_dict

    def get_hotel_views_in_this_page(self, page):
        output_list = []
        soup = BeautifulSoup(page.text, 'lxml')
        reviews = soup.select('.reviewSelector')
        for review in reviews:
            data = {}
            data['review_text'] = review.select_one('.partial_entry').getText()
            data['rate'] = self._return_rating_code(review.select_one('.ui_bubble_rating').attrs['class'][1])
            data['user_id'] = review.select_one('.avatar').attrs['class'][-1]
            data['title'] = review.select_one('.noQuotes').getText()
            data['review_date'] = review.select_one('.ratingDate').attrs['title']
            data['stayed_date'] = review.select_one('.recommend-titleInline').getText().partition('Stayed: ')[-1].split(',')[0]
            trip_type_text = review.select_one('.recommend-titleInline').getText().partition('Stayed: ')[-1].split(' ')
            data['trip_type'] = trip_type_text[-1] if len(trip_type_text) > 2 else 'N/A'
            opt_info = self._optional_information(review.select('.recommend-column'))
            data['hotel'] = self.get_name()
            data.update(opt_info)
            output_list.append(data)
        return output_list

    def get_all_reviews(self):
        post_data, get_data = self.open_hotel_page(self.hotel_link)
        list_views = self.get_hotel_views_in_this_page(post_data)
        try:
            soup2 = BeautifulSoup(get_data, 'lxml')
            first_page_number = int(soup2.select_one('a.pageNum.first.current').attrs['data-page-number'])
            last_page_number = int(soup2.select_one('a.pageNum.last.taLnk').attrs['data-page-number'])
        except:
            first_page_number = last_page_number = None

        if first_page_number:
            for page_number in range(first_page_number, last_page_number):
                next_page_link = self.hotel_link.partition('-Reviews-')[0] + '-or' + str(page_number * 5) + '-' + self.hotel_link.partition('-Reviews-')[2]
                post_data, _ = self.open_hotel_page(next_page_link)
                list_views += self.get_hotel_views_in_this_page(post_data)
        return list_views
