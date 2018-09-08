import json
import time

import requests

from lxml import html
from lxml.etree import tostring


class City:

    def __init__(self):
        self.trip_advisor = 'https://www.tripadvisor.ca'
        self.name = ''
        self.Session = requests.session()
        self.uri = ''
        self.city_page = ''
        self.vacation_rentals_link = ''
        self.hotels_link = ''
        self.attration_link = ''
        self.resturant_link = ''
        self.hotels = []
        self.resturants = []
        self.vacation_rentals = []

    def set_city(self, name):
        self.trip_advisor = 'https://www.tripadvisor.ca'
        self.name = name
        self.Session = requests.session()
        self.uri = self.__get_city_uri(name)
        self.city_page = self.__openpage(self.uri)
        self.vacation_rentals_link = ''
        self.hotels_link = ''
        self.attration_link = ''
        self.resturant_link = ''
        self.hotels = []
        self.resturants = []
        self.vacation_rentals = []

    def start(self):
        self.__get_city_links()

    def __find_variable(self, text, variable):
        a = text.find(variable) + len(variable)
        b = text.find('"', text.find(variable) + len(variable))
        return text[a: b]

    def __get_city_uri(self, city_name):
        # Create today directory for new crs
        try:
            first_page = self.Session.get(self.trip_advisor)
        except Exception as e:
            print(e)
            return None

        # Get City Url
        search_session_id = self.__find_variable(first_page.text, 'typeahead.searchSessionId":"')
        time_now = str(int(time.time() * 1000))
        fetch_city_url = 'https://www.tripadvisor.ca/TypeAheadJson?interleaved=true&geoPages=true&details=true&types' \
                         '=geo,hotel,eat,attr,vr,air,theme_park,al,act,train,' \
                         'uni&neighborhood_geos=true&link_type=geo&matchTags=true&matchGlobalTags=true&matchKeywords' \
                         '=true&matchOverview=true&matchUserProfiles=true&strictAnd=false&scoreThreshold=0.8&hglt' \
                         '=true&disableMaxGroupSize=true&max=6&injectNewLocation=true&injectLists=true&nearby=true' \
                         '&local=true&parentids=&typeahead1_5=true&geoBoostFix=true&nearPages=true&nearPagesLevel' \
                         '=strict&supportedSearchTypes=find_near_stand_alone_query&query=' + city_name + \
                         '&action=API&uiOrigin=MASTHEAD&source=MASTHEAD&startTime=' + time_now + '&searchSessionId=' \
                         + search_session_id
        fetched_cities = self.Session.get(fetch_city_url)
        data = json.loads(fetched_cities.text)
        if 'results' in data:
            if len(data.get("results")) != 0:
                return self.trip_advisor + data.get("results")[0]['url']
        return None

    def __openpage(self, uri):
        try:
            city_page = self.Session.get(uri)
        except Exception as e:
            print(e)
            exit(1)
        return city_page.text

    def __get_city_links(self):
        tree = html.fromstring(self.city_page)
        nev_links = list(set(tree.xpath('//div[@class="navLinks"]/ul/li/a/@href')))
        for _ in nev_links:
            if 'Hotels-' in _:
                self.hotels_link = self.trip_advisor + str(_)
            elif 'Attractions-' in _:
                self.attration_link = self.trip_advisor + str(_)
            elif 'Restaurants-' in _:
                self.resturant_link = self.trip_advisor + str(_)
            elif 'VacationRentals-' in _:
                self.vacation_rentals_link = self.trip_advisor + str(_)

    def get_all_hotels_in_city(self):
        hotel_page = self.__openpage(self.hotels_link)
        tree = html.fromstring(hotel_page)
        hotels = list(
            set(tree.xpath('//a[contains(concat( " ", @class, " " ), concat( " ", "prominent", " " ))]/@href')))

        pages = list(
            set(tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "pageNumbers", " " ))]/a/@href')))
        max = -1
        min = 10000
        for _ in pages:
            a = _.find('-oa') + len('-oa')
            b = _.find('-', _.find('-oa') + len('-oa'))
            tmp = int(_[a: b])
            if tmp > max:
                max = tmp
            if tmp < min:
                min = tmp

        if len(pages) == 0:
            hotels = list(set(hotels))
            self.hotels = hotels
        else:
            page = pages[0]
            for i in range(min, max + 1, 30):
                a = page.find('-oa') + len('-oa')
                b = page.find('-', page.find('-oa') + len('-oa'))
                page = page[:a] + str(i) + page[b:]
                hotel_page = self.__openpage(self.trip_advisor + page)
                tree = html.fromstring(hotel_page)
                hotels += list(
                    set(tree.xpath('//a[contains(concat( " ", @class, " " ), concat( " ", "prominent", " " ))]/@href')))

        self.hotels = list(set(hotels))
        self.hotels = [self.trip_advisor + x for x in hotels]

        return self.hotels

    def get_all_resturant_in_city(self):
        resturant_page = self.__openpage(self.resturant_link)
        tree = html.fromstring(resturant_page)
        resturants = list(
            set(tree.xpath('//div[(@id = "EATERY_LIST_CONTENTS")]//a[contains(concat( " ", @class, " " ), concat( " '
                           '", "property_title", " " ))]/@href')))

        pages = list(
            set(tree.xpath('//div[(@id = "EATERY_LIST_CONTENTS")]//a[contains(concat( " ", @class, " " ), concat( " '
                           '", "taLnk", " " ))]/@href')))
        max = -1
        min = 10000
        for _ in pages:
            a = _.find('-oa') + len('-oa')
            b = _.find('-', _.find('-oa') + len('-oa'))
            tmp = int(_[a: b])
            if tmp > max:
                max = tmp
            if tmp < min:
                min = tmp

        if len(pages) == 0:
            resturants = list(set(resturants))
            self.resturants = resturants
        else:
            page = pages[0]
            for i in range(min, max + 1, 30):
                a = page.find('-oa') + len('-oa')
                b = page.find('-', page.find('-oa') + len('-oa'))
                page = page[:a] + str(i) + page[b:]
                resturant_page = self.__openpage(self.trip_advisor + page)
                tree = html.fromstring(resturant_page)
                resturants += list(
                                set(tree.xpath('//div[(@id = "EATERY_LIST_CONTENTS")]//a[contains(concat( " ", @class, " " ), concat( " '
                                '", "property_title", " " ))]/@href')))

        self.resturants = list(set(resturants))
        self.resturants = [self.trip_advisor + x for x in resturants]

        return self.resturants

    def get_all_vacation_rental_in_city(self):
        if self.vacation_rentals_link == "":
            return []
        vacation_rental_page = self.__openpage(self.vacation_rentals_link)
        tree = html.fromstring(vacation_rental_page)
        vacation_rentals = list(
            set(tree.xpath('//a[contains(concat( " ", @class, " " ), concat( " ", "vrPhotoLink", " " ))]/@href')))

        pages = list(
            set(tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "pageNumbers", " " ))]/a/@href')))
        max = -1
        min = 10000
        for _ in pages:
            a = _.find('-oa') + len('-oa')
            b = _.find('-', _.find('-oa') + len('-oa'))
            tmp = int(_[a: b])
            if tmp > max:
                max = tmp
            if tmp < min:
                min = tmp

        if len(pages) == 0:
            vacation_rentals = list(set(vacation_rentals))
            self.vacation_rentals = vacation_rentals
        else:
            page = pages[0]
            for i in range(min, max + 1, 30):
                a = page.find('-oa') + len('-oa')
                b = page.find('-', page.find('-oa') + len('-oa'))
                page = page[:a] + str(i) + page[b:]
                vacation_rental_page = self.__openpage(self.trip_advisor + page)
                tree = html.fromstring(vacation_rental_page)
                vacation_rentals += list(
                                set(tree.xpath('//a[contains(concat( " ", @class, " " ), concat( " ", "vrPhotoLink", " " ))]/@href')))

        self.vacation_rentals = list(set(vacation_rentals))
        self.vacation_rentals = [self.trip_advisor + x for x in vacation_rentals]

        return self.vacation_rentals

    def get_all_thing_to_do_in_city(self):
        if self.attration_link == "":
            return []
        atraction_page = self.__openpage(self.attration_link)
        tree = html.fromstring(atraction_page)
        attration = list(
            set(tree.xpath('//a[contains(concat( " ", @class, " " ), concat( " ", "vrPhotoLink", " " ))]/@href')))

        pages = list(
            set(tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "pageNumbers", " " ))]/a/@href')))
        max = -1
        min = 10000
        for _ in pages:
            a = _.find('-oa') + len('-oa')
            b = _.find('-', _.find('-oa') + len('-oa'))
            tmp = int(_[a: b])
            if tmp > max:
                max = tmp
            if tmp < min:
                min = tmp

        if len(pages) == 0:
            attration = list(set(attration))
            self.attrations = attration
        else:
            page = pages[0]
            for i in range(min, max + 1, 30):
                a = page.find('-oa') + len('-oa')
                b = page.find('-', page.find('-oa') + len('-oa'))
                page = page[:a] + str(i) + page[b:]
                atraction_page = self.__openpage(self.trip_advisor + page)
                tree = html.fromstring(atraction_page)
                attration += list(
                                set(tree.xpath('//a[contains(concat( " ", @class, " " ), concat( " ", "photo_link", " " ))]/@href')))

        self.attrations = list(set(attration))
        self.attrations = [self.trip_advisor + x for x in attration]

        return self.attrations
