import numpy as np

def simulate_heat(dx, dt, a=1.1e-4, L=0.1, T_total=2.0):

    N = int(L / dx) + 1
    T = np.zeros(N)
    T[0] = 100.0
    T[-1] = 100.0
    center = N // 2
    steps = int(T_total / dt)
    A = a / dx ** 2
    C = a / dx ** 2
    B = (2 * a / dx ** 2) + (1 / dt)

    alpha = np.zeros(N)
    beta = np.zeros(N)

    for _ in range(steps):
        alpha[1] = 0.0
        beta[1] = 100.0
        for i in range(1, N - 1):
            F = -T[i] / dt
            denominator = B - C * alpha[i]
            alpha[i + 1] = A / denominator
            beta[i + 1] = (C * beta[i] - F) / denominator
        T_new = np.zeros(N)
        T_new[-1] = 100.0
        for i in range(N - 2, -1, -1):
            T_new[i] = alpha[i + 1] * T_new[i + 1] + beta[i + 1]
        T = T_new

    return T[center]


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
            T_center = simulate_heat(dx, dt)
            print(f"{T_center:12.4f}", end="")
        print()


if __name__ == "__main__":
    main()