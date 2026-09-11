import heapq
import logging
import random
from dataclasses import dataclass, field
from typing import List, Optional

LOG_FILENAME = "simulation_log.txt"

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    filename=LOG_FILENAME,
    filemode="w",
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
    encoding="utf-8",
)

logger = logging.getLogger(__name__)

@dataclass
class Request:
    req_id: int
    arrival_time: float
    service_time: float
    start_service_time: Optional[float] = None
    finish_service_time: Optional[float] = None

    @property
    def total_time(self) -> float:
        if self.finish_service_time is not None:
            return self.finish_service_time - self.arrival_time
        return 0.0


@dataclass
class Server:
    server_id: int
    is_busy: bool = False
    current_request: Optional[Request] = None
    total_busy_time: float = 0.0
    processed_count: int = 0

@dataclass(order=True)
class Event:
    time: float
    event_type: str = field(compare=False)
    request: Request = field(compare=False)
    server: Optional[Server] = field(default=None, compare=False)


class QueueingSystem:

    def __init__(
        self,
        num_servers: int,
        arrival_rate: float,
        service_rate: float,
    ):
        self.num_servers = num_servers
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate

        self.servers: List[Server] = [
            Server(server_id=i + 1) for i in range(num_servers)
        ]

        self.event_calendar: List[Event] = []

        self.generated_requests_count = 0
        self.processed_requests: List[Request] = []
        self.rejected_requests_count = 0

    def get_free_server(self) -> Optional[Server]:
        for server in self.servers:
            if not server.is_busy:
                return server
        return None

    def schedule_event(self, event: Event):
        heapq.heappush(self.event_calendar, event)

    def run_simulation(self, max_simulation_time: float):
        current_time = 0.0

        logger.info(
            f"=== ЗАПУСК МОДЕЛИРОВАНИЯ СМО M/M/{self.num_servers} ==="
        )
        logger.info(
            f"Параметры: Lambda={self.arrival_rate}, Mu={self.service_rate}, "
            f"Число приборов={self.num_servers}"
        )

        #первый приход
        first_arrival_interval = random.expovariate(self.arrival_rate)
        self.generated_requests_count += 1
        first_req = Request(
            req_id=self.generated_requests_count,
            arrival_time=first_arrival_interval,
            service_time=random.expovariate(self.service_rate),
        )
        self.schedule_event(
            Event(
                time=first_arrival_interval,
                event_type="ARRIVAL",
                request=first_req,
            )
        )

        while self.event_calendar:
            event = heapq.heappop(self.event_calendar)
            current_time = event.time

            if current_time > max_simulation_time:
                break

            if event.event_type == "ARRIVAL":
                self.handle_arrival(event.request, current_time)
            elif event.event_type == "DEPARTURE":
                self.handle_departure(event.request, event.server, current_time)

        logger.info("== МОДЕЛИРОВАНИЕ ЗАВЕРШЕНО ==")
        self.generate_report(current_time)

    def handle_arrival(self, request: Request, current_time: float):
        logger.info(f"t={current_time:.2f} | Заявка #{request.req_id} поступила.")

        next_interval = random.expovariate(self.arrival_rate)
        self.generated_requests_count += 1
        next_req = Request(
            req_id=self.generated_requests_count,
            arrival_time=current_time + next_interval,
            service_time=random.expovariate(self.service_rate),
        )
        self.schedule_event(
            Event(
                time=next_req.arrival_time,
                event_type="ARRIVAL",
                request=next_req,
            )
        )

        free_server = self.get_free_server()
        if free_server is not None:
            free_server.is_busy = True
            free_server.current_request = request
            request.start_service_time = current_time

            logger.info(
                f"t={current_time:.2f} | Заявка #{request.req_id} "
                f"направлена на Прибор #{free_server.server_id}."
            )

            departure_time = current_time + request.service_time
            self.schedule_event(
                Event(
                    time=departure_time,
                    event_type="DEPARTURE",
                    request=request,
                    server=free_server,
                )
            )
        else:
            self.rejected_requests_count += 1
            logger.warning(
                f"t={current_time:.2f} | ОТКАЗ! Все приборы ({self.num_servers}) заняты. "
                f"Заявка #{request.req_id} потеряна."
            )

    def handle_departure(
        self, request: Request, server: Server, current_time: float
    ):
        request.finish_service_time = current_time
        server.processed_count += 1
        server.total_busy_time += request.service_time
        self.processed_requests.append(request)

        server.is_busy = False
        server.current_request = None

        logger.info(
            f"t={current_time:.2f} | Заявка #{request.req_id} завершила обслуживание "
            f"на Приборе #{server.server_id}. Прибор свободен."
        )

    def generate_report(self, total_sim_time: float):
        total_gen = self.generated_requests_count - 1
        processed_len = len(self.processed_requests)
        rejected_cnt = self.rejected_requests_count

        prob_rejection = (rejected_cnt / total_gen) if total_gen > 0 else 0.0

        avg_service_time = (
            sum(r.service_time for r in self.processed_requests) / processed_len
            if processed_len > 0
            else 0.0
        )

        report_lines = [
            "          ИТОГОВЫЙ ОТЧЕТ РАБОТЫ СМО          ",
            "-" * 50,
            f"Время моделирования:           {total_sim_time:.2f} ед. времени",
            f"Всего поступило заявок:        {total_gen}",
            f"Успешно обслужено:            {processed_len}",
            f"Отклонено (отказов):            {rejected_cnt}",
            f"Вероятность отказа (Pотк):     {prob_rejection:.4f} ({prob_rejection * 100:.2f}%)",
            f"Среднее время обслуживания:    {avg_service_time:.4f}",
            "-" * 50,
            "Загрузка приборов:",
        ]

        for s in self.servers:
            util = (
                (s.total_busy_time / total_sim_time) if total_sim_time > 0 else 0.0
            )
            report_lines.append(
                f"  • Прибор #{s.server_id}: Обслужено={s.processed_count}, "
                f"Коэф. загрузки={util:.2f} ({util * 100:.1f}%)"
            )

        report_lines.append("-" * 50)
        report_text = "\n".join(report_lines)
        print(report_text)
        logger.info(report_text)

if __name__ == "__main__":
    random.seed(42)
    smo = QueueingSystem(
        num_servers=3, arrival_rate=5.0, service_rate=1.5
    )
    smo.run_simulation(max_simulation_time=100.0)

    print(f"\n[Успешно] Подробный лог работы сохранен в файл: {LOG_FILENAME}")