import math
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#функция нормального распределения
def norm_cdf(x, mu, std):
    if x == np.inf:
        return 1.0
    if x == -np.inf:
        return 0.0
    return 0.5 * (1.0 + math.erf((x - mu) / (std * math.sqrt(2))))

#плотность нормального распределения
def norm_pdf(x, mu, std):
    return (1.0 / (std * np.sqrt(2.0 * np.pi))) * np.exp(-0.5 * ((x - mu) / std) ** 2)

#дискретная св
class DiscreteRVTab:
    def __init__(self, parent):
        self.frame = parent
        self.setup_ui()

    def setup_ui(self):
        left_frame = tk.Frame(self.frame, bg="#90e0ef", padx=20, pady=20)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.prob_entries = []
        for i in range(4):
            lbl = tk.Label(left_frame, text=f"Prob {i+1}", font=("Arial", 14), bg="#90e0ef")
            lbl.grid(row=i, column=0, sticky="w", pady=8)
            entry = tk.Entry(left_frame, font=("Arial", 14), width=8, justify="center")
            entry.grid(row=i, column=1, pady=8, padx=10)
            self.prob_entries.append(entry)

        default_p = ["0.25", "0.15", "0.20", "0.20"]
        for entry, val in zip(self.prob_entries, default_p):
            entry.insert(0, val)

        lbl_p5 = tk.Label(left_frame, text="Prob 5", font=("Arial", 14), bg="#90e0ef")
        lbl_p5.grid(row=4, column=0, sticky="w", pady=8)
        self.p5_button = tk.Button(
            left_frame, text="auto", font=("Arial", 12), width=7, relief=tk.RAISED, state=tk.DISABLED
        )
        self.p5_button.grid(row=4, column=1, pady=8, padx=10)

        lbl_n = tk.Label(left_frame, text="Число экспериментов", font=("Arial", 12), bg="#90e0ef")
        lbl_n.grid(row=5, column=0, sticky="w", pady=(20, 8))
        self.n_entry = tk.Entry(left_frame, font=("Arial", 14), width=8, justify="center")
        self.n_entry.grid(row=5, column=1, pady=(20, 8), padx=10)
        self.n_entry.insert(0, "1000")

        btn_start = tk.Button(
            left_frame,
            text="Запуск",
            font=("Arial", 14, "bold"),
            bg="#0077b6",
            fg="white",
            activebackground="#023e8a",
            activeforeground="white",
            width=10,
            command=self.run_simulation
        )
        btn_start.grid(row=6, column=0, columnspan=2, pady=25)

        right_frame = tk.Frame(self.frame, bg="#90e0ef", padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.fig, self.ax = plt.subplots(figsize=(5.5, 3.2), dpi=100)
        self.fig.patch.set_facecolor("#90e0ef")
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.results_frame = tk.Frame(right_frame, bg="#90e0ef")
        self.results_frame.pack(fill=tk.X, pady=5)

        self.lbl_avg = tk.Label(self.results_frame, text="Avg: -", font=("Arial", 14), bg="#90e0ef", anchor="w")
        self.lbl_avg.pack(fill=tk.X)

        self.lbl_var = tk.Label(self.results_frame, text="Var: -", font=("Arial", 14), bg="#90e0ef", anchor="w")
        self.lbl_var.pack(fill=tk.X)


    def run_simulation(self):
        try:
            p1_4 = [float(e.get().replace(",", ".")) for e in self.prob_entries]
            sum_p = sum(p1_4)

            if sum_p >= 1.0 or any(p < 0 for p in p1_4):
                messagebox.showerror("Ошибка", "Сумма P1..P4 должна быть меньше 1, а вероятности >= 0!")
                return

            p5 = 1.0 - sum_p
            probs = np.array(p1_4 + [p5])
            N = int(self.n_entry.get())

            if N <= 0:
                messagebox.showerror("Ошибка", "Размер выборки N должен быть больше 0!")
                return

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения!")
            return

        values = np.array([1, 2, 3, 4, 5])
        cum_probs = np.cumsum(probs)
        u = np.random.rand(N)
        samples = np.searchsorted(cum_probs, u) + 1

        counts = np.array([np.sum(samples == v) for v in values])
        emp_probs = counts / N

        e_mean = np.sum(values * probs)
        e_var = np.sum((values ** 2) * probs) - (e_mean ** 2)

        emp_mean = np.mean(samples)
        emp_var = np.var(samples)

        err_mean = (abs(emp_mean - e_mean) / abs(e_mean)) * 100 if e_mean != 0 else 0
        err_var = (abs(emp_var - e_var) / abs(e_var)) * 100 if e_var != 0 else 0

        expected_counts = N * probs
        chi2_stat = np.sum(((counts - expected_counts) ** 2) / expected_counts)

        # табличное критическое значение для df = 5 - 1 = 4, a = 0.05
        chi2_crit = 9.488
        is_greater = chi2_stat > chi2_crit

        self.ax.clear()
        bars = self.ax.bar(values, emp_probs, color="#8ecae6", edgecolor="#219ebc", width=0.8, hatch="..")
        self.ax.set_ylabel("freq.", fontsize=10)
        self.ax.set_ylim(0, max(max(emp_probs) * 1.25, 0.3))
        self.ax.set_xticks(values)
        self.ax.grid(axis='y', linestyle='--', alpha=0.5)

        for bar, prob in zip(bars, emp_probs):
            yval = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.01, f"{prob:.3f}",
                         ha='center', va='bottom', fontsize=9)

        self.fig.tight_layout()
        self.canvas.draw()

        self.lbl_avg.config(text=f"Avg: {emp_mean:.3f} (error = {err_mean:.0f}%)")
        self.lbl_var.config(text=f"Var: {emp_var:.3f} (error = {err_var:.0f}%)")

        status_text = "true" if is_greater else "false"
        status_color = "red" if is_greater else "green"

        for widget in self.results_frame.winfo_children():
            if getattr(widget, "_is_chi_container", False):
                widget.destroy()

        chi_container = tk.Frame(self.results_frame, bg="#90e0ef")
        chi_container._is_chi_container = True
        chi_container.pack(fill=tk.X)

        tk.Label(chi_container, text=f"Chi-squared: {chi2_stat:.2f} > {chi2_crit:.3f}  is ",
                 font=("Arial", 14), bg="#90e0ef").pack(side=tk.LEFT)
        tk.Label(chi_container, text=status_text, font=("Arial", 14, "bold"),
                 fg=status_color, bg="#90e0ef").pack(side=tk.LEFT)

