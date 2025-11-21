import threading
from calendar import calendar

class Results:
    def __init__(self):
        self.lock = threading.Lock()
        self.accepted = 0
        self.rejected = 0
        self.completed = 0
        self.total_wait_time = 0.0
        self.total_process_time = 0.0
        self.completed_ids = []

    def record_accepted(self, order):
        with self.lock:
            self.accepted += 1
            print(f"[Results] Заказ {order.id} зарегистрирован как принят.")

    def record_rejected(self, order):
        with self.lock:
            self.rejected += 1
            print(f"[Results] Заказ {order.id} зарегистрирован как отклонённый.")

    def record_completed(self, order, wait_time, process_time):
        with self.lock:
            self.completed += 1
            self.total_wait_time += wait_time
            self.total_process_time += process_time
            self.completed_ids.append(order.id)
            print(f"[Results] Заказ {order.id} завершён. Время ожидания {wait_time:.2f}s, время обработки {process_time:.2f}s")

    def print_summary(self, buffer_snapshot):
        with self.lock:
            print("\n===== ОТЧЁТ ПО ИТОГАМ СИМУЛЯЦИИ =====")
            print(f"Принято: {self.accepted}")
            print(f"Отклонено: {self.rejected}")
            print(f"Завершено: {self.completed}")
            avg_wait = self.total_wait_time / self.completed if self.completed else 0
            avg_proc = self.total_process_time / self.completed if self.completed else 0
            print(f"Среднее время ожидания: {avg_wait:.2f}s")
            print(f"Среднее время обработки: {avg_proc:.2f}s")
            print(f"Остаток в буфере ({len(buffer_snapshot)}): {[ (o.id, o.user_id) for o in buffer_snapshot ]}")
            print("======================================\n")
