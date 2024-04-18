from app.database.models.cities import *


class Cabinet(BaseModel):
    city = ForeignKeyField(City, backref='cabinets', on_delete='CASCADE')
    location = TextField(null=False)
    readable_name = TextField(null=False)


db.create_tables([Cabinet])
