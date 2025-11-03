import requests
from api import Books

#Добавить книгу
def add_jsobin(data):
    url = f'https://api.jsonbin.io/v3/b'
    headers = {
      'Content-Type': 'application/json',
      'X-Master-Key': '$2a$10$Jnw1/tH1QXgtCxLp3fQfiO9h5.gQ34dILvwn9Yk96eiDZOcttQI4y'
    }
    requests.post(url, json=data, headers=headers)


#Обновить книгу
def update_book(data, bake_id):
    url = f'https://api.jsonbin.io/v3/b/{bake_id}'
    headers = {
      'Content-Type': 'application/json',
      'X-Master-Key': '$2a$10$Jnw1/tH1QXgtCxLp3fQfiO9h5.gQ34dILvwn9Yk96eiDZOcttQI4y'
    }
    requests.put(url, json=data, headers=headers)

#Удалить бакет
def delete_backet(bake_id):
    url = f'https://api.jsonbin.io/v3/b/{bake_id}'
    headers = {
        'Content-Type': 'application/json',
        'X-Master-Key': '$2a$10$Jnw1/tH1QXgtCxLp3fQfiO9h5.gQ34dILvwn9Yk96eiDZOcttQI4y'
    }
    requests.delete(url, json=None, headers=headers)