import argparse
import logging
import os
from multiprocessing.dummy import Pool

from parsers.city import CityParser
from parsers.hotel import HotelParser
from parsers.restaurant import RestaurantParser
from parsers.thingtodo import ThingToDoParser
from parsers.user import UserParser
from parsers.vacationrental import VacationRentalParser

# local imports
from utils import return_logger, save_csv_file

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
current_city_path = ''

logger = return_logger(__name__)

def restaurant_helper(link):
    global current_city_path
    restaurant_parser = RestaurantParser(link)
    restaurant_name = restaurant_parser.get_name()
    logger.info('Getting reviews for {} restaurant'.format(restaurant_name))
    restaurant_reviews = restaurant_parser.get_all_reviews()
    if restaurant_reviews:
        filename =  restaurant_name 
        csv_file_path = os.path.join(current_city_path, filename)
        save_csv_file(csv_file_path, restaurant_reviews, 'restaurant')

def main():
    # instantiate and argument parser
    parser = argparse.ArgumentParser(description='a simple CLI for trip adviser information gathering',)
    parser.add_argument('cityname', help='City name cannot left be blank!')
    data = parser.parse_args()

    cityname = data.cityname.title()

    city = CityParser(cityname)
    logger.info("Getting {}'s restaurants...".format(city.name))

    if city.uri:
        city.start()
        global current_city_path
        current_city_path = os.path.join(CURRENT_PATH, 'data', city.name)
        os.makedirs(current_city_path, exist_ok=True)
        restaurant_links = city.get_all_resturant_in_city()
        logger.info('Total restaurant in {} is : {}'.format(cityname, len(restaurant_links)))
        pool = Pool(5)
        results = pool.map(restaurant_helper, restaurant_links)

        #for link in restaurant_links:
        #    restaurant_parser = RestaurantParser(link)
        #    restaurant_name = restaurant_parser.get_name()
        #    logger.info('Getting reviews for {} restaurant'.format(restaurant_name))
        #    restaurant_reviews = restaurant_parser.get_all_reviews()
        #    if restaurant_reviews:
        #        filename =  restaurant_name 
        #        csv_file_path = os.path.join(current_city_path, filename)
        #        save_csv_file(csv_file_path, restaurant_reviews, 'restaurant')
    else:
        logger.info('{} city not found'.format(cityname))
        exit(1)

if __name__ == '__main__':
    main()
## db_ = TripAdvDatabase()
## db_.connect_to('tripadvisor','reveiws')
## db_.correct_reveiew_texts_for_csv()
## print("done")

# city.start()
# print(hamedan.get_all_resturant_in_city())

# hotel = Hotel()
# hotel.set_hotel(hamedan.get_all_hotels_in_city()[0])
# print(hotel.get_hotel_name())
# print(hotel.get_all_hotel_reviews())

# resturant = Resturant()
# resturant.set_database(db_)
# resturant.set_city_name(city.name)
# resturant.set_resturant('https://www.tripadvisor.com/Hotel_Review-g294217-d1235711-Reviews-Dorsett_Mongkok_Hong_Kong-Hong_Kong.html')
# print(resturant.get_resturant_name())
#
# resturant.get_all_resturant_reviews()

# vacation_rental = VacationRental()
# vacation_rental.set_vacation_rental(hamedan.get_all_vacation_rental_in_city()[0])
#
# print(vacation_rental.get_vacation_rental_name)
# print(vacation_rental.get_all_vacation_rental_reviews())
#
# user = User()
# user.set_user_id('32FAC1394D12463BEF002F045BED0CCC')
# print(user.user_link)
# print(user.name)
# print(user.leve_of_contribor)
# print(user.n_contributions)
# print(user.n_cities_visited)
# print(user.n_helpful_votes)
# print('user.from_city: ', user.from_city)

# thing_to_do = ThingToDo()
# thing_to_do.set_thing_to_do('https://www.tripadvisor.ca/Attraction_Review-g187147-d189796-Reviews-8th_Arrondissement-Paris_Ile_de_France.html')
# print(thing_to_do.name)
# print(thing_to_do.get_all_thing_to_do_reviews())
