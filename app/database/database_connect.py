from peewee import *

try:
    db = PostgresqlDatabase('modul_db', user='postgres', password='О1azSd*', host='localhost', port=5432)
    print(":)")
except:
    print(":(")


class BaseModel(Model):
    class Meta:
        database = db


db.create_tables([BaseModel])
