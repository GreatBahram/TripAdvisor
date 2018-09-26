"""
This is a simple doctest for overall module, in order to run it use : python3 overall.py

>>> import requests
>>> url = 'https://www.tripadvisor.com/Tourism-g946401-Gorgan_Golestan_Province-Vacations.html'
>>> data = requests.get(url)
>>> data.status_code
200
>>> overall_review_numbers(data.text, url, 'Gorgan')
{'num_of_vactionalrentals': 0, 'vacationalrentals_reviews': 0, 'num_of_restaurants': '(5)', 'restaurants_reviews': '26', 'num_of_hotels': '(6)', 'hotels_reviews': '65', 'num_of_thingstodo': '(6)', 'thingstodo_reviews': '77', 'forum': '6', 'flights': 0, 'URL': 'https://www.tripadvisor.com/Tourism-g946401-Gorgan_Golestan_Province-Vacations.html', 'city': 'Gorgan'}
"""
from bs4 import BeautifulSoup

def overall_review_numbers(html_codes, uri, city):
    """ """
    soup = BeautifulSoup(html_codes, 'html.parser')
    overall_dict = {
            'num_of_vactionalrentals': '.vacationRentals  .typeQty',
            'vacationalrentals_reviews': '.vacationRentals .contentCount',
            'num_of_restaurants': '.restaurants .typeQty',
            'restaurants_reviews': '.restaurants .contentCount',
            'num_of_hotels': '.hotels .typeQty',
            'hotels_reviews': '.hotels .contentCount',
            'num_of_thingstodo': '.attractions  .typeQty',
            'thingstodo_reviews': '.attractions .contentCount',
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

if __name__ == '__main__':
    import doctest
    doctest.testmod()
