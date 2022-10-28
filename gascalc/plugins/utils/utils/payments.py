import uuid

import requests

from yandex_checkout import Payment

def create_payment():

    payment = Payment.create({
                            "amount":
                                {"value": "500.00",
                                "currency": "RUB"},               
                            "confirmation":
                                {"type": "redirect",
                                "return_url": "http://127.0.0.1:5000"},
                            "capture": True,
                            "description": "Заказ №1"
                            }, uuid.uuid4())

    return payment.id

def find_payment(payment_id):

    payment = Payment.find_one(payment.id)

    status = payment.json()

    return status