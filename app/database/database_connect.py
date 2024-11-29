from peewee import *

try:
    db = PostgresqlDatabase('test1', user='postgres', password='1337', host='192.168.1.98', port=5432)
    print(":)")
except:
    print(":(")

try:
    db2 = PostgresqlDatabase('test2', user='postgres', password='1337', host='192.168.1.98', port=5432)
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
