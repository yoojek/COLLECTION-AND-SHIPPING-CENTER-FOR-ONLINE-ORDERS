import threading
import time
import random
from calendar import calendar

""" 
Сборщик (прибор). Получает задания от manager через assign_order(). 
После получения order, обрабатывает его случайное равномерное время. 
Поддерживает 'sticky_user' - если начал с user_X, будет стараться продолжить с ним. 
"""

class Assembler(threading.Thread):
    def __init__(self, assembler_id, results):
        super().__init__(daemon=True)
        self.id = assembler_id
        self.results = results
        self._lock = threading.Lock()
        self._assigned_order = None
        self._assigned_event = threading.Event()
        self.stop_flag = threading.Event()
        self.busy = False
        self.sticky_user = None

    def assign_order(self, order):
        with self._lock:
            self._assigned_order = order
            self._assigned_event.set()

    def run(self):
        while not self.stop_flag.is_set():
            self._assigned_event.wait(timeout=0.5)

            if self.stop_flag.is_set():
                break

            with self._lock:
                if self._assigned_order is None:
                    self._assigned_event.clear()
                    continue

                order = self._assigned_order
                self._assigned_order = None
                self._assigned_event.clear()

            calendar.record(
                "assembly_start",
                order=order,
                asm_before={self.id: "idle"},
                asm_after={self.id: "busy"}
            )

            self.busy = True
            self.sticky_user = order.user_id

            start = time.time()
            print(f"[Assembler {self.id}] Начинаю сборку заказа {order.id} (user_{order.user_id})")

            process_time = random.uniform(6.0, 12.0)
            time.sleep(process_time)
            end = time.time()

            self.results.record_completed(order, wait_time=(start - order.created_time), process_time=process_time)

            print(f"[Assembler {self.id}] Завершил сборку заказа {order.id} (user_{order.user_id}) за {process_time:.2f}s")

            calendar.record(
                "assembly_end",
                order=order,
                asm_before={self.id: "busy"},
                asm_after={self.id: "idle"}
            )

            self.busy = False

    def stop(self):
        self.stop_flag.set()
        self._assigned_event.set()

    def is_busy(self):
        return self.busy
