import tkinter as tk
import random

CELL_SIZE = 7
COLS, ROWS = 110, 70
DELAY = 100

EMPTY = 0
TREE = 1
WET_TREE = 2
BURNING = 3

COLORS = {
    EMPTY: "#222222",
    TREE: "#2ecc71",
    WET_TREE: "#1e5e3a",
    BURNING: "#e74c3c"
}
P_GROWTH = 0.005

class FireSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Пожар")

        self.is_paused = True
        self.wind_bonus = tk.DoubleVar(value=0.25)
        self.prob_wet = tk.DoubleVar(value=0.05)
        self.temperature = tk.DoubleVar(value=20.0)

        self.prob_spontaneous = tk.DoubleVar(value=2.0)

        self.p_spread_normal_base = 0.25
        self.wind_dir = (1, 0)

        self.grid = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        self.initialize_grid()
        self.setup_gui()
        self.ignite_center()

        self.draw_all()
        self.update_loop()

    def setup_gui(self):
        main_frame = tk.Frame(self.root, bg="#222222")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(main_frame, width=COLS * CELL_SIZE, height=ROWS * CELL_SIZE, bg=COLORS[EMPTY],
                                highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=5, pady=5)

        settings_frame = tk.Frame(main_frame, bg="#333333", padx=10, pady=10)
        settings_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        tk.Label(settings_frame, text="Интенсивность ветра", fg="#f1c40f", bg="#333333", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(5, 0))
        scale_wind = tk.Scale(settings_frame, from_=0.0, to=0.5, resolution=0.05, orient=tk.HORIZONTAL, variable=self.wind_bonus, bg="#333333", fg="white", highlightthickness=0)
        scale_wind.pack(fill=tk.X, pady=(0, 10))

        tk.Label(settings_frame, text="Горючесть влажного леса", fg="#2ecc71", bg="#333333",font=("Arial", 9, "bold")).pack(anchor=tk.W)
        scale_wet = tk.Scale(settings_frame, from_=0.0, to=0.3, resolution=0.02, orient=tk.HORIZONTAL, variable=self.prob_wet, bg="#333333", fg="white", highlightthickness=0)
        scale_wet.pack(fill=tk.X, pady=(0, 10))

        tk.Label(settings_frame, text="Температура воздуха (°C)", fg="#e67e22", bg="#333333", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        scale_temp = tk.Scale(settings_frame, from_=-10.0, to=50.0, resolution=5.0, orient=tk.HORIZONTAL, variable=self.temperature, bg="#333333", fg="white", highlightthickness=0)
        scale_temp.pack(fill=tk.X, pady=(0, 10))

        tk.Label(settings_frame, text="Частота ударов молний", fg="#e74c3c", bg="#333333", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        scale_lightning = tk.Scale(settings_frame, from_=0.0, to=15.0, resolution=1.0, orient=tk.HORIZONTAL, variable=self.prob_spontaneous, bg="#333333", fg="white", highlightthickness=0)
        scale_lightning.pack(fill=tk.X, pady=(0, 20))

        self.btn_pause = tk.Button(settings_frame, text="СТАРТ СИМУЛЯЦИИ", command=self.toggle_pause, bg="#27ae60", fg="white", font=("Arial", 11, "bold"), height=2)
        self.btn_pause.pack(fill=tk.X, pady=5)

        btn_reset = tk.Button(settings_frame, text="СБРОСИТЬ", command=self.reset_simulation, bg="#7f8c8d", fg="white", font=("Arial", 9, "bold"))
        btn_reset.pack(fill=tk.X, pady=5)

    def initialize_grid(self):
        for r in range(ROWS):
            for c in range(COLS):
                rand = random.random()
                if rand < 0.50:
                    self.grid[r][c] = TREE
                elif rand < 0.70:
                    self.grid[r][c] = WET_TREE
                else:
                    self.grid[r][c] = EMPTY

    def ignite_center(self):
        mid_r, mid_c = ROWS // 2, COLS // 2
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if 0 <= mid_r + dr < ROWS and 0 <= mid_c + dc < COLS:
                    self.grid[mid_r + dr][mid_c + dc] = BURNING

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.config(text="ПРОДОЛЖИТЬ", bg="#3498db")
        else:
            self.btn_pause.config(text="ПОСТАВИТЬ НА ПАУЗУ", bg="#e67e22")

    def reset_simulation(self):
        self.initialize_grid()
        self.ignite_center()
        self.draw_all()
        self.is_paused = True
        self.btn_pause.config(text="СТАРТ СИМУЛЯЦИИ", bg="#27ae60")

    def draw_cell(self, r, c):
        x1, y1 = c * CELL_SIZE, r * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        color = COLORS[self.grid[r][c]]
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def draw_all(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] != EMPTY:
                    self.draw_cell(r, c)

    def update_loop(self):
        if not self.is_paused:
            next_grid = [row[:] for row in self.grid]

            current_wind_bonus = self.wind_bonus.get()
            current_p_spread_wet = self.prob_wet.get()
            current_temp = self.temperature.get()
            current_p_spontaneous = (self.prob_spontaneous.get() / 100000)

            temp_modifier = max(0.0, current_temp * 0.005)
            effective_p_normal = self.p_spread_normal_base + temp_modifier

            for r in range(ROWS):
                for c in range(COLS):
                    if self.grid[r][c] == BURNING:
                        next_grid[r][c] = EMPTY

                    elif self.grid[r][c] == EMPTY:
                        if random.random() < P_GROWTH:
                            next_grid[r][c] = TREE if random.random() < 0.80 else WET_TREE

                    elif self.grid[r][c] in (TREE, WET_TREE):
                        is_ignited = False
                        base_prob = effective_p_normal if self.grid[r][c] == TREE else current_p_spread_wet
                        for dr in [-1, 0, 1]:
                            for dc in [-1, 0, 1]:
                                if dr == 0 and dc == 0:
                                    continue

                                nr, nc = r + dr, c + dc
                                if 0 <= nr < ROWS and 0 <= nc < COLS:
                                    if self.grid[nr][nc] == BURNING:
                                        if dr == self.wind_dir[1] and dc == self.wind_dir[0]:
                                            final_prob = base_prob + current_wind_bonus
                                        else:
                                            final_prob = base_prob

                                        if random.random() < final_prob:
                                            is_ignited = True
                                            break
                            if is_ignited:
                                break
                        if is_ignited:
                            next_grid[r][c] = BURNING
                        elif random.random() < current_p_spontaneous:
                            next_grid[r][c] = BURNING

            self.grid = next_grid
            self.draw_all()

        self.root.after(DELAY, self.update_loop)

root = tk.Tk()
app = FireSimulation(root)
root.mainloop()