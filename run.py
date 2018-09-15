import argparse
import os
import sys
from multiprocessing.dummy import Pool

import redis

# local imports
from parsers.city import CityParser
from parsers.overall import overall_review_numbers
from parsers.restaurant import RestaurantParser
from utils import remove_parenthesis, return_logger, save_csv_file

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
current_city_path = ''

logger = return_logger(__name__)

redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)

def restaurant_helper(link):
    global current_city_path
    restaurant_parser = RestaurantParser(link)
    restaurant_name = restaurant_parser.get_name()
    city_name = current_city_path.split('/')[-1].lower()
    if not redis_db.sismember('{}:'.format(city_name), restaurant_name):
        logger.info("Getting {}'s data...".format(restaurant_name))
        restaurant_reviews = restaurant_parser.get_all_reviews()
        redis_db.sadd('{}:'.format(city_name), restaurant_name)
        if restaurant_reviews:
            logger.info(' -> Storing reviews for {} restaurant...'.format(restaurant_name))
            return restaurant_reviews
    else:
        logger.info('Skipping {} restaurant since it has already downloaded...'.format(restaurant_name))


class TripCli(object):
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Trip Advisor cli',
            usage='''test.py <command> [<cityname>]
The most commonly used trip advisor commands are:
   restaurant     Gather all reviews for given city
   overall      Gather overall information for each city
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
                current_city_path = os.path.join(CURRENT_PATH, 'data', 'restaurant')
                os.makedirs(current_city_path, exist_ok=True)
                restaurant_links = city_parser.get_all_resturant_in_city()
                logger.info('Total restaurant in {} is : {}'.format(cityname, len(restaurant_links)))
                pool = Pool(5)
                results = pool.map(restaurant_helper, restaurant_links)
                for result in results:
                    if result:
                        save_csv_file(current_city_path, result, 'restaurant', city=cityname)
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
                data = city_parser._openpage(city_parser.uri)
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

if __name__ == '__main__':
    TripCli()
