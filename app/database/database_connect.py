from peewee import *

try:
    db = PostgresqlDatabase('testik3', user='bogdanafter', password='bogdanafter', host='192.168.1.206', port=5432)
    print(":)")
except:
    print(":(")


class BaseModel(Model):
    class Meta:
        database = db


db.create_tables([BaseModel])
