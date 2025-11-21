import threading
import random
import time
from dataclasses import dataclass
from calendar import calendar

""" 
Генерирует поток заказов по Пуассону. 
Каждый заказ получает user_id в диапазоне 1..num_users (возможны множественные заказы от одного пользователя). 
После генерации вызывает callback(order). 
"""

@dataclass
class Order:
    id: int
    user_id: int
    created_time: float

class OrderGenerator(threading.Thread):
    def __init__(self, callback, lambda_rate=0.5, num_users=10, max_orders=None):
        super().__init__(daemon=True)
        self.callback = callback
        self.lambda_rate = lambda_rate
        self.num_users = num_users
        self.stop_flag = threading.Event()
        self.order_id = 0
        self.max_orders = max_orders

    def stop(self):
        self.stop_flag.set()

    def run(self):
        while not self.stop_flag.is_set():
            inter = random.expovariate(self.lambda_rate)
            time.sleep(inter)

            if self.stop_flag.is_set():
                break

            self.order_id += 1
            user = random.randint(1, self.num_users)

            order = Order(self.order_id, user, time.time())
            print(f"[OrderGenerator] Сгенерирован заказ {order.id} от user_{order.user_id}")

            calendar.record("order_generated", order)

            self.callback(order)
            # Всплески заказов (акции\скидки\что угодно, но люди делают много заказов)
            if random.random() < 0.15:
                burst_count = random.randint(2, 6)
                print(f"[OrderGenerator] ВСПЛЕСК заказов: {burst_count}")

                for _ in range(burst_count):
                    if self.stop_flag.is_set():
                        break

                    self.order_id += 1
                    user = random.randint(1, self.num_users)

                    burst_order = Order(self.order_id, user, time.time())
                    print(f"[OrderGenerator] (всплеск) заказ {burst_order.id} от user_{burst_order.user_id}")

                    calendar.record("order_generated", burst_order)

                    self.callback(burst_order)

            if self.max_orders and self.order_id >= self.max_orders:
                break
