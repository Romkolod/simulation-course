import random
import tkinter as tk
from tkinter import ttk, messagebox


class RandomEventsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Моделирование случайных событий")
        self.root.geometry("480x520")
        self.root.resizable(False, False)

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Вкладка 1
        self.tab_yes_no = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_yes_no, text="1. Да / Нет")
        self._build_yes_no_tab()

        # Вкладка 2
        self.tab_8ball = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_8ball, text="2. Magic 8-Ball")
        self._build_8ball_tab()

    # ДА/НЕТ
    def _build_yes_no_tab(self):
        container = ttk.Frame(self.tab_yes_no, padding=20)
        container.pack(fill="both", expand=True)

        lbl_title = ttk.Label(
            container,
            text="Приложение «Да или Нет»",
            font=("", 14, "bold")
        )
        lbl_title.pack(pady=(0, 15))

        lbl_prompt = ttk.Label(
            container,
            text="Задайте вопрос, на который можно ответить однозначно:",
            font=("", 10)
        )
        lbl_prompt.pack(anchor="w", pady=(0, 5))

        self.entry_yes_no = ttk.Entry(container, width=40, font=("", 11))
        self.entry_yes_no.pack(fill="x", pady=(0, 15))

        btn_get_answer = ttk.Button(
            container,
            text="Получить ответ",
            command=self._generate_yes_no
        )
        btn_get_answer.pack(pady=(0, 20))

        self.lbl_yes_no_result = tk.Label(
            container,
            text="?",
            font=("", 28, "bold"),
            bg="#e0e0e0",
            fg="#333333",
            width=12,
            height=3,
            relief="groove"
        )
        self.lbl_yes_no_result.pack()

    def _generate_yes_no(self):
        question = self.entry_yes_no.get().strip()
        if not question:
            messagebox.showwarning("Внимание", "Пожалуйста, введите вопрос!")
            return

        outcome = random.choice(["ДА", "НЕТ"])

        if outcome == "ДА":
            self.lbl_yes_no_result.config(
                text="ДА",
                bg="#4CAF50",
                fg="white"
            )
        else:
            self.lbl_yes_no_result.config(
                text="НЕТ",
                bg="#F44336",
                fg="white"
            )

    #  Шар
    def _build_8ball_tab(self):
        container = ttk.Frame(self.tab_8ball, padding=15)
        container.pack(fill="both", expand=True)

        lbl_prompt = ttk.Label(
            container,
            text="Задайте вопрос ШАРУ СУДЬБЫ:",
            font=("", 11, "bold")
        )
        lbl_prompt.pack(pady=(0, 5))

        self.entry_8ball = ttk.Entry(container, width=40, font=("", 10))
        self.entry_8ball.pack(fill="x", pady=(0, 10))

        btn_ask_ball = ttk.Button(
            container,
            text="Встряхнуть шар",
            command=self._generate_8ball_answer
        )
        btn_ask_ball.pack(pady=(0, 10))

        self.canvas = tk.Canvas(
            container,
            width=260,
            height=260,
            bg="#f0f0f0",
            highlightthickness=0
        )
        self.canvas.pack()

        self.answers = [
            "Бесспорно",
            "Предрешено",
            "Никаких сомнений",
            "Определенно да",
            "Можешь быть\nуверен в этом",

            "Мне кажется — да",
            "Вероятнее всего",
            "Хорошие\nперспективы",
            "Знаки говорят — да",
            "Да",

            "Пока не ясно,\nпопробуй снова",
            "Спроси позже",
            "Лучше не\nрассказывать",
            "Сейчас нельзя\nпредсказать",
            "Сконцентрируйся\nи спроси опять",

            "Даже не думай",
            "Мой ответ — нет",
            "По моим данным — нет",
            "Перспективы\nне очень хорошие",
            "Весьма сомнительно"
        ]

        self._draw_ball("8")

    def _draw_ball(self, text_to_display):
        self.canvas.delete("all")
        self.canvas.create_oval(10, 10, 250, 250, fill="#1a1a1a", outline="#000000", width=2)
        if text_to_display == "8":
            self.canvas.create_oval(85, 85, 175, 175, fill="white", outline="")
            self.canvas.create_text(
                130, 130,
                text="8",
                font=("", 42, "bold"),
                fill="black"
            )
        else:
            points = [130, 65, 65, 185, 195, 185]
            self.canvas.create_polygon(points, fill="#0d47a1", outline="#1976d2", width=2)

            self.canvas.create_text(
                130, 145,
                text=text_to_display,
                font=("", 9, "bold"),
                fill="white",
                justify="center"
            )

    def _generate_8ball_answer(self):
        question = self.entry_8ball.get().strip()
        if not question:
            messagebox.showwarning("Внимание", "Шар не отвечает на пустоту. Задайте вопрос!")
            return

        selected_answer = random.choice(self.answers)
        self._draw_ball(selected_answer)


if __name__ == "__main__":
    root = tk.Tk()
    app = RandomEventsApp(root)
    root.mainloop()