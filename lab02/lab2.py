import numpy as np

def simulate_heat(dx, dt, a=1e-4, L=1.0, T_total=2.0):
    # проверка устойчивости
    if dt > dx*dx/(2*a):
        raise ValueError(f"Неустойчивая схема: dt={dt} слишком велико для dx={dx}")

    N = int(L / dx) + 1  # количество узлов

    T = np.zeros(N)
    T_new = np.zeros(N)

    center = N // 2
    T[center] = 100.0

    steps = int(T_total / dt)

    for _ in range(steps):
        for i in range(1, N - 1):
            T_new[i] = T[i] + a * dt / dx**2 * (T[i+1] - 2*T[i] + T[i-1])

        T_new[0] = 0
        T_new[-1] = 0

        T, T_new = T_new, T

    return T[center]  # температура в центре через 2 секунды


def main():
    dx_values = [0.1, 0.01, 0.001, 0.0001]
    dt_values = [0.1, 0.01, 0.001, 0.0001]

    print("Шаг по времени \\ шаг по пространству")
    print("        ", end="")
    for dx in dx_values:
        print(f"{dx:>12}", end="")
    print()

    for dt in dt_values:
        print(f"{dt:<8}", end="")
        for dx in dx_values:
            try:
                T_center = simulate_heat(dx, dt)
                print(f"{T_center:12.4f}", end="")
            except ValueError:
                print(f"{'unstable':>12}", end="")
        print()

main()