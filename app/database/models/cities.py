from app.database.database_connect import *


class City(BaseModel):
    name = TextField(null=False)


db.create_tables([City])
