### Моделирование полёта тела в атмосфере

**Задание:**  
Реализовать приложение для моделирования полёта тела в атмосфере.  
Предусмотреть возможность ввода шага моделирования и вывода результатов.

Выполнить моделирование **без очистки предыдущих результатов** для различных шагов моделирования, сравнить траектории и заполнить таблицу:

| Шаг моделирования, с | 1 | 0.1 | 0.01 | 0.001 | 0.0001 |
|----------------------|---|-----|------|-------|--------|
| Дальность полёта, м |   |     |      |       |        |
| Максимальная высота, м | | | | | |
| Скорость в конечной точке, м/с | | | | | |

**Сделать выводы.**

**В отчёт включить:**
- код программы;
- скриншот с несколькими траекториями;
- заполненную таблицу;
- выводы.

LAB 1
import math
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt


class Params:
    def __init__(self, m, S, v0, alpha_deg):
        self.m = m
        self.S = S
        self.v0 = v0
        self.alpha = math.radians(alpha_deg)

        self.rho = 1.225
        self.g = 9.81
        self.Cd = 0.47

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

        if y < 0:
            break

    final_speed = math.sqrt(vx * vx + vy * vy)

    return x, max_y, final_speed, xs, ys


def run_simulation():
    try:
        dt_values = list(map(float, entry_dt.get().split()))

        m = float(entry_m.get())
        S = float(entry_S.get())
        v0 = float(entry_v0.get())
        alpha = float(entry_alpha.get())

        if any(dt <= 0 for dt in dt_values):
            raise ValueError

    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректные числовые значения параметров")
        return

    p = Params(m, S, v0, alpha)

    results_str = "Результаты моделирования:\n"

    plt.figure()
    plt.xlabel("x (м)")
    plt.ylabel("y (м)")
    plt.title("Траектории полёта")
    plt.grid(True)


    for dt in dt_values:
        distance, max_height, final_speed, xs, ys = simulate(dt, p)

        results_str += (
            f"\n--- dt = {dt} ---\n"
            f"Дальность: {distance:.3f} м\n"
            f"Макс. высота: {max_height:.3f} м\n"
            f"Скорость в конце: {final_speed:.3f} м/с\n"
        )

        plt.plot(xs, ys, label=f"dt = {dt}")

    old = result_text.get()
    if old.strip():
        result_text.set(old + "\n" + results_str)
    else:
        result_text.set(results_str)

    plt.legend()
    plt.show()


root = tk.Tk()
root.title("Моделирование полёта камня")

def add_field(label_text, default):
    tk.Label(root, text=label_text).pack()
    entry = tk.Entry(root)
    entry.pack()
    entry.insert(0, default)
    return entry

entry_dt = add_field("Введите dt (можно несколько через пробел):", "0.1 0.01 0.001")
entry_alpha = add_field("Угол броска (градусы):", "60")
entry_v0 = add_field("Начальная скорость v0 (м/с):", "20")
entry_m = add_field("Масса m (кг):", "0.1")
entry_S = add_field("Площадь S (м²):", "0.01")

tk.Button(root, text="Запустить моделирование", command=run_simulation).pack(pady=10)

result_text = tk.StringVar()
tk.Label(root, textvariable=result_text, justify="left").pack()

root.mainloop()



(60*)   <img width="751" height="635" alt="image" src="https://github.com/user-attachments/assets/59b04a40-652a-4e20-a51f-ede9df7adb82" />
   
(45*)     <img width="751" height="775" alt="image" src="https://github.com/user-attachments/assets/e2f230f2-61b3-4d7c-8f1c-a6b3a196961e" />
 

(30*)    <img width="735" height="722" alt="image" src="https://github.com/user-attachments/assets/abf8b842-d1a0-4250-a93c-29e1e9e4e75b" />
        
60*
Шаг моделирования, с	1	0.1	0.01	0.001	0.0001
Дальность полета, м	4.243	17.437	18.751	18.86	18.867
Макс.высота, м	0	9.102	10.195	10.304	10.315
Скорость в конце, м/с	4.905	12.276	12.852	12.884	12.887
| Шаг моделирования, с | 1 | 0.1 | 0.01 | 0.001 | 0.0001 |
|----------------------|---|-----|------|-------|--------|
| Дальность полёта, м | 4.243  |  17.437   |  18.751    |  18.86     |   18.867     |
| Максимальная высота, м |0| 9.102 |10.195 | 10.304| 10.315 |
| Скорость в конечной точке, м/с |4.905 | 12.276| 12.852| 12.884| 12.887|






Выводы: 
•	Дальность увеличивается до определенного градуса: +- 40*, затем из-за сопротивления воздуха идет на убыль
•	Скорость увеличивается с уменьшением градуса броска
•	Чем меньше dt — тем точнее траектория

