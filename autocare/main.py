from fastapi import FastAPI
from pony.orm import Database, PrimaryKey, Required, db_session

app = FastAPI()

db = Database()


class MyEntity(db.Entity):
    id = PrimaryKey(int, auto=True)
    attr1 = Required(str)


db.bind(provider="mysql", host="127.0.0.1", user="root", passwd="passwd", db="autocare")
db.generate_mapping(create_tables=True)


@app.post("/add_entity")
def add(attr1: str):
    add_entity(attr1)


@app.get("/get_entity/{entity_id}")
def get(entity_id: int):
    return get_entity(entity_id)


@db_session
def add_entity(attr1: str):
    try:
        MyEntity(attr1=attr1)
        return "Entity added"
    except Exception as e:
        return str(e)


@db_session
def get_entity(entity_id: int):
    entity = MyEntity.get(id=entity_id)
    return entity.attr1
