import random
import matplotlib.pyplot as plt


def simulate_mm1_visualized(
    lambda_rate: float, mu_rate: float, num_customers: int = 50000):
    current_time = 0.0
    server_free_time = 0.0

    wait_times = []  # Wq
    system_times = []  # W

    history_times = []  # прибытие
    history_queue = []
    running_avg_wait = []

    current_queue = []

    running_sum_wait = 0.0

    for i in range(1, num_customers + 1):
        interarrival = random.expovariate(lambda_rate)
        current_time += interarrival

        service_time = random.expovariate(mu_rate)
        current_queue = [
            leave_t for leave_t in current_queue if leave_t > current_time
        ]

        # Время ожидания в очереди
        wait = max(0.0, server_free_time - current_time)
        wait_times.append(wait)

        # Время в системе
        system_time = wait + service_time
        system_times.append(system_time)

        # Время освобождения
        server_free_time = max(current_time, server_free_time) + service_time

        if wait > 0:
            current_queue.append(server_free_time)

        running_sum_wait += wait
        running_avg_wait.append(running_sum_wait / i)

        if len(history_times) < 2000:
            history_times.append(current_time)
            history_queue.append(len(current_queue))

    avg_wait = sum(wait_times) / num_customers
    avg_system = sum(system_times) / num_customers
    rho = lambda_rate / mu_rate

    print(f"=== Результаты моделирования ({num_customers} клиентов) ===")
    print(f"Коэффициент загрузки системы (ρ): {rho:.4f}")
    print(f"Среднее время ожидания в очереди (Wq): {avg_wait:.4f}")
    print(f"Среднее время пребывания в системе (W):  {avg_system:.4f}")

    theory_wq = None
    theory_w = None

    if rho < 1:
        theory_wq = lambda_rate / (mu_rate * (mu_rate - lambda_rate))
        theory_w = 1 / (mu_rate - lambda_rate)
        print("\n=== Теоретические расчёты ===")
        print(f"Теоретическое Wq: {theory_wq:.4f}")
        print(f"Теоретическое W:  {theory_w:.4f}")
    else:
        print("\nСистема нестабильна (ρ >= 1): длина очереди растёт бесконечно!")

    plot_results(
        history_times,
        history_queue,
        wait_times,
        running_avg_wait,
        avg_wait,
        theory_wq)


def plot_results(
    times,
    queue_lengths,
    wait_times,
    running_avg_wait,
    avg_wait,
    theory_wq=None):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10))

    ax1.step(
        times,
        queue_lengths,
        where="post",
        color="#1f77b4",
        alpha=0.8,
        label="Длина очереди"
    )
    ax1.set_title("Динамика изменения длины очереди во времени (фрагмент)")
    ax1.set_xlabel("Время")
    ax1.set_ylabel("Заявок в очереди")
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend()

    ax2.hist(
        wait_times,
        bins=50,
        density=True,
        color="#2ca02c",
        edgecolor="black",
        alpha=0.6,
        label="Эмпирическая плотность"
    )
    ax2.axvline(
        avg_wait,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Модель Wq = {avg_wait:.4f}"
    )
    if theory_wq is not None:
        ax2.axvline(
            theory_wq,
            color="black",
            linestyle=":",
            linewidth=2,
            label=f"Теория Wq = {theory_wq:.4f}"
        )
    ax2.set_title("Распределение времени ожидания в очереди (Wq)")
    ax2.set_xlabel("Время ожидания")
    ax2.set_ylabel("Плотность вероятности")
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend()

    ax3.plot(
        running_avg_wait,
        color="#ff7f0e",
        linewidth=1.5,
        label="Накопительное среднее Wq"
    )
    if theory_wq is not None:
        ax3.axhline(
            theory_wq,
            color="black",
            linestyle="--",
            linewidth=2,
            label=f"Теория Wq ({theory_wq:.4f})"
        )
    ax3.set_title("Сходимость среднего времени ожидания с увеличением числа клиентов")
    ax3.set_xlabel("Обслужено клиентов")
    ax3.set_ylabel("Среднее Wq")
    ax3.grid(True, linestyle="--", alpha=0.6)
    ax3.legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    LAMBDA = 2.0  # Интенсивность входящего потока
    MU = 3.0  # Интенсивность обслуживания

    simulate_mm1_visualized(lambda_rate=LAMBDA, mu_rate=MU, num_customers=50000)