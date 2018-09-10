import csv
import logging
import sys


def save_csv_file(csv_file_path, restaurant_reviews, type_):
    """
    Save dictionaries as csv file
        arguments:
            csv_file_path: 
            data:
            type_: can be one of the ('restaurant', 'hotel', 'city', 'thingtodo', 'vacational_rental')
        returns:
            None
    """
    different_types = ('restaurant', 'hotel', 'city', 'thingtodo', 'vacational_rental')
    if type_ in different_types:
        csv_file_path = csv_file_path + '_' + type_ + '.csv'
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
        logger = return_logger(__name__)
        logger.error("Unknown type") 
        sys.exit(2)

def return_logger(module_name):
    """return a logger object """

    logger = logging.getLogger(module_name)
    logformat = '%(asctime)-12s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig( format=logformat, datefmt='%y/%m/%d %H-%M-%S', level=logging.INFO)

    return logger
