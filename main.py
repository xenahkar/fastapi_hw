from enum import Enum
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
import time
from typing import List, Union, Optional


app = FastAPI()


class DogType(str, Enum):
    terrier = "terrier"
    bulldog = "bulldog"
    dalmatian = "dalmatian"


class Dog(BaseModel):
    name: str
    pk: int
    kind: DogType


class Timestamp(BaseModel):
    id: int
    timestamp: int


dogs_db = {
    0: Dog(name='Bob', pk=0, kind='terrier'),
    1: Dog(name='Marli', pk=1, kind="bulldog"),
    2: Dog(name='Snoopy', pk=2, kind='dalmatian'),
    3: Dog(name='Rex', pk=3, kind='dalmatian'),
    4: Dog(name='Pongo', pk=4, kind='dalmatian'),
    5: Dog(name='Tillman', pk=5, kind='bulldog'),
    6: Dog(name='Uga', pk=6, kind='bulldog')
}

post_db = [
    Timestamp(id=0, timestamp=12),
    Timestamp(id=1, timestamp=10)
]


@app.get('/')
def root():
    return 'Successful Response'


@app.post('/post', response_model=Timestamp, summary='Get Post')
def post():
    if len(post_db) > 0:
        last_post_id = post_db[-1].id
        new_post = Timestamp(id=last_post_id+1, timestamp=int(time.time()))
    else:
        new_post = Timestamp(id=0, timestamp=int(time.time()))
    post_db.append(new_post)
    return new_post


@app.get('/dog', response_model=List[Dog], summary='Get Dogs')
def get_dog(kind: Optional[Union[str, None]] = None):
    if kind is None:
        return list(dogs_db.values())
    if kind in DogType._member_names_:
        return [dog for dog in dogs_db.values() if dog.kind == kind]
    else:
        raise HTTPException(status_code=422,
                            detail={'loc': 'kind',
                                    'msg': f'Oops! No dog breed {kind} in database.',
                                    'type': "error"})


@app.post('/dog', response_model=Dog, summary='Create Dog')
def create_dog(dog: Dog):
    if dog.pk in dogs_db:
        raise HTTPException(status_code=422,
                            detail={'loc': 'pk',
                                    'msg': f'Oops! The specified PK already exists.',
                                    'type': "error"})
    last_dog_index = list(dogs_db.keys())[-1]
    dogs_db[last_dog_index+1] = dog
    return dog


@app.get('/dog/{pk}', response_model=Dog, summary='Get Dog By Pk')
def get_dog_by_pk(pk: int):
    if pk in dogs_db:
        dog = dogs_db[pk]
        return dog
    else:
        raise HTTPException(status_code=422, detail={'loc': 'pk',
                                                     'msg': f'Oops! No dog with pk {pk} in database.',
                                                     'type': "error"})


@app.patch('/dog/{pk}', response_model=Dog, summary='Update Dog')
def update_dog(pk: int, dog: Dog):
    if pk in dogs_db:
        dogs_db[pk] = dog
        return dog
    else:
        raise HTTPException(status_code=422,
                            detail={'loc': 'pk',
                                    'msg': f'Oops! No dogs with PK {pk} in database.',
                                    'type': "error"})