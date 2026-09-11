import math
import tkinter as tk
from tkinter import messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np


class PuassonApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Моделирование Пуассоновского потока запросов")
    self.root.geometry("950x600")

    control_frame = ttk.LabelFrame(root, text=" Параметры модели ", padding=10)
    control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    ttk.Label(control_frame, text="Интенсивность λ (запр/сек):").pack(
        anchor=tk.W, pady=(5, 0)
    )
    self.entry_lambda = ttk.Entry(control_frame)
    self.entry_lambda.insert(0, "5.0")
    self.entry_lambda.pack(fill=tk.X, pady=(0, 10))

    ttk.Label(control_frame, text="Интервал времени T (сек):").pack(
        anchor=tk.W, pady=(5, 0)
    )
    self.entry_T = ttk.Entry(control_frame)
    self.entry_T.insert(0, "2.0")
    self.entry_T.pack(fill=tk.X, pady=(0, 10))

    ttk.Label(control_frame, text="Число экспериментов (N):").pack(
        anchor=tk.W, pady=(5, 0)
    )
    self.entry_N = ttk.Entry(control_frame)
    self.entry_N.insert(0, "10000")
    self.entry_N.pack(fill=tk.X, pady=(0, 15))

    btn_run = ttk.Button(
        control_frame,
        text=" Запустить симуляцию",
        command=self.run_simulation,
    )
    btn_run.pack(fill=tk.X, pady=5)

    ttk.Label(control_frame, text="Результаты:").pack(
        anchor=tk.W, pady=(15, 0)
    )
    self.txt_results = tk.Text(
        control_frame, width=32, height=15, font=("Arial", 9)
    )
    self.txt_results.pack(fill=tk.BOTH, expand=True, pady=5)

    plot_frame = ttk.Frame(root, padding=10)
    plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    self.fig, self.ax = plt.subplots(figsize=(6, 5))
    self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
    self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    self.ax.set_title("Установите параметры и нажмите кнопку запуск")
    self.canvas.draw()

  def run_simulation(self):
    try:
      lam = float(self.entry_lambda.get())
      T = float(self.entry_T.get())
      N = int(self.entry_N.get())
      if lam <= 0 or T <= 0 or N <= 0:
        raise ValueError
    except ValueError:
      messagebox.showerror(
          "Ошибка", "Введите корректные положительные числа!"
      )
      return

    #поток
    requests_per_interval = []
    for _ in range(N):
      t = 0.0
      count = 0
      while True:
        dt = np.random.exponential(scale=1.0 / lam)
        t += dt
        if t <= T:
          count += 1
        else:
          break
      requests_per_interval.append(count)

    requests_per_interval = np.array(requests_per_interval)

    emp_mean = np.mean(requests_per_interval)
    emp_var = np.var(requests_per_interval, ddof=1)
    theo_val = lam * T

    self.txt_results.delete("1.0", tk.END)
    res_text = (
        f"=== СТАТИСТИКА ===\n"
        f"λ = {lam} | T = {T}c | N = {N}\n"
        f"Теоретич. λT = {theo_val:.2f}\n\n"
        f"Среднее (E[X]):\n"
        f"  Эмпирич: {emp_mean:.4f}\n"
        f"  Теоретич: {theo_val:.4f}\n\n"
        f"Дисперсия (Var[X]):\n"
        f"  Эмпирич: {emp_var:.4f}\n"
        f"  Теоретич: {theo_val:.4f}\n\n")
    self.txt_results.insert(tk.END, res_text)

    self.ax.clear()
    max_k = np.max(requests_per_interval)
    unique, counts = np.unique(requests_per_interval, return_counts=True)
    emp_probs = counts / N

    k_values = np.arange(0, max_k + 1)

    theo_probs = [
        (theo_val**k) * math.exp(-theo_val) / math.factorial(k)
        for k in k_values
    ]

    self.ax.bar(
        unique,
        emp_probs,
        width=0.6,
        alpha=0.6,
        color="#4A90E2",
        edgecolor="black",
        label="Эмпирическое",
    )
    self.ax.plot(
        k_values,
        theo_probs,
        "ro--",
        linewidth=2,
        markersize=5,
        label=f"Пуассон (Puass({theo_val}))",
    )

    self.ax.set_title(f"Распределение за T = {T} c (λ = {lam})")
    self.ax.set_xlabel("Число запросов (k)")
    self.ax.set_ylabel("Вероятность P(X = k)")
    self.ax.set_xticks(k_values)
    self.ax.grid(True, linestyle="--", alpha=0.5)
    self.ax.legend()
    self.fig.tight_layout()

    self.canvas.draw()


if __name__ == "__main__":
  root = tk.Tk()
  app = PuassonApp(root)
  root.mainloop()