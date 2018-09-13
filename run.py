import argparse
import os
import sys
from multiprocessing.dummy import Pool

import redis

# local imports
from parsers.city import CityParser
from parsers.overall import overall_review_numbers
from parsers.restaurant import RestaurantParser
from utils import return_logger, save_csv_file, remove_parenthesis

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
current_city_path = ''

logger = return_logger(__name__)

redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)

def restaurant_helper(link):
    global current_city_path
    restaurant_parser = RestaurantParser(link)
    restaurant_name = restaurant_parser.get_name()
    city_name = current_city_path.split('/')[-1].lower()
    redis_output = redis_db.get('{}'.format(restaurant_name + '@' + city_name))
    if not redis_output:
        logger.info("Getting {}'s restaurant data...".format(restaurant_name))
        restaurant_reviews = restaurant_parser.get_all_reviews()
        redis_db.incr('{}'.format(restaurant_name + '@' + city_name))
        if restaurant_reviews:
            filename =  restaurant_name 
            csv_file_path = os.path.join(current_city_path, filename)
            save_csv_file(csv_file_path, restaurant_reviews, 'restaurant')
            logger.info(' -> Storing reviews for {} restaurant...'.format(restaurant_name))
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
        parser.add_argument('cityname', help='City name cannot left be blank!')
        args = parser.parse_args(sys.argv[2:])

        cityname = args.cityname.title()

        city = CityParser(cityname)
        logger.info("Getting {}'s restaurants...".format(city.name))

        if city.uri:
            city.start()
            global current_city_path
            current_city_path = os.path.join(CURRENT_PATH, 'data', 'restaurant', city.name)
            os.makedirs(current_city_path, exist_ok=True)
            restaurant_links = city.get_all_resturant_in_city()
            logger.info('Total restaurant in {} is : {}'.format(cityname, len(restaurant_links)))
            pool = Pool(5)
            results = pool.map(restaurant_helper, restaurant_links)

        else:
            logger.info('{} city not found'.format(cityname))
            exit(1)

    def overall(self):
        parser = argparse.ArgumentParser(
            description='overall information about the city ')
        # NOT prefixing the argument with -- means it's not optional
        parser.add_argument('cityname')
        args = parser.parse_args(sys.argv[2:])
        cityname = args.cityname.title()

        city = CityParser(cityname)
        logger.info("Getting {}'s restaurants...".format(city.name))

        if city.uri:
            data = city._openpage(city.uri)
            if data:
                global current_city_path
                current_city_path = os.path.join(CURRENT_PATH, 'data', 'overall')
                os.makedirs(current_city_path, exist_ok=True)
                overall_result = overall_review_numbers(data, city.uri, cityname)
                overall_result = remove_parentheses(overall_result)
                current_city_path = os.path.join(current_city_path, cityname)
                save_csv_file(current_city_path, overall_result, 'overall')
                print('\n'.join(" - {}: {}".format(key, value) for key, value in overall_result.items()))
        else:
            logger.info('{} city not found'.format(cityname))
            exit(1)

if __name__ == '__main__':
    TripCli()
