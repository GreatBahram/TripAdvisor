import requests
from lxml import html
from lxml.etree import tostring


class RestaurantParser:
    def __init__(self, restaurant_link):
        self.resturant_link = restaurant_link
        self.trip_advisor = 'https://www.tripadvisor.ca'
        self.name = self.get_name()
        if self.name is None:
            return None
        self.Session = requests.session()

    def open_resturant_page(self, resturant_link):
        try:
            response_resturant_page = self.Session.get(resturant_link)
            tree = html.fromstring(response_resturant_page.text)
            review_ids = list(set(tree.xpath(
                '//*[contains(concat( " ", @class, " " ), concat( " ", "review-container", " " ))]/@data-reviewid')))
            data_val = {'reviews': ','.join(review_ids)}
            headers = {'Referer': resturant_link}
            return self.Session.post(
                'https://www.tripadvisor.ca/OverlayWidgetAjax?Mode=EXPANDED_HOTEL_REVIEWS_RESP&metaReferer=',
                data=data_val,
                headers=headers)
        except Exception as e:
            return None

    def get_name(self):
        try:
            return self.resturant_link[self.resturant_link.find('-Reviews-') + 9: self.resturant_link.find('-',
                                                                                               self.resturant_link.find(
                                                                                                   '-Reviews-') + 9)]
        except Exception as e:
            return None

    def get_resturant_views_in_this_page(self, page):
        output_list = []
        tree = html.fromstring(page.text)
        reviews = list(set(tree.xpath('//div[@class="reviewSelector"]')))
        for _ in reviews:
            data = {}
            tree = html.fromstring(str(tostring(_)))
            review_text = list(set(tree.xpath('//p[@class="partial_entry"]/text()')))
            review_text = review_text[0]
            user_id = list(set(tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "avatar", " " ))]/@class')))[0]
            user_id = user_id[15:]
            title = list(set(tree.xpath('//span[contains(concat( " ", @class, " " ), concat( " ", "noQuotes", " " ))]/text()')))[0]
            rating_date = list(set(tree.xpath('//span[contains(concat( " ", @class, " " ), concat( " ", "ratingDate", " " ))]/@title')))[0]
            data['review_text'] = review_text
            data['title'] = title
            data['user_id'] = user_id
            data['date'] = rating_date
            data['restaurant'] = self.get_name()
            output_list.append(data)
        return output_list

    def get_all_reviews(self):
        response_resturant_page = self.Session.get(self.resturant_link)
        resturant_link = self.resturant_link
        tree = html.fromstring(response_resturant_page.text)
        try:
            page_numbers = list(set(tree.xpath(
                '//div[@id="REVIEWS"]//div[contains(concat( " ", @class, " " ), concat( " ", "ui_pagination", '
                '" " ))]/div/a/@data-page-number')))
            page_numbers = max(list(map(int, page_numbers)))
        except:
            page_numbers = -1

        resturant_page_content = self.open_resturant_page(self.resturant_link)
        list_views = self.get_resturant_views_in_this_page(resturant_page_content)

        if page_numbers != -1:
            for i in range(1, page_numbers):
                next_resturant_page = resturant_link[:resturant_link.find('-Reviews-')] \
                                  + '-or' + str(i * 5) + '-' \
                                  + resturant_link[resturant_link.find('-Reviews-') + 9:]
                list_views += self.get_resturant_views_in_this_page(self.open_resturant_page(next_resturant_page))

        return list_views
