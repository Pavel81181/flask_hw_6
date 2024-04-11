# Задание №6
# Необходимо создать базу данных для интернет-магазина. База данных должна
# состоять из трех таблиц: товары, заказы и пользователи. Таблица товары должна
# содержать информацию о доступных товарах, их описаниях и ценах. Таблица
# пользователи должна содержать информацию о зарегистрированных
# пользователях магазина. Таблица заказы должна содержать информацию о
# заказах, сделанных пользователями.
# ○ Таблица пользователей должна содержать следующие поля: id (PRIMARY KEY),
# имя, фамилия, адрес электронной почты и пароль.
# ○ Таблица товаров должна содержать следующие поля: id (PRIMARY KEY),
# название, описание и цена.
# ○ Таблица заказов должна содержать следующие поля: id (PRIMARY KEY), id
# пользователя (FOREIGN KEY), id товара (FOREIGN KEY), дата заказа и статус
# заказа.
# Погружение в Python
# Задание №6 (продолжение)
# Создайте модели pydantic для получения новых данных и
# возврата существующих в БД для каждой из трёх таблиц
# (итого шесть моделей).
# Реализуйте CRUD операции для каждой из таблиц через
# создание маршрутов, REST API (итого 15 маршрутов).
# ○ Чтение всех
# ○ Чтение одного
# ○ Запись
# ○ Изменение
# ○ Удаление

import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
from typing import List
from datetime import date

DATABASE_URL = "sqlite:///market.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("firstname", sqlalchemy.String(30)),
    sqlalchemy.Column("lastname", sqlalchemy.String(30)),
    sqlalchemy.Column("email", sqlalchemy.String(30)),
    sqlalchemy.Column("password", sqlalchemy.String(20)),
)
products = sqlalchemy.Table(
    "products",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(30)),
    sqlalchemy.Column("description", sqlalchemy.String(100)),
    sqlalchemy.Column("price", sqlalchemy.Float),
)

orders = sqlalchemy.Table(
    "orders",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("product_id", sqlalchemy.Integer, sqlalchemy.ForeignKey('products.id')),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column("date", sqlalchemy.Date()),
    sqlalchemy.Column("status", sqlalchemy.String(30)),
)

engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)

app = FastAPI()

class UserIn(BaseModel):
    firstname: str = Field(..., max_length=30)
    lastname: str = Field(..., max_length=30)
    email: EmailStr = Field(..., max_length=50)
    password: str = Field(..., min_length=5)

class User(UserIn):
    id: int

class ProductIn(BaseModel):
    name: str = Field(..., max_length=30)
    description: str = Field(..., max_length=100)
    price: float

class Product(ProductIn):
    id: int


class OrderIn(BaseModel):
    product_id: int
    user_id: int
    date: date
    status: str = Field(..., max_length=30)


class Order(OrderIn):
    id: int



@app.get("/users/", response_model=List[User])
async def get_users():
    query = users.select()
    return await database.fetch_all(query)

@app.get("/users/{user_id}", response_model=User)
async def get_users(users_id: int):
    query = users.select().where(users.c.id == users_id)
    return await database.fetch_one(query)

@app.post("/users/", response_model=User)
async def create_user(user: UserIn):
        query = users.insert().values(**user.model_dump())
        last_record_id = await database.execute(query)
        return {**user.model_dump(), "id": last_record_id}

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, new_user: UserIn):
        query = users.update().where(users.c.id == user_id).values(**new_user.model_dump())
        await database.execute(query)
        return {**new_user.model_dump(), "id": user_id}

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
        query = users.delete().where(users.c.id == user_id)
        await database.execute(query)
        return {'message': 'User deleted'}

@app.get("/products/", response_model=List[Product])
async def get_products():
    query = products.select()
    return await database.fetch_all(query)

@app.get("/products/{product_id}", response_model=Product)
async def get_products(product_id: int):
    query = products.select().where(products.c.id == product_id)
    return await database.fetch_one(query)

@app.post("/products/", response_model=Product)
async def create_product(product: ProductIn):
        query = products.insert().values(**product.model_dump())
        last_record_id = await database.execute(query)
        return {**product.model_dump(), "id": last_record_id}

@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, new_product: ProductIn):
        query = products.update().where(products.c.id == product_id).values(**new_product.model_dump())
        await database.execute(query)
        return {**new_product.model_dump(), "id": product_id}

@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
        query = products.delete().where(products.c.id == product_id)
        await database.execute(query)
        return {'message': 'Product deleted'}

@app.get("/orders/", response_model=List[Order])
async def get_orders():
    query = orders.select()
    return await database.fetch_all(query)

@app.get("/orders/{order_id}", response_model=Order)
async def get_orders(order_id: int):
    query = orders.select().where(orders.c.id == order_id)
    return await database.fetch_one(query)

@app.post("/orders/", response_model=Order)
async def create_order(order: OrderIn):
        query = orders.insert().values(**order.model_dump())
        last_record_id = await database.execute(query)
        return {**order.model_dump(), "id": last_record_id}

@app.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: int, new_order: OrderIn):
        query = orders.update().where(orders.c.id == order_id).values(**new_order.model_dump())
        await database.execute(query)
        return {**new_order.model_dump(), "id": order_id}

@app.delete("/orders/{order_id}")
async def delete_order(order_id: int):
        query = orders.delete().where(orders.c.id == order_id)
        await database.execute(query)
        return {'message': 'order deleted'}