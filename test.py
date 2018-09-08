from parsers.city import City
from parsers.hotel import Hotel
from parsers.resturant import Resturant
from parsers.thingtodo import ThingToDo
from parsers.user import User
from parsers.vacationrental import VacationRental

#from TripAdvDatabase import TripAdvDatabase

city = City()
## db_ = TripAdvDatabase()
## db_.connect_to('tripadvisor','reveiws')
## db_.correct_reveiew_texts_for_csv()
## print("done")
# city.set_city('Tehran')
# if city.uri == '':
#     print('cannot load paris page')
#     exit(1)

# city.start()
# print(hamedan.get_all_resturant_in_city())

# hotel = Hotel()
# hotel.set_hotel(hamedan.get_all_hotels_in_city()[0])
# print(hotel.get_hotel_name())
# print(hotel.get_all_hotel_reviews())

# resturant = Resturant()
# resturant.set_database(db_)
# resturant.set_city_name(city.name)
# resturant.set_resturant('https://www.tripadvisor.com/Hotel_Review-g294217-d1235711-Reviews-Dorsett_Mongkok_Hong_Kong-Hong_Kong.html')
# print(resturant.get_resturant_name())
#
# resturant.get_all_resturant_reviews()

# vacation_rental = VacationRental()
# vacation_rental.set_vacation_rental(hamedan.get_all_vacation_rental_in_city()[0])
#
# print(vacation_rental.get_vacation_rental_name)
# print(vacation_rental.get_all_vacation_rental_reviews())
#
# user = User()
# user.set_user_id('32FAC1394D12463BEF002F045BED0CCC')
# print(user.user_link)
# print(user.name)
# print(user.leve_of_contribor)
# print(user.n_contributions)
# print(user.n_cities_visited)
# print(user.n_helpful_votes)
# print('user.from_city: ', user.from_city)


# thing_to_do = ThingToDo()
# thing_to_do.set_thing_to_do('https://www.tripadvisor.ca/Attraction_Review-g187147-d189796-Reviews-8th_Arrondissement-Paris_Ile_de_France.html')
# print(thing_to_do.name)
# print(thing_to_do.get_all_thing_to_do_reviews())
