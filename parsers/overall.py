from collections import namedtuple

from bs4 import BeautifulSoup

def overall_review_numbers(html_codes, uri, city):
    """ """
    soup = BeautifulSoup(html_codes, 'html.parser')
    overall_dict = {
            'num_of_vactionalrentals': '.vacationrentals  .typeQty',
            'vacationalrentals': '.vacationrentals .contentCount',
            'num_of_restaurants': '.restaurants .typeQty',
            'restaurants': '.restaurants .contentCount',
            'num_of_hotels': '.hotels .typeQty',
            'hotels': '.hotels .contentCount',
            'num_of_thingstodo': '.attractions  .typeQty',
            'thingstodo': '.attractions .contentCount',
            'forum': '.forum .contentCount',
            'flights': '.flights .contentCount', 
            }
    for key in overall_dict:
        try:
            overall_dict[key] = soup.select('{}'.format(overall_dict[key]))[0].getText().split()[0]
        except IndexError:
            overall_dict[key] = 0

    overall_dict['URL'] = uri
    overall_dict['city'] = city

    return overall_dict
