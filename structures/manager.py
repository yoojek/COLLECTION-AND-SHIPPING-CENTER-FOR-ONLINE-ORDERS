import threading
import time
from calendar import calendar

""" 
Менеджер: - наблюдает за буфером и за свободными сборщиками - 
назначает самый новый заказ свободному сборщику с минимальным номером - если сборщик имеет sticky_user, 
сначала пытается найти самый новый заказ этого user 
"""

class Manager(threading.Thread):
    def __init__(self, buffer, assemblers, poll_interval=0.1):
        super().__init__(daemon=True)
        self.buffer = buffer
        self.assemblers = assemblers
        self.poll_interval = poll_interval
        self.stop_flag = threading.Event()

    def run(self):
        while not self.stop_flag.is_set():

            if not self.buffer.has_orders():
                time.sleep(self.poll_interval)
                continue

            free = [a for a in sorted(self.assemblers, key=lambda x: x.id)
                    if not a.busy and not a._assigned_event.is_set()]

            if not free:
                time.sleep(self.poll_interval)
                continue

            for assembler in free:
                if not self.buffer.has_orders():
                    break

                asm_before = {a.id: a.busy for a in self.assemblers}

                assigned = None

                if assembler.sticky_user is not None:
                    assigned = self.buffer.pop_newest_by_user(assembler.sticky_user)
                    if assigned:
                        print(f"[Manager] Назначил assembler {assembler.id} заказ {assigned.id} (sticky user_{assembler.sticky_user})")

                        calendar.record(
                            "order_assigned",
                            order=assigned,
                            asm_before=asm_before,
                            asm_after=asm_before,
                            note=f"Назначен assembler {assembler.id} (sticky)"
                        )

                        assembler.assign_order(assigned)
                        continue
                    else:
                        assembler.sticky_user = None

                assigned = self.buffer.pop_newest()
                if assigned:
                    print(f"[Manager] Назначил assembler {assembler.id} заказ {assigned.id} (user_{assigned.user_id})")

                    calendar.record(
                        "order_assigned",
                        order=assigned,
                        asm_before=asm_before,
                        asm_after=asm_before,
                        note=f"Назначен assembler {assembler.id}"
                    )

                    assembler.assign_order(assigned)

            time.sleep(self.poll_interval)

    def stop(self):
        self.stop_flag.set()
