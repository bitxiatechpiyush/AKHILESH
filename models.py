from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

db = PyMongo()

class User:
    def __init__(self, username, password, user_type):
        self.username = username
        self.password = password
        self.user_type = user_type
        self.firstname = 'default'
        self.lastname = 'default'
        self.license_no = 'default'
        self.age = 0
        self.car_details = {
            'make': 'default',
            'model': 'default',
            'year': 0,
            'platno': 'default'
        }

    def save(self):
        db.db.users.insert_one(self.__dict__)

    @staticmethod
    def find_one(query):
        return db.db.users.find_one(query)

    @staticmethod
    def update_one(query, update):
        db.db.users.update_one(query, update)