from lxml.etree import tostring
import requests
from lxml import html


class VacationRental:
    def set_database(self,database):
        self.database = database

    def set_city_name(self,city_name):
        self.city_name = city_name

    def set_vacation_rental(self, vacation_rental_link):
        self.trip_advisor = 'https://www.tripadvisor.com'
        self.vacation_rental_link = vacation_rental_link
        self.name = self.get_vacation_rental_name
        if self.name is None:
            return None
        self.Session = requests.session()
        self.rw_count = 0;

    def get_review_count(self):
        return self.rw_count

    def find_variable(self, text, variable):
        a = text.find(variable) + len(variable)
        b = text.find('"', text.find(variable) + len(variable))
        return text[a: b]

    def open_vacation_rental_page(self, vacation_rental_link):
        try:
            response_vacation_rental_page = self.Session.get(vacation_rental_link)
            tree = html.fromstring(response_vacation_rental_page.text)
            review_ids = list(set(tree.xpath(
                '//*[contains(concat( " ", @class, " " ), concat( " ", "review-container", " " ))]/@data-reviewid')))
            data_val = {'reviews': ','.join(review_ids)}
            headers = {'Referer': vacation_rental_link}
            return self.Session.post(
                'https://www.tripadvisor.ca/OverlayWidgetAjax?Mode=EXPANDED_HOTEL_REVIEWS_RESP&metaReferer=',
                data=data_val,
                headers=headers)
        except Exception as e:
            return None

    @property
    def get_vacation_rental_name(self):
        try:
            return self.vacation_rental_link[self.vacation_rental_link.find('Review-') + 24: self.vacation_rental_link.find('-', self.vacation_rental_link.find('Review-') + 24)]
        except Exception as e:
            return None

    def get_vacation_rental_views_in_this_page(self, page):
        output_list = []
        tree = html.fromstring(page.text)
        reviews = list(set(tree.xpath('//div[@class="reviewSelector"]')))
        for _ in reviews:
            try:
                data = {}
                tree = html.fromstring(str(tostring(_)))
                review_list = list(tree.xpath('//div[@class="entry"]'))
                review_text = ''
                tree_ = html.fromstring(str(tostring(review_list[0])))
                review_text_list = list(tree_.xpath('//p[@class="partial_entry"]/text()'))
                for text in review_text_list:
                    review_text = review_text + text
                user_id = list(set(tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "avatar", " " ))]/@class')))[0]
                user_id = user_id[15:]
                title = list(set(
                    tree.xpath('//span[contains(concat( " ", @class, " " ), concat( " ", "noQuotes", " " ))]/text()')))[
                    0]
                rating_date = list(set(tree.xpath(
                    '//span[contains(concat( " ", @class, " " ), concat( " ", "ratingDate", " " ))]/@title')))[0]
                stay_date = ''
                try:
                    stay_date = list(set(tree.xpath(
                        '//div[contains(concat( " ", @class, " " ), concat( " ", "recommend-titleInline", " " ))]/text()')))[
                        0]
                except:
                    stay_date = ''
                rate_val = -1
                if len(list(set(tree.xpath('//span[contains(concat( " ", @class, " " ), concat( " ", "ui_bubble_rating bubble_50", " " ))]')))) :
                    rate_val = 5
                elif len(list(set(tree.xpath('//span[contains(concat( " ", @class, " " ), concat( " ", "ui_bubble_rating bubble_40", " " ))]')))) :
                    rate_val = 4
                elif len(list(set(tree.xpath('//span[contains(concat( " ", @class, " " ), concat( " ", "ui_bubble_rating bubble_30", " " ))]')))) :
                    rate_val = 3
                elif len(list(set(tree.xpath('//span[contains(concat( " ", @class, " " ), concat( " ", "ui_bubble_rating bubble_20", " " ))]')))) :
                    rate_val = 2
                elif len(list(set(tree.xpath('//span[contains(concat( " ", @class, " " ), concat( " ", "ui_bubble_rating bubble_10", " " ))]')))) :
                    rate_val = 1
                self.database.add_reveiw(review_text, title, rating_date,rate_val,'', user_id, self.__class__.__name__, self.name, self.city_name)
                self.rw_count += 1

                #     data['review_text'] = review_text
                #     data['title'] = title
                #     data['user_id'] = user_id
                #     data['rating_date'] = rating_date
                #     data['stay_date'] = stay_date
                #     output_list.append(data)
                # return output_list
            except Exception as e:
                continue

    def get_all_vacation_rental_reviews(self):
        response_vacation_rental_page = self.Session.get(self.vacation_rental_link)
        vacation_rental_link = self.vacation_rental_link
        tree = html.fromstring(response_vacation_rental_page.text)
        try:
            page_numbers = list(set(tree.xpath(
                '//div[@id="REVIEWS"]//div[contains(concat( " ", @class, " " ), concat( " ", "ui_pagination", '
                '" " ))]/div/a/@data-page-number')))
            page_numbers = max(list(map(int, page_numbers)))
        except:
            page_numbers = -1

        vacation_rental_page_content = self.open_vacation_rental_page(self.vacation_rental_link)
        self.get_vacation_rental_views_in_this_page(vacation_rental_page_content)
        # list_views = self.get_vacation_rental_views_in_this_page(vacation_rental_page_content)

        if page_numbers != -1:
            for i in range(1, page_numbers):
                next_vacation_rental_page = vacation_rental_link[:vacation_rental_link.find('-Reviews-')] \
                                  + '-or' + str(i * 5) + '-' \
                                  + vacation_rental_link[vacation_rental_link.find('-Reviews-') + 9:]
                self.get_vacation_rental_views_in_this_page(self.open_vacation_rental_page(next_vacation_rental_page))
                # list_views += self.get_vacation_rental_views_in_this_page(self.open_vacation_rental_page(next_vacation_rental_page))

        # return list_views
