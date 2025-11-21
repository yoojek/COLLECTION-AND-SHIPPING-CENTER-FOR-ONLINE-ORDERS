import threading

class Calendar:
    def __init__(self):
        self.lock = threading.Lock()
        self.log = []
        self.counter = 0

    def record(self, event, order=None, buf_before=None, buf_after=None, asm_before=None, asm_after=None, note=""):
        with self.lock:
            self.counter += 1
            self.log.append({
                "id": self.counter,
                "event": event,
                "order": order.id if order else None,
                "user": order.user_id if order else None,
                "buf_before": buf_before,
                "buf_after": buf_after,
                "asm_before": asm_before,
                "asm_after": asm_after,
                "note": note,
            })

    def dump(self):
        print("\n===== КАЛЕНДАРЬ СОБЫТИЙ =====")
        for e in self.log:
            print(f"{e['id']:04d} | {e['event']:<20} | order={e['order']} user={e['user']} "
                  f"| buf_before={e['buf_before']} | buf_after={e['buf_after']} "
                  f"| asm_before={e['asm_before']} | asm_after={e['asm_after']} | {e['note']}")
        print("================================\n")


calendar = Calendar()
