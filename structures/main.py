import time
from order_generator import OrderGenerator
from order_receiver import OrderReceiver
from buffer import Buffer
from assembler import Assembler
from manager import Manager
from results import Results
from calendar import calendar

def main(simulation_time=60):
    print("Запуск симуляции центра сборки и отправки интернет-заказов")

    results = Results()
    buf = Buffer(capacity=5)
    receiver = OrderReceiver(buffer=buf, results=results, invalid_prob=0.07)

    assemblers = [Assembler(i, results) for i in (1,2,3)]
    for a in assemblers:
        a.start()

    manager = Manager(buffer=buf, assemblers=assemblers)
    manager.start()

    generator = OrderGenerator(callback=receiver.receive, lambda_rate=0.35, num_users=12)
    generator.start()

    try:
        time.sleep(simulation_time)
    except KeyboardInterrupt:
        print("Прервано пользователем.")

    print("Приём новых заказов остановлен.")
    generator.stop()
    generator.join(timeout=1)

    print("Ожидание завершения обработки всех заказов...")

    while True:
        buffer_empty = buf.is_empty()
        assemblers_idle = all(not a.is_busy() for a in assemblers)

        if buffer_empty and assemblers_idle:
            break

        time.sleep(0.2)

    manager.stop()
    manager.join(timeout=1)

    for a in assemblers:
        a.stop()
        a.join(timeout=1)

    buffer_snapshot = buf.snapshot()
    results.print_summary(buffer_snapshot)

    calendar.dump()

    print("Симуляция завершена.")

if __name__ == "__main__":
    main(simulation_time=60) # Для теста оставил 1мин
