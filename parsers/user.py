import requests

from lxml import html
from lxml.etree import tostring


class UserParser:

    def set_database(self,database):
        self.database = database

    def set_user_id(self, id):
        self.Session = requests.session()
        self.trip_advisor = 'https://www.tripadvisor.ca'
        self.id = id
        self.brief = self.get_user_brief()
        self.name = ''
        self.user_link = ''
        self.leve_of_contribor = 0
        self.n_contributions = 0
        self.n_cities_visited = 0
        self.n_helpful_votes = 0
        self.from_city = ''
        self.get_attributes()

    def find_variable(self, text, variable):
        a = text.find(variable) + len(variable)
        b = text.find('"', text.find(variable) + len(variable))
        return text[a: b]

    def open_user_page(self, hotel_link):
        try:
            response_hotel_page = self.Session.get(hotel_link)
            tree = html.fromstring(response_hotel_page.text)
            review_ids = list(set(tree.xpath(
                '//*[contains(concat( " ", @class, " " ), concat( " ", "review-container", " " ))]/@data-reviewid')))
            data_val = {'reviews': ','.join(review_ids)}
            headers = {'Referer': hotel_link}
            return self.Session.post(
                'https://www.tripadvisor.ca/OverlayWidgetAjax?Mode=EXPANDED_HOTEL_REVIEWS_RESP&metaReferer=',
                data=data_val,
                headers=headers)
        except Exception as e:
            return None

    def get_user_brief(self):
        return 'https://www.tripadvisor.ca/MemberOverlay?Mode=owa&uid=' + self.id + '&c=&src=597541025&fus=false&partner=false&LsoId=&metaReferer=Restaurant_Review'

    def get_attributes(self):
        brief_page = self.Session.get(self.brief)
        tree = html.fromstring(brief_page.text)
        self.name = list(set(tree.xpath('//a/h3/text()')))[0]
        self.user_link = self.trip_advisor + list(set(tree.xpath('//a/@href')))[0]
        tmp_leve_of_contribor = list(set(tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "badgeinfo", " " ))]/span/text()')))
        tmp_ns = list(set(tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "badgeTextReviewEnhancements", " " ))]/text()')))
        tmp_from_city = list(set(tree.xpath(
            '//*[contains(concat( " ", @class, " " ), concat( " ", "memberdescriptionReviewEnhancements", " " ))]/li/text()')))

        for _ in tmp_from_city:
            if 'from' in _:
                tmp = _
                tmp = tmp[tmp.find('from') + 5:]
                self.from_city = tmp

        if len(tmp_leve_of_contribor) == 1:
            self.leve_of_contribor = tmp_leve_of_contribor[0]
        else:
            self.leve_of_contribor = 0

        for _ in tmp_ns:
            if 'Cities visited' in _:
                tmp = _
                tmp = tmp[0:tmp.find(' ')]
                self.n_cities_visited = int(tmp)
            elif 'Contributions' in _:
                tmp = _
                tmp = tmp[0:tmp.find(' ')]
                self.n_contributions = int(tmp)
            elif 'Helpful votes' in _:
                tmp = _
                tmp = tmp[0:tmp.find(' ')]
                self.n_helpful_votes = int(tmp)
