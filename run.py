# Standard library imports
import argparse
import os
import sys
from multiprocessing.dummy import Pool

# Third party imports
import redis

# Local imports
from parsers.city import CityParser
from parsers.hotel import HotelParser
from parsers.overall import overall_review_numbers
from parsers.restaurant import RestaurantParser
from utils import accumulator, remove_parenthesis, return_logger, save_csv_file

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
current_city_path = ''

logger = return_logger(__name__)

redis_db = redis.StrictRedis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)

def restaurant_helper(link):
    global current_city_path
    restaurant_parser = RestaurantParser(link)
    restaurant_name = restaurant_parser.get_name()
    city_name = current_city_path.split('/')[-1].lower()
    if not redis_db.sismember('{}_restaurnat:'.format(city_name), restaurant_name):
        logger.info("Getting {}'s data...".format(restaurant_name))
        restaurant_reviews = restaurant_parser.get_all_reviews()
        if restaurant_reviews:
            logger.info(' -> Storing reviews for {} restaurant...'.format(restaurant_name))
            csv_file_path = os.path.join(current_city_path, restaurant_name)
            save_csv_file(csv_file_path, restaurant_reviews, 'restaurant', city=city_name)
        redis_db.sadd('{}_restaurnat:'.format(city_name), restaurant_name)
    else:
        logger.info('Skipping {} restaurant since it has already downloaded...'.format(restaurant_name))

def hotel_helper(link):
    global current_city_path
    hotel_parser = HotelParser(link)
    hotel_name = hotel_parser.get_name()
    city_name = current_city_path.split('/')[-1].lower()
    if not redis_db.sismember('{}_hotel:'.format(city_name), hotel_name):
        logger.info("Getting {}'s data...".format(hotel_name))
        hotel_reviews = hotel_parser.get_all_reviews()
        if hotel_reviews:
            logger.info(' -> Storing reviews for {} restaurant...'.format(hotel_name))
            csv_file_path = os.path.join(current_city_path, hotel_name)
            save_csv_file(csv_file_path, hotel_reviews, 'hotel', city=city_name)
        redis_db.sadd('{}_hotel:'.format(city_name), hotel_name)
    else:
        logger.info('Skipping {} restaurant since it has already downloaded...'.format(hotel_name))


class TripCli():
    num_of_threads = 5

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Trip Advisor cli',
            usage='''test.py <command> [<cityname>]
The most commonly used trip advisor commands are:
   restaurant     Gather all reviews for given city
   overall      Gather overall information for each city
   hotel      Gather hotel information for each city
''')
        parser.add_argument('command', help='Subcommand to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            logger.error('Unrecognized command')
            #parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def restaurant(self):
        parser = argparse.ArgumentParser( description='Gather restaurant information for given city')
        parser.add_argument('cityname', help='City name cannot left be blank!', nargs='*')
        args = parser.parse_args(sys.argv[2:])
        for city in args.cityname:
            cityname = city.lower()
            city_parser = CityParser(cityname)
            logger.info("Getting {}'s restaurants...".format(city_parser.name))
            if city_parser.uri:
                city_parser.start()
                global current_city_path
                redis_list_name = '{}_restaurant:links'.format(cityname)
                if redis_db.llen(redis_list_name):
                    restaurant_links = redis_db.lrange(redis_list_name, 0 , -1)
                else:
                    restaurant_links = city_parser.get_all_resturant_in_city()
                    redis_db.lpush(redis_list_name, *restaurant_links)
                logger.info('Total restaurant in {} is : {}'.format(cityname, len(restaurant_links)))
                current_city_path = os.path.join(CURRENT_PATH, 'data', 'restaurant', cityname)
                os.makedirs(current_city_path, exist_ok=True)
                pool = Pool(TripCli.num_of_threads)
                pool.map(restaurant_helper, restaurant_links)
                integrated_reviews = os.path.join(CURRENT_PATH, 'data', 'restaurant', cityname) + '.csv'
                all_csv_files = os.path.join(current_city_path, '*.csv')
                header = 'city,restaurant,title,review_text,user_id,date\n'
                accumulator(integrated_reviews, all_csv_files, header)
            else:
                logger.info('{} city not found'.format(cityname))
                exit(1)

    def overall(self):
        parser = argparse.ArgumentParser(
            description='overall information about the city ')
        # NOT prefixing the argument with -- means it's not optional
        parser.add_argument('cityname', help='city cannot left be blank!', nargs='*')
        args = parser.parse_args(sys.argv[2:])
        for city in args.cityname:
            cityname = city.title()
            city_parser = CityParser(cityname)
            logger.info("Getting {}'s restaurants...".format(city_parser.name))

            if city_parser.uri:
                #data = city_parser._openpage(city_parser.uri)
                city_parser.start()
                #print(city_parser.vacation_rentals_link)
                data = city_parser._openpage(city_parser.vacation_rentals_link)
                if data:
                    global current_city_path
                    current_city_path = os.path.join(CURRENT_PATH, 'data', 'overall') 
                    os.makedirs(current_city_path, exist_ok=True)
                    overall_result = overall_review_numbers(data, city_parser.uri, cityname)
                    overall_result = remove_parenthesis(overall_result)
                    current_city_path = os.path.join(current_city_path, 'overall') 
                    save_csv_file(current_city_path, overall_result, 'overall')
                    print('\n'.join(" - {}: {}".format(key, value) for key, value in overall_result.items()))
            else:
                logger.info('{} city not found'.format(cityname))
                exit(1)

    def hotel(self):
        parser = argparse.ArgumentParser( description='Gather hotel information for given city')
        parser.add_argument('cityname', help='City name cannot left be blank!', nargs='*')
        args = parser.parse_args(sys.argv[2:])
        for city in args.cityname:
            cityname = city.lower()
            city_parser = CityParser(cityname)
            logger.info("Getting {}'s hotels...".format(city_parser.name))
            if city_parser.uri:
                city_parser.start()
                global current_city_path
                redis_list_name = '{}_hotel:links'.format(cityname)
                if redis_db.llen(redis_list_name):
                    hotel_links = redis_db.lrange(redis_list_name, 0 , -1)
                else:
                    hotel_links = city_parser.get_all_hotels_in_city()
                    redis_db.lpush(redis_list_name, *hotel_links)
                logger.info('Total hotel in {} is : {}'.format(cityname, len(hotel_links)))
                current_city_path = os.path.join(CURRENT_PATH, 'data', 'hotel', cityname)
                os.makedirs(current_city_path, exist_ok=True)
                pool = Pool(5)
                pool.map(hotel_helper, hotel_links)
                integrated_reviews = os.path.join(CURRENT_PATH, 'data', 'hotel', cityname) + '.csv'
                all_csv_files = os.path.join(current_city_path, '*.csv')
                header = 'city,restaurant,user_id,date,rate,title,review_text\n'
                accumulator(integrated_reviews, all_csv_files, header)
            else:
                logger.info('{} city not found'.format(cityname))
                exit(1)

if __name__ == '__main__':
    TripCli()
