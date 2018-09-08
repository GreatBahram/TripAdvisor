import json
import time
from lxml.etree import tostring
from tripDatabase import *
import requests
from lxml import html


Session = requests.session()
tripadvisor = 'https://www.tripadvisor.ca'


def findVariable(Text, Variable):
    a = Text.find(Variable) + len(Variable)
    b = Text.find('"', Text.find(Variable) + len(Variable))
    return Text[a: b]


def getCityUri(cityName):
    # Create today directory for new crs
    global Session
    global tripadvisor
    try:
        firstPage = Session.get(tripadvisor)
    except Exception as e:
        print(e)
        return None

    # Get City Url
    searchSessionId = findVariable(firstPage.text, 'typeahead.searchSessionId":"')
    SessionId = findVariable(firstPage.text, '"sessionId":"')
    TimeNow = str(int(time.time() * 1000))
    fetchCityUrl = 'https://www.tripadvisor.ca/TypeAheadJson?interleaved=true&geoPages=true&details=true&types=geo,hotel,eat,attr,vr,air,theme_park,al,act,train,uni&neighborhood_geos=true&link_type=geo&matchTags=true&matchGlobalTags=true&matchKeywords=true&matchOverview=true&matchUserProfiles=true&strictAnd=false&scoreThreshold=0.8&hglt=true&disableMaxGroupSize=true&max=6&injectNewLocation=true&injectLists=true&nearby=true&local=true&parentids=&typeahead1_5=true&geoBoostFix=true&nearPages=true&nearPagesLevel=strict&supportedSearchTypes=find_near_stand_alone_query&query=' + cityName + '&action=API&uiOrigin=MASTHEAD&source=MASTHEAD&startTime=' + TimeNow + '&searchSessionId=' + searchSessionId
    fetchedCities = Session.get(fetchCityUrl)
    data = json.loads(fetchedCities.text)
    return data["results"][0]['url']


def openPage(Uri):
    global Session
    try:
        cityPage = Session.get(Uri)
    except Exception as e:
        print(e)
        exit(1)

    return cityPage.text


def getCityLinks(cityPage):
    tree = html.fromstring(cityPage)
    nevLinks = list(set(tree.xpath('//div[@class="navLinks"]/ul/li/a/@href')))
    return nevLinks


def getAllHotelsInCity(hotelsPage):
    tree = html.fromstring(hotelsPage)
    hotels = list(
        set(tree.xpath('//a[contains(concat( " ", @class, " " ), concat( " ", "prominent", " " ))]/@href')))

    pages = list(
        set(tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "pageNumbers", " " ))]/a/@href')))
    Max = -1
    Min = 10000
    for _ in pages:
        a = _.find('-oa') + len('-oa')
        b = _.find('-', _.find('-oa') + len('-oa'))
        tmp = int(_[a: b])
        if tmp > Max:
            Max = tmp
        if tmp < Min:
            Min = tmp

    if len(pages) == 0:
        hotels = list(set(hotels))
        return hotels
    page = pages[0]
    for i in range(Min, Max + 1, 30):
        a = page.find('-oa') + len('-oa')
        b = page.find('-', page.find('-oa') + len('-oa'))
        page = page[:a] + str(i) + page[b:]
        mahdi = openPage(tripadvisor + page)
        tree = html.fromstring(mahdi)
        hotels += list(
            set(tree.xpath('//a[contains(concat( " ", @class, " " ), concat( " ", "prominent", " " ))]/@href')))

    hotels = list(set(hotels))
    return hotels


def openHotelPage(hotelLink):
    try:
        responseHotelPage = Session.get(hotelLink)
        tree = html.fromstring(responseHotelPage.text)
        review_ids = list(set(tree.xpath(
            '//*[contains(concat( " ", @class, " " ), concat( " ", "review-container", " " ))]/@data-reviewid')))
        data_val = {'reviews': ','.join(review_ids)}
        headers = {'Referer': hotelLink}
        return Session.post(
            'https://www.tripadvisor.ca/OverlayWidgetAjax?Mode=EXPANDED_HOTEL_REVIEWS_RESP&metaReferer=', data=data_val,
            headers=headers)
    except:
        return None


def getHotelViewsInThisPage(page):
    outputList = []
    tree = html.fromstring(page.text)
    reviews = list(set(tree.xpath('//div[@class="reviewSelector"]')))
    for _ in reviews:
        tree = html.fromstring(str(tostring(_)))
        # reviewId = list(set(tree.xpath('//@data-reviewid')))
        review_text = list(set(tree.xpath('//p[@class="partial_entry"]')))

        # data['reviewID'] = reviewId[0]
        # data['review'] = review_text[0].text
        outputList.append(review_text[0].text)
    return outputList


def getAllHotelReviews(city, hotel_link):
    hotel_name = get_hotel_name(hotel_link)
    hotel_link = tripadvisor + hotel_link
    response_hotel_page = Session.get(hotel_link)
    tree = html.fromstring(response_hotel_page.text)
    print('second')
    hotel_page = openHotelPage(hotel_link)
    try:
        page_numbers = list(set(tree.xpath(
            '//div[@id="REVIEWS"]//div[contains(concat( " ", @class, " " ), concat( " ", "ui_pagination", '
            '" " ))]/div/a/@data-page-number')))
        page_numbers = max(list(map(int, page_numbers)))
    except:
        page_numbers = -1

    print('page_numbers: ', page_numbers)
    list_views = getHotelViewsInThisPage(hotel_page)

    insert_city_hotel_review_list(city, hotel_name, list_views)

    if page_numbers != -1:
        for i in range(1, page_numbers):
            print('page: ', str(i))
            next_hotel_page = hotel_link[:hotel_link.find('-Reviews-')] \
                              + '-or' + str(i*5) + '-' \
                              + hotel_link[hotel_link.find('-Reviews-') + 9:]
            list_views = getHotelViewsInThisPage(openHotelPage(next_hotel_page))
            add_reviews_to_hotel_list(city, hotel_name, list_views)

    return list_views


def get_hotel_name(hotel_link):
    return hotel_link[hotel_link.find('-Reviews-') + 9: hotel_link.find('-', hotel_link.find('-Reviews-') + 9)]
