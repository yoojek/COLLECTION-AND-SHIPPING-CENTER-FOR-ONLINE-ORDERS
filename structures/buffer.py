import threading
from collections import deque
from calendar import calendar

""" 
Буфер с capacity мест. Сохраняет объекты Order. 
Политика: при переполнении удаляется самый старый заказ, новый добавляется в конец (последняя позиция == самое новое). 
Извлечение выполняется LIFO: сборщик берет самый новый заказ. 
Также можно извлечь самый новый заказ конкретного пользователя. 
"""

class Buffer:
    def __init__(self, capacity=5):
        self.capacity = capacity
        self.deque = deque()
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)

    def _state(self):
        return [o.id for o in self.deque]

    def add_order(self, order):
        with self.lock:
            before = self._state().copy()

            removed = None
            if len(self.deque) >= self.capacity:
                removed = self.deque.popleft()
                print(f"[Buffer] Переполнение: удалён старейший заказ {removed.id} (user_{removed.user_id})")

            self.deque.append(order)
            print(f"[Buffer] Добавлен заказ {order.id} (user_{order.user_id}). Заполнение: {len(self.deque)}/{self.capacity}")
            print(f"[Buffer] Текущее состояние: {self._state()}")

            calendar.record(
                "buffer_push",
                order=order,
                buf_before=before,
                buf_after=self._state()
            )

            self.not_empty.notify_all()

    def pop_newest(self):
        with self.lock:
            if not self.deque:
                return None

            before = self._state().copy()
            order = self.deque.pop()

            print(f"[Buffer] Извлечён самый новый заказ {order.id} (user_{order.user_id})")
            print(f"[Buffer] Текущее состояние: {self._state()}")

            calendar.record(
                "buffer_pop_newest",
                order=order,
                buf_before=before,
                buf_after=self._state()
            )

            return order

    def pop_newest_by_user(self, user_id):
        with self.lock:
            before = self._state().copy()

            for i in range(len(self.deque)-1, -1, -1):
                if self.deque[i].user_id == user_id:
                    order = self.deque[i]
                    del self.deque[i]

                    print(f"[Buffer] Извлечён заказ {order.id} пользователя user_{order.user_id} (sticky-user)")
                    print(f"[Buffer] Текущее состояние: {self._state()}")

                    calendar.record(
                        "buffer_pop_by_user",
                        order=order,
                        buf_before=before,
                        buf_after=self._state()
                    )

                    return order
            return None

    def has_orders(self):
        with self.lock:
            return len(self.deque) > 0

    def snapshot(self):
        with self.lock:
            return list(self.deque)

    def is_empty(self):
        with self.lock:
            return len(self.deque) == 0
