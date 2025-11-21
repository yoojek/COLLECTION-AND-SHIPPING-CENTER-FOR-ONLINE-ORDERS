import random
from calendar import calendar

""" 
Принимает заказ от генератора, проверяет корректность (рандомные ошибки), 
и если корректен -- помещает в буфер (через метод buffer.add_order). 
В случае ошибки -- отклоняет и сообщет в results.
"""

class OrderReceiver:
    def __init__(self, buffer, results, invalid_prob=0.1):
        self.buffer = buffer
        self.results = results
        self.invalid_prob = invalid_prob

    def receive(self, order):
        if random.random() < self.invalid_prob:
            print(f"[OrderReceiver] Заказ {order.id} от user_{order.user_id} отклонён (ошибка оформления)")
            self.results.record_rejected(order)

            calendar.record("order_rejected", order)
            return

        print(f"[OrderReceiver] Заказ {order.id} от user_{order.user_id} принят системой")
        self.results.record_accepted(order)

        calendar.record("order_accepted", order, buf_before=self.buffer._state().copy())

        self.buffer.add_order(order)
