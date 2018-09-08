import threading
import time

from dbhelper import TripAdvDatabase
from parsers.city import City
from parsers.hotel import Hotel
from parsers.restaurant import Restaurant
from parsers.user import User
from parsers.vacationrental import VacationRental
from ThingToDo import ThingToDo


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), int(n)):
        yield l[i:i + int(n)]

city = City()
db_ = TripAdvDatabase()
db_.connect_to('tripadvisor','reveiws')
mydb = db_.get_db()
result_col = mydb['add_results']
hotel_completed = mydb['hotel_completed']
resturant_completed = mydb['resturant_completed']
vacation_rental_completed = mydb['vacation_rental']
thing_to_do_completed = mydb['thing_to_do']

city_list = [
        'Tehran', 'Hong Kong', 'Bangkok', 'London', 'Singapore', 'Macau', 'Dubai', 'Paris', 'New York', 'Shenzhen', 'Kuala Lumpur', 'Phuket',
        'Rome', 'Tokyo', 'Taipei', 'Istanbul', 'Seoul', 'Guangzhou', 'Prague', 'Mecca', 'Miami', 'Delhi', 'Mumbai', 'Barcelona', 'Pattaya', 'Shanghai',
        'Las Vegas', 'Milan', 'Amsterdam', 'Antalya', 'Vienna', 
        ]

def get_hotels(hotel_link_list,city_name ):
        hotel = Hotel()
        hotel.set_database(db_)
        hotel.set_city_name(city.name)
        n_all_rw = 0;
        for link in hotel_link_list:
            try:
                hotel.set_hotel(link)
                hotel.get_all_hotel_reviews()
                result_col.insert({'city': city_name, 'link_of_place': link, 'number_of_reveiws': hotel.get_review_count()})
                n_all_rw += hotel.get_review_count()
            except Exception as e:
                continue
        hotel_completed.insert({'city': city_name, 'all_hotel_review_count': n_all_rw})

def get_resturants(resturant_link_list,city_name) :
        resturant = Restaurant()
        resturant.set_database(db_)
        resturant.set_city_name(city.name)
        n_all_rw = 0;
        for link in resturant_link_list:
            try:
                resturant.set_resturant(link)
                resturant.get_all_resturant_reviews()
                result_col.insert({'city': city_name,'link_of_place': link,'number_of_reveiws': resturant.get_review_count()})
                n_all_rw += resturant.get_review_count()
            except Exception as e:
                continue
        resturant_completed.insert({'city': city_name, 'all_resturant_review_count': n_all_rw})

def get_vacation_rental(vacation_rental_link_list,city_name):
        vacation_rental = VacationRental()
        vacation_rental.set_database(db_)
        vacation_rental.set_city_name(city.name)
        n_all_rw = 0;
        for link in vacation_rental_link_list:
            try:
                vacation_rental.set_vacation_rental(link)
                vacation_rental.get_all_vacation_rental_reviews()
                result_col.insert({'city': city_name,'link_of_place': link,'number_of_reveiws': vacation_rental.get_review_count()})
                n_all_rw += vacation_rental.get_review_count()
            except Exception as e:
                continue
        vacation_rental_completed.insert({'city': city_name, 'all_vacation_rental_review_count': n_all_rw})

def get_thing_to_do(thing_to_do_link_list,city_name):
        thing_to_do = ThingToDo()
        thing_to_do.set_database(db_)
        thing_to_do.set_city_name(city.name)
        n_all_rw = 0;
        for link in thing_to_do_link_list:
            try:
                thing_to_do.set_thing_to_do(link)
                thing_to_do.get_all_thing_to_do_reviews()
                result_col.insert({'city': city_name,'link_of_place': link,'number_of_reveiws': thing_to_do.get_review_count()})
                n_all_rw += thing_to_do.get_review_count()
            except Exception as e:
                continue
        thing_to_do_completed.insert({'city': city_name, 'all_thing_to_do_review_count': n_all_rw})

def main():
        city_name = 'Tehran'
        print("Start adding reveiws for the city: {}".format(city_name))
        city.set_city(city_name)
        if city.uri == '':
            print('cannot load {} page'.format(city_name))
            exit(1)
        city.start()

        hotel_link_list = city.get_all_hotels_in_city()
        print("Number of hotels in {} : {}".format(city_name, len(hotel_link_list)))
        hotel_link_list_list = []
        if(len(hotel_link_list) > 10) :
            hotel_link_list_list = chunks(hotel_link_list,len(hotel_link_list)/10)
        else:
            hotel_link_list_list = chunks(hotel_link_list,1)

        for list_ in hotel_link_list_list:
            t = threading.Thread(target=get_hotels,args =(list_,city_name))
            t.daemon = True
            t.start()

        resturant_link_list = city.get_all_resturant_in_city()
        print("Number of resturants in {} : {}".format(city_name, len(resturant_link_list)))
        resturant_link_list_list = []
        if(len(resturant_link_list) > 10) :
            resturant_link_list_list = chunks(resturant_link_list,len(resturant_link_list)/10)
        else:
            resturant_link_list_list = chunks(resturant_link_list,1)
        for list_ in resturant_link_list_list:
            t = threading.Thread(target=get_resturants,args =(list_,city_name))
            t.daemon = True
            t.start()

        vacation_rental_link_list = city.get_all_vacation_rental_in_city()
        print("Number of vacation_rental in {} : {}".format(city_name, len(vacation_rental_link_list)))
        vacation_rentalt_link_list_list = []
        if(len(vacation_rental_link_list) > 10) :
            vacation_rentalt_link_list_list = chunks(vacation_rental_link_list,len(vacation_rental_link_list)/10)
        else:
            vacation_rentalt_link_list_list = chunks(vacation_rental_link_list,1)
        for list_ in vacation_rentalt_link_list_list:
            t = threading.Thread(target=get_vacation_rental,args =(list_,city_name))
            t.daemon = True
            t.start()

        thing_to_do_link_list = city.get_all_thing_to_do_in_city()
        print("Number of thing_to_do in {} : {}".format(city_name, len(thing_to_do_link_list)))
        thing_to_do_link_list_list = []
        if(len(thing_to_do_link_list) > 10) :
            thing_to_do_link_list_list = chunks(thing_to_do_link_list,len(thing_to_do_link_list)/10)
        else:
            thing_to_do_link_list_list = chunks(thing_to_do_link_list,1)

        for list_ in thing_to_do_link_list_list:
            t = threading.Thread(target=get_thing_to_do,args =(list_,city_name))
            t.daemon = True
            t.start()

        while 1:
            hotels_done = 0;
            resturants_done = 0;
            vacation_rental_done = 0;
            thing_to_do_done = 0;
            res = hotel_completed.find()
            for r in res:
                hotels_done += 1;
            res = resturant_completed.find()
            for r in res:
                resturants_done += 1;
            res = thing_to_do_completed.find()
            for r in res:
                thing_to_do_done += 1;
            res = vacation_rental_completed.find()
            for r in res:
                vacation_rental_done += 1;

            if ((hotels_done == len(hotel_link_list_list)) and (resturants_done == len(resturant_link_list_list)) and (vacation_rental_done == len(vacation_rentalt_link_list_list)) and (thing_to_do_done == len(thing_to_do_link_list_list))) :
                print("ALL DONE FOR CITY {}".format(city_name))
                exit(0)
            time.sleep(5)

if __name__ == "__main__": main()
