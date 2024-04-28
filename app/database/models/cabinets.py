from app.database.database_connect import *


class Ss_main_cabinet(BaseModel):
    city = CharField(null=False)
    shkaf_id = CharField(unique=True)
    zone = CharField()
    location = CharField()
    street = CharField()
    extra_inf = CharField()


db.create_tables([Ss_main_cabinet])
