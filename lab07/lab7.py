import csv
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


#Вычисление матричной экспоненты
def matrix_expm(A, terms=20):
    res = np.eye(A.shape[0])
    term = np.eye(A.shape[0])
    for k in range(1, terms):
        term = term @ A / k
        res += term
    return res

class WeatherMarkovApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Марковская модель погоды")
        self.root.geometry("1100x950")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.STATES = {0: "1 — Ясно", 1: "2 — Облачно", 2: "3 — Пасмурно"}
        self.STATE_NAMES = ["Ясно", "Облачно", "Пасмурно"]
        self.NUM_STATES = len(self.STATES)
        self.TOTAL_DAYS = 360
        self.ANIMATION_INTERVAL_MS = 80

        # Исходная матрица интенсивностей Q и расчёт P
        self.Q = np.array(
            [
                [-0.5, 0.3, 0.2],
                [0.4, -0.7, 0.3],
                [0.2, 0.5, -0.7],
            ]
        )
        self.P = matrix_expm(self.Q * 1.0)
        self.P = self.P / self.P.sum(axis=1, keepdims=True)

        self.recalculate_theoretical_pi()
        self.reset_data()

        self._create_widgets()
        self._setup_plots()

        self.is_running = False
        self.anim = FuncAnimation(
            self.fig,
            self.update_plot,
            interval=self.ANIMATION_INTERVAL_MS,
            blit=False,
            cache_frame_data=False,
        )
        self.anim.event_source.stop()

    def on_closing(self):
        self.pause_sim()
        self.root.destroy()

    def recalculate_theoretical_pi(self):
        #Расчёт теоретического стационарного распределения
        A_mat = (self.P.T - np.eye(self.NUM_STATES)).copy()
        A_mat[-1, :] = 1.0
        b_vec = np.array([0.0, 0.0, 1.0])
        try:
            self.pi_theoretical = np.linalg.solve(A_mat, b_vec)
        except np.linalg.LinAlgError:
            self.pi_theoretical = np.ones(self.NUM_STATES) / self.NUM_STATES

    def reset_data(self):
        initial_state = np.random.choice(self.NUM_STATES)
        self.history_days = [0]
        self.history_states = [initial_state]
        self.state_counts = np.zeros(self.NUM_STATES, dtype=int)
        self.state_counts[initial_state] = 1

    def _create_widgets(self):
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        self.btn_start = ttk.Button(
            control_frame, text="Запустить / Продолжить", command=self.start_sim
        )
        self.btn_start.pack(side=tk.LEFT, padx=5)

        self.btn_pause = ttk.Button(
            control_frame, text="Пауза", command=self.pause_sim, state=tk.DISABLED
        )
        self.btn_pause.pack(side=tk.LEFT, padx=5)

        self.btn_reset = ttk.Button(
            control_frame, text="Сброс", command=self.reset_sim
        )
        self.btn_reset.pack(side=tk.LEFT, padx=5)

        self.btn_export = ttk.Button(
            control_frame, text="Сохранить в CSV", command=self.export_csv
        )
        self.btn_export.pack(side=tk.RIGHT, padx=5)

        self.lbl_status = ttk.Label(
            control_frame,
            text="Статус: Готов к запуску",
            font=("Arial", 10, "bold"),
        )
        self.lbl_status.pack(side=tk.LEFT, padx=20)

        matrix_frame = ttk.LabelFrame(
            self.root, text=" Матрица вероятностей переходов P ", padding=10
        )
        matrix_frame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=5)

        for col_idx, name in enumerate(self.STATE_NAMES):
            lbl = ttk.Label(
                matrix_frame, text=f"В {name}", font=("Arial", 9, "bold")
            )
            lbl.grid(row=0, column=col_idx + 1, padx=10, pady=2)

        self.matrix_entries = []
        for row_idx, row_name in enumerate(self.STATE_NAMES):
            lbl = ttk.Label(
                matrix_frame, text=f"Из {row_name}:", font=("Arial", 9, "bold")
            )
            lbl.grid(row=row_idx + 1, column=0, padx=10, pady=2, sticky=tk.E)

            entry_row = []
            for col_idx in range(self.NUM_STATES):
                entry = ttk.Entry(matrix_frame, width=10, justify="center")
                entry.insert(0, f"{self.P[row_idx, col_idx]:.3f}")
                entry.grid(row=row_idx + 1, column=col_idx + 1, padx=5, pady=2)
                entry_row.append(entry)
            self.matrix_entries.append(entry_row)

        self.btn_apply_matrix = ttk.Button(
            matrix_frame, text="Применить матрицу", command=self.apply_matrix
        )
        self.btn_apply_matrix.grid(
            row=1, column=self.NUM_STATES + 1, rowspan=3, padx=15, pady=5
        )

    def apply_matrix(self):
        new_P = np.zeros((self.NUM_STATES, self.NUM_STATES))

        try:
            for i in range(self.NUM_STATES):
                for j in range(self.NUM_STATES):
                    val = float(self.matrix_entries[i][j].get().replace(",", "."))
                    if val < 0:
                        raise ValueError("Вероятности не могут быть отрицательными.")
                    new_P[i, j] = val
        except ValueError as e:
            messagebox.showerror(
                "Ошибка ввода",
                f"Введите корректные неотрицательные числа!\n\nДетали: {e}",
            )
            return

        for i in range(self.NUM_STATES):
            row_sum = new_P[i].sum()
            if row_sum == 0:
                messagebox.showerror(
                    "Ошибка матрицы",
                    f"Сумма элементов в строке {i+1} ('Из {self.STATE_NAMES[i]}') не может быть равна 0!",
                )
                return
            if not np.isclose(row_sum, 1.0, atol=1e-3):
                new_P[i] = new_P[i] / row_sum

        self.P = new_P
        for i in range(self.NUM_STATES):
            for j in range(self.NUM_STATES):
                self.matrix_entries[i][j].delete(0, tk.END)
                self.matrix_entries[i][j].insert(0, f"{self.P[i, j]:.3f}")

        self.recalculate_theoretical_pi()

        for bar, val_theo in zip(self.bars_theo, self.pi_theoretical):
            bar.set_height(val_theo)

        self.reset_sim()
        messagebox.showinfo(
            "Успешно",
            "Новая матрица вероятностей успешно применена и нормирована!",
        )

    def _setup_plots(self):
        self.fig, (self.ax_line, self.ax_bar) = plt.subplots(
            2, 1, figsize=(10, 6)
        )
        self.fig.suptitle(
            "Марковская модель погоды в реальном времени",
            fontsize=13,
            fontweight="bold",
        )

        (self.line,) = self.ax_line.plot(
            [],
            [],
            marker="o",
            markersize=3,
            color="navy",
            linestyle="-",
            alpha=0.7,
        )
        self.ax_line.set_xlim(0, self.TOTAL_DAYS)
        self.ax_line.set_ylim(-0.5, 2.5)
        self.ax_line.set_yticks([0, 1, 2])
        self.ax_line.set_yticklabels(
            ["1 — Ясно", "2 — Облачно", "3 — Пасмурно"]
        )
        self.ax_line.set_xlabel("День")
        self.ax_line.set_ylabel("Состояние погоды")
        self.ax_line.grid(True, linestyle="--", alpha=0.5)

        x_indices = np.arange(self.NUM_STATES)
        bar_width = 0.35

        self.bars_emp = self.ax_bar.bar(
            x_indices - bar_width / 2,
            [0, 0, 0],
            bar_width,
            label="Эмпирическое",
            color="skyblue",
        )
        self.bars_theo = self.ax_bar.bar(
            x_indices + bar_width / 2,
            self.pi_theoretical,
            bar_width,
            label="Теоретическое (Стационарное)",
            color="orange",
            alpha=0.8,
        )

        self.ax_bar.set_xticks(x_indices)
        self.ax_bar.set_xticklabels(["1 — Ясно", "2 — Облачно", "3 — Пасмурно"])
        self.ax_bar.set_ylim(0, 1.0)
        self.ax_bar.set_ylabel("Доля времени (Вероятность)")
        self.ax_bar.legend(loc="upper right")
        self.ax_bar.grid(True, linestyle="--", alpha=0.5, axis="y")

        self.text_stats = self.ax_bar.text(
            0.02,
            0.70,
            "",
            transform=self.ax_bar.transAxes,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )

        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(
            side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10
        )

        self.canvas.draw()

    def update_plot(self, frame):
        if not self.is_running:
            return self.line, self.bars_emp, self.text_stats

        if len(self.history_days) >= self.TOTAL_DAYS:
            self.pause_sim()
            self.lbl_status.config(text="Статус: Моделирование завершено")
            messagebox.showinfo(
                "Готово",
                f"Моделирование на {self.TOTAL_DAYS} дней успешно завершено!",
            )
            return self.line, self.bars_emp, self.text_stats

        current_state = self.history_states[-1]
        next_state = np.random.choice(self.NUM_STATES, p=self.P[current_state])

        current_day = len(self.history_days)
        self.history_days.append(current_day)
        self.history_states.append(next_state)
        self.state_counts[next_state] += 1

        self.line.set_data(self.history_days, self.history_states)

        total_simulated = len(self.history_states)
        emp_freqs = self.state_counts / total_simulated

        for bar, val in zip(self.bars_emp, emp_freqs):
            bar.set_height(val)

        mae = np.mean(np.abs(emp_freqs - self.pi_theoretical))

        self.text_stats.set_text(
            f"День: {current_day} / {self.TOTAL_DAYS}\n"
            f"Текущее состояние: {self.STATES[next_state]}\n"
            f"Среднее отклонение (MAE): {mae:.4f}"
        )

        return self.line, self.bars_emp, self.text_stats

    def start_sim(self):
        if not self.is_running:
            self.is_running = True
            self.btn_start.config(state=tk.DISABLED)
            self.btn_pause.config(state=tk.NORMAL)
            self.lbl_status.config(text="Статус: Выполняется расчет...")
            if self.anim:
                self.anim.event_source.start()

    def pause_sim(self):
        if self.is_running:
            self.is_running = False
            if self.anim:
                self.anim.event_source.stop()
            self.btn_start.config(state=tk.NORMAL)
            self.btn_pause.config(state=tk.DISABLED)
            self.lbl_status.config(text="Статус: Пауза")

    def reset_sim(self):
        self.pause_sim()
        self.reset_data()

        self.line.set_data([], [])
        for bar in self.bars_emp:
            bar.set_height(0)
        self.text_stats.set_text("")
        self.canvas.draw()

        self.lbl_status.config(text="Статус: Сброшено")

    def export_csv(self):
        if len(self.history_days) <= 1:
            messagebox.showwarning(
                "Предупреждение", "Сначала запустите симуляцию!"
            )
            return

        #Первый файл
        log_filename = "weather_simulation_daily_log.csv"
        with open(log_filename, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["Day", "State_ID", "State_Name"])
            for day, state in zip(self.history_days, self.history_states):
                writer.writerow([day, state + 1, self.STATE_NAMES[state]])

        #Второй файл
        summary_filename = "weather_stats_summary.csv"
        total_simulated = len(self.history_states)
        emp_freqs = self.state_counts / total_simulated
        with open(summary_filename, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(
                [
                    "State_ID",
                    "State_Name",
                    "Days_Count",
                    "Empirical_Frequency",
                    "Theoretical_Stationary_Prob",
                    "Absolute_Difference",
                ]
            )
            for i in range(self.NUM_STATES):
                abs_diff = abs(emp_freqs[i] - self.pi_theoretical[i])
                writer.writerow(
                    [
                        i + 1,
                        self.STATE_NAMES[i],
                        self.state_counts[i],
                        f"{emp_freqs[i]:.6f}",
                        f"{self.pi_theoretical[i]:.6f}",
                        f"{abs_diff:.6f}",
                    ]
                )

        messagebox.showinfo(
            "Успех",
            f"Данные сохранены в файлы:\n1. {log_filename}\n2. {summary_filename}",
        )
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherMarkovApp(root)
    root.mainloop()