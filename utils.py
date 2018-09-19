import csv
import logging
import os
import sys


def save_csv_file(csv_file_path, data, type_, city=None):
    """ Save dictionaries as csv file """

    different_types = ('restaurant', 'hotel', 'city', 'thingtodo', 'vacational_rental', 'overall')
    if type_ in different_types and data != []:
        if type_ == 'overall': 
            csv_file_path = csv_file_path + '.csv'
            skip = False
            if os.path.exists(csv_file_path):
                csv_file = open('{}'.format(csv_file_path), mode='at')
                skip = True
            else:
                csv_file = open('{}'.format(csv_file_path), mode='wt')

            with csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=list(data.keys())) 
                if not skip:
                    writer.writeheader()
                writer.writerow(data)
        elif type_ == 'restaurant':
            csv_file_path = csv_file_path + '.csv'
            skip = False

            if os.path.exists(csv_file_path):
                csv_file = open('{}'.format(csv_file_path), mode='at')
                skip = True
            else:
                csv_file = open('{}'.format(csv_file_path), mode='wt')

            with csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=['city', 'restaurant', 'title', 'review_text', 'user_id', 'date']) 
                if not skip:
                    writer.writeheader()
                for review in data:
                    review['city'] = city
                    writer.writerow(review)
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

def remove_parenthesis(dictionary):
    """ remove () from the value"""
    for key in dictionary:
        value = dictionary[key]
        if type(value) == str:
            new_value = value.replace('(', '')
            new_value = new_value.replace(')', '')
            dictionary[key] = new_value
        else:
            continue
    return dictionary
