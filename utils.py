import csv
import logging
import sys


def save_csv_file(csv_file_path, data, type_):
    """ Save dictionaries as csv file """

    different_types = ('restaurant', 'hotel', 'city', 'thingtodo', 'vacational_rental', 'overall')
    if type_ in different_types and data != []:
        csv_file_path = csv_file_path + '_' + type_ + '.csv'
        csv_file = open('{}'.format(csv_file_path), mode='wt')
        if type_ == 'overall': 
            with csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=list(data.keys())) 
                writer.writeheader()
                writer.writerow(data)
        elif type_ == 'restaurant':
            with csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=list(data[0].keys())) 
                writer.writeheader()
                for review in data:
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