#нормальная св
class NormalRVTab:
    def __init__(self, parent):
        self.frame = parent
        self.setup_ui()

    def setup_ui(self):
        left_frame = tk.Frame(self.frame, bg="#90e0ef", padx=20, pady=20)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        lbl_mean = tk.Label(left_frame, text="Mean", font=("Arial", 14), bg="#90e0ef")
        lbl_mean.grid(row=0, column=0, sticky="w", pady=12)
        self.mean_entry = tk.Entry(left_frame, font=("Arial", 14), width=8, justify="center")
        self.mean_entry.grid(row=0, column=1, pady=12, padx=10)
        self.mean_entry.insert(0, "0.5")

        lbl_var = tk.Label(left_frame, text="Var", font=("Arial", 14), bg="#90e0ef")
        lbl_var.grid(row=1, column=0, sticky="w", pady=12)
        self.var_entry = tk.Entry(left_frame, font=("Arial", 14), width=8, justify="center")
        self.var_entry.grid(row=1, column=1, pady=12, padx=10)
        self.var_entry.insert(0, "1.0")

        lbl_size = tk.Label(left_frame, text="Sample size", font=("Arial", 14), bg="#90e0ef")
        lbl_size.grid(row=2, column=0, sticky="w", pady=12)
        self.size_entry = tk.Entry(left_frame, font=("Arial", 14), width=8, justify="center")
        self.size_entry.grid(row=2, column=1, pady=12, padx=10)
        self.size_entry.insert(0, "1000")

        btn_start = tk.Button(
            left_frame,
            text="Запуск",
            font=("Arial", 14, "bold"),
            bg="#0077b6",
            fg="white",
            activebackground="#023e8a",
            activeforeground="white",
            width=10,
            command=self.run_simulation
        )
        btn_start.grid(row=3, column=0, columnspan=2, pady=30)

        right_frame = tk.Frame(self.frame, bg="#90e0ef", padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.fig, self.ax = plt.subplots(figsize=(5.5, 3.2), dpi=100)
        self.fig.patch.set_facecolor("#90e0ef")
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.results_frame = tk.Frame(right_frame, bg="#90e0ef")
        self.results_frame.pack(fill=tk.X, pady=5)

        self.lbl_avg = tk.Label(self.results_frame, text="Avg: -", font=("Arial", 14), bg="#90e0ef", anchor="w")
        self.lbl_avg.pack(fill=tk.X)

        self.lbl_var = tk.Label(self.results_frame, text="Var: -", font=("Arial", 14), bg="#90e0ef", anchor="w")
        self.lbl_var.pack(fill=tk.X)

    def generate_normal_box_muller(self, mu, std, N):
        n_pairs = (N + 1) // 2
        u1 = np.random.rand(n_pairs)
        u2 = np.random.rand(n_pairs)

        z0 = np.sqrt(-2.0 * np.log(u1)) * np.cos(2.0 * np.pi * u2)
        z1 = np.sqrt(-2.0 * np.log(u1)) * np.sin(2.0 * np.pi * u2)

        z = np.concatenate([z0, z1])[:N]
        return mu + std * z


    def run_simulation(self):
        try:
            mu = float(self.mean_entry.get().replace(",", "."))
            var_th = float(self.var_entry.get().replace(",", "."))
            N = int(self.size_entry.get())

            if var_th <= 0 or N <= 0:
                messagebox.showerror("Ошибка", "Дисперсия и выборка должны быть > 0!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения!")
            return

        std_th = np.sqrt(var_th)
        samples = self.generate_normal_box_muller(mu, std_th, N)

        emp_mean = np.mean(samples)
        emp_var = np.var(samples)

        err_mean = (abs(emp_mean - mu) / abs(mu)) * 100 if mu != 0 else abs(emp_mean) * 100
        err_var = (abs(emp_var - var_th) / var_th) * 100

        k = 6
        bins_inner = np.linspace(mu - 3 * std_th, mu + 3 * std_th, k + 1)
        counts, _ = np.histogram(samples, bins=bins_inner)

        #теоретические вероятности
        prob_expected = []
        for i in range(k):
            low = -np.inf if i == 0 else bins_inner[i]
            high = np.inf if i == k - 1 else bins_inner[i + 1]
            p = norm_cdf(high, mu, std_th) - norm_cdf(low, mu, std_th)
            prob_expected.append(p)

        prob_expected = np.array(prob_expected)
        expected_counts = N * prob_expected

        chi2_stat = np.sum(((counts - expected_counts) ** 2) / expected_counts)

        #табличное значение для df = 6 - 1 = 5, a = 0.05
        chi2_crit = 11.070
        is_greater = chi2_stat > chi2_crit

        self.ax.clear()

        rel_freqs = counts / N
        bin_centers = (bins_inner[:-1] + bins_inner[1:]) / 2
        bin_width = bins_inner[1] - bins_inner[0]

        self.ax.bar(bin_centers, rel_freqs, width=bin_width * 0.95, color="#a2d2ff",
                    edgecolor="#b7094c", alpha=0.85)

        #кривая плотности
        x_curve = np.linspace(mu - 3.5 * std_th, mu + 3.5 * std_th, 200)
        y_curve = norm_pdf(x_curve, mu, std_th) * bin_width
        self.ax.plot(x_curve, y_curve, color="#52b788", linewidth=2.5)

        x_labels = [f"({bins_inner[i]:.1f}; {bins_inner[i+1]:.1f}]" for i in range(k)]
        self.ax.set_xticks(bin_centers)
        self.ax.set_xticklabels(x_labels, fontsize=8)
        self.ax.set_ylim(0, max(max(rel_freqs) * 1.2, max(y_curve) * 1.2))
        self.ax.grid(axis='y', linestyle='--', alpha=0.4)

        self.fig.tight_layout()
        self.canvas.draw()

        self.lbl_avg.config(text=f"Avg: {emp_mean:.3f} (error = {err_mean:.0f}%)")
        self.lbl_var.config(text=f"Var: {emp_var:.3f} (error = {err_var:.0f}%)")

        status_text = "true" if is_greater else "false"
        status_color = "red" if is_greater else "green"

        for widget in self.results_frame.winfo_children():
            if getattr(widget, "_is_chi_container", False):
                widget.destroy()

        chi_container = tk.Frame(self.results_frame, bg="#90e0ef")
        chi_container._is_chi_container = True
        chi_container.pack(fill=tk.X)

        tk.Label(chi_container, text=f"Chi-squared: {chi2_stat:.2f} > {chi2_crit:.2f}  is ",
                 font=("Arial", 14), bg="#90e0ef").pack(side=tk.LEFT)
        tk.Label(chi_container, text=status_text, font=("Arial", 14, "bold"),
                 fg=status_color, bg="#90e0ef").pack(side=tk.LEFT)


class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Лаб 6: моделирование св")
        self.root.geometry("920x570")
        self.root.configure(bg="#90e0ef")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background="#90e0ef", borderwidth=0)
        style.configure("TNotebook.Tab", font=("Arial", 11, "bold"), padding=[15, 5], background="#caf0f8")
        style.map("TNotebook.Tab", background=[("selected", "#0077b6")], foreground=[("selected", "white")])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab1 = tk.Frame(self.notebook, bg="#90e0ef")
        self.notebook.add(self.tab1, text=" Lab 06-1 (Дискретная СВ) ")
        self.app_tab1 = DiscreteRVTab(self.tab1)

        self.tab2 = tk.Frame(self.notebook, bg="#90e0ef")
        self.notebook.add(self.tab2, text=" Lab 06-2 (Нормальная СВ) ")
        self.app_tab2 = NormalRVTab(self.tab2)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()