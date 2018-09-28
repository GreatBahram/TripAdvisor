# Standard library imports
import csv
import glob
import logging
import os
import sys


def save_csv_file(csv_file_path, data, type_, city=None):
    """ Save dictionaries as csv file """
    skip = False
    different_types = ('restaurant', 'hotel', 'city', 'thingtodo', 'vacational_rental', 'overall')
    if type_ in different_types and data != []:
        if type_ == 'overall': 
            csv_file_path = csv_file_path + '.csv'
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
            if os.path.exists(csv_file_path):
                csv_file = open('{}'.format(csv_file_path), mode='at')
                skip = True
            else:
                csv_file = open('{}'.format(csv_file_path), mode='wt')

            with csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=['city', 'restaurant','user_id', 'date', 'rate', 'title', 'review_text']) 
                if not skip:
                    writer.writeheader()
                for review in data:
                    review['city'] = city
                    writer.writerow(review)
        elif type_ == 'hotel':
            csv_file_path = csv_file_path + '.csv'
            if os.path.exists(csv_file_path):
                csv_file = open('{}'.format(csv_file_path), mode='at')
                skip = True
            else:
                csv_file = open('{}'.format(csv_file_path), mode='wt')

            with csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=['city', 'hotel','user_id', 'review_date', 'stayed_date', \
                        'trip_type', 'Service', 'Cleanliness', 'SleepQuality', 'rate', 'title', 'review_text']) 
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

def accumulator(integrated_csv_file, all_csv_files, header, remove=False):
    """ accumualte all csv file into one file and remove separated files (optioanl)"""
    with open(integrated_csv_file, mode='wt') as output_file:
        output_file.write(header)
        for csv_file in glob.glob(all_csv_files):
            with open(csv_file, mode='rt') as input_file:
                next(input_file, None) # skip default header
                for line in input_file:
                    output_file.write(line)
    if remove:
        for csv_file in glob.glob(all_csv_files):
            os.remove(csv_file)
        os.rmdir(os.path.dirname(all_csv_files))
    return None
