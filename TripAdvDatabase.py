import pymongo
import urllib
from datetime import datetime


class TripAdvDatabase:

    def __init__(self):
        self.username = 'admin'
        self.password = urllib.parse.quote_plus('9X00DfaColorfullGP(d12@l4l')
        self.db_address = 'mongodb://' + self.username + ':' + self.password + '@88.99.153.217:23727/admin?authSource=admin'

    def get_db(self):
        return  self.mydb

    def connect_to(self,database_name,collection_name):
        try:
            myclient = pymongo.MongoClient(self.db_address)
            self.mydb = myclient[database_name]
            self.collection = self.mydb[collection_name]
        except Exception as e:
            print(e)
            exit(0)

    def add_reveiw(self, review_text, title, rating_date, rate_value, stay_date, user_id, type_of_place, name_of_place, city_name):
        stay_date_obj = datetime(2000,1,1,1,1,1)
        rating_date_obj = ''

        if len(rating_date) != 0:
            rating_date_obj = datetime.strptime(rating_date, '%B %d, %Y')
        else :
            print('rating date is empty, failed to add to DB')
            return
        if len(stay_date) != 0:
            try:
                stay_date_obj = datetime.strptime(stay_date, '%B %d, %Y')
            except:
                stay_date_obj = datetime(2000, 1, 1, 1, 1, 1)

        self.collection.insert({
            'city': city_name,
            'type_of_place': type_of_place,
            'name_of_place': name_of_place,
            'user_id': user_id,
            'stay_date': stay_date_obj,
            'rating_date': rating_date_obj,
            'rate': rate_value,
            'title': title,
            'review_text': review_text
        })

    def correct_reveiew_texts_for_csv(self):
        res = self.collection.find()
        for r in res:
            text = r['review_text']
            text_ = text.replace(","," ")
            self.collection.update_one({
                '_id': r['_id']
            }, {
                '$set': {
                    'review_text': text_
                }
            }, upsert=False)


