import argparse
import csv
import logging
import os
import sys

from parsers.city import CityParser
from parsers.hotel import HotelParser
from parsers.restaurant import RestaurantParser
from parsers.thingtodo import ThingToDoParser
from parsers.user import UserParser
from parsers.vacationrental import VacationRentalParser

#from TripAdvDatabase import TripAdvDatabase
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

def main():
    # instantiate and argument parser
    parser = argparse.ArgumentParser(description='a simple CLI for trip adviser information gathering',)
    parser.add_argument('cityname', help='City name cannot left be blank!')
    data = parser.parse_args()

    # instantiate and config logger
    logger = logging.getLogger(__name__)
    logformat = '%(asctime)-12s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig( format=logformat, datefmt='%y/%m/%d %H-%M', level=logging.INFO)

    cityname = data.cityname.title()

    city = CityParser(cityname)
    logger.info("Getting {}'s restaurants...".format(city.name))

    if city.uri:
        city.start()
        current_city_path = os.path.join(CURRENT_PATH, 'data', city.name)
        os.makedirs(current_city_path, exist_ok=True)
        restaurant_links = city.get_all_resturant_in_city()
        logger.info('Total restaurant in {} is : {}'.format(cityname, len(restaurant_links)))
        restaurant_with_name = 0
        for link in restaurant_links:
            restaurant_parser = RestaurantParser(link)
            restaurant_name = restaurant_parser.get_name()
            logger.info('Getting reviews for {} restaurant'.format(restaurant_name))
            restaurant_reviews = restaurant_parser.get_all_reviews()
            if restaurant_reviews:
                filename =  restaurant_name + '.csv'
                csv_file_path = os.path.join(current_city_path, filename)
                csv_file = open('{}'.format(csv_file_path), mode='wt')
                with csv_file:
                    field_names = ['user_id', 'date', 'title', 'review_text']
                    writer = csv.DictWriter(csv_file, fieldnames=field_names) 
                    writer.writeheader()
                    for review in restaurant_reviews:
                        review_text = review['review_text']
                        review_title = review['title']
                        review_date = review['rating_date']
                        review_userid = review['user_id']
                        writer.writerow( { 'user_id' : review_userid, 'date': review_date, 'title': review_title, 'review_text': review_text, })
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
