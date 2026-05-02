import math
import matplotlib.pyplot as plt


class Params:
    def __init__(self):
        self.m = 0.1      # масса, кг
        self.S = 0.01     # площадь, м^2
        self.Cd = 0.47    # коэффициент сопротивления
        self.rho = 1.225  # плотность воздуха, кг/м^3
        self.g = 9.81     # ускорение свободного падения, м/с^2
        self.v0 = 50.0    # начальная скорость, м/с
        self.alpha = math.radians(45.0)  # угол в радианах


def simulate(dt, p: Params):
    x = 0.0
    y = 0.0

    vx = p.v0 * math.cos(p.alpha)
    vy = p.v0 * math.sin(p.alpha)

    xs = [x]
    ys = [y]
    max_y = y

    while y >= 0.0:
        v = math.sqrt(vx * vx + vy * vy)

        Fdx = -0.5 * p.rho * p.Cd * p.S * v * vx
        Fdy = -0.5 * p.rho * p.Cd * p.S * v * vy

        ax = Fdx / p.m
        ay = -p.g + Fdy / p.m

        vx += ax * dt
        vy += ay * dt

        x += vx * dt
        y += vy * dt

        xs.append(x)
        ys.append(y)

        if y > max_y:
            max_y = y

        if y < 0.0:
            break

    final_speed = math.sqrt(vx * vx + vy * vy)

    return {
        "dt": dt,
        "range": x,
        "max_height": max_y,
        "final_speed": final_speed,
        "xs": xs,
        "ys": ys
    }


def main():
    p = Params()

    dts = [1.0, 0.1, 0.01, 0.001, 0.0001]

    results = []

    for dt in dts:
        res = simulate(dt, p)
        results.append(res)

    print("\nТаблица результатов:\n")
    print("Шаг dt, с:           ", end="")
    for r in results:
        print(f"{r['dt']:12.6f}", end="")
    print()

    print("Дальность полёта, м: ", end="")
    for r in results:
        print(f"{r['range']:12.6f}", end="")
    print()

    print("Макс. высота, м:     ", end="")
    for r in results:
        print(f"{r['max_height']:12.6f}", end="")
    print()

    print("Скорость в конце, м/с:", end="")
    for r in results:
        print(f"{r['final_speed']:12.6f}", end="")
    print("\n")

    plt.figure()
    for r in results:
        xs = r["xs"]
        ys = r["ys"]
        plt.plot(xs, ys, label=f"dt = {r['dt']}")

    plt.xlabel("x (м)")
    plt.ylabel("y (м)")
    plt.title("Траектории для разных шагов dt")
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
