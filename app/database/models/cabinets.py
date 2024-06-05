from app.database.database_connect import *


class ss_main_vendor(BaseModel):
    vendor_name = CharField(max_length=255, unique=True, null=False)


class ss_main_city(BaseModel):
    city_name = CharField(max_length=255, unique=True, null=False)
    country = CharField(max_length=255, null=False)
    vendor = ForeignKeyField(ss_main_vendor, backref='cities', null=False, on_delete='CASCADE', to_field='vendor_name')


class ss_main_zone(BaseModel):
    zone_name = CharField(max_length=255, unique=True, null=False)
    city = ForeignKeyField(ss_main_city, backref='zones', null=False, on_delete='CASCADE', to_field='city_name')
    vendor = ForeignKeyField(ss_main_vendor, backref='zones', null=False, on_delete='CASCADE', to_field='vendor_name')


class Ss_main_cabinet(BaseModel):
    city = ForeignKeyField(ss_main_city, backref='cabinets', null=False, on_delete='CASCADE', to_field='city_name')
    shkaf_id = CharField(null=False, unique=True, max_length=255)
    zone = ForeignKeyField(ss_main_zone, backref='cabinets', null=False, on_delete='CASCADE', to_field='zone_name')
    location = TextField()
    street = TextField()
    extra_inf = TextField()
    vendor = ForeignKeyField(ss_main_vendor, backref='cabinets', null=False, on_delete='CASCADE',
                             to_field='vendor_name')


db.create_tables([Ss_main_cabinet])
