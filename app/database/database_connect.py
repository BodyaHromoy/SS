from peewee import *

try:
    db = PostgresqlDatabase('testik6', user='bogdanafter', password='bogdanafter', host='192.168.1.206', port=5432)
    print(":)")
except:
    print(":(")

try:
    db2 = PostgresqlDatabase('testik7', user='bogdanafter', password='bogdanafter', host='192.168.1.206', port=5432)
    print(":)")
except:
    print(":(")


class BaseModel(Model):
    class Meta:
        database = db


class BaseModel2(Model):
    class Meta:
        database = db2


db2.create_tables([BaseModel2])
