import flet as ft
import json
import sqlite3
from os import makedirs, path
from datetime import datetime


# ------------------- Работа с файлами -------------------

try:
    with open("beginners.json", encoding="utf-8") as f:
        students = json.load(f)
except FileNotFoundError:
    with open("beginners.json", "w", encoding="utf-8") as f:
        json.dump([], f)


class Counter(ft.UserControl):
    def __init__(self, name, coins, *args):
        super().__init__()
        self.coins = coins
        self.name = ft.ElevatedButton(
            name, bgcolor="#6495ED", color="#000000", width=240, on_click=self.add_coins
        )
        self.add_coins_field = ft.TextField(
            width=70,
            dense=True,
            input_filter=ft.NumbersOnlyInputFilter(),
            border_radius=20,
            text_align=ft.TextAlign.CENTER,
        )
        self.for_what_field = ft.TextField(
            width=200,
            dense=True,
            border_radius=20,
            text_align=ft.TextAlign.CENTER,
        )
        self.args = args

    def quick_add_coins(self, e):
        """быстрое добавление лидеркоинов по кнопкам"""
        self.coins += e.control.text
        self.text.value = self.coins
        self.save_operation_in_log(e)
        db = sqlite3.connect("lidercoins.db")
        c = db.cursor()
        c.execute(
            "UPDATE lidercoins SET number_of_coins = ? WHERE full_name = ?",
            (self.coins, self.name.text),
        )
        db.commit()
        db.close()
        self.update()

    def add_coins(self, e):
        """добавление лидеркоинов вручную"""
        db = sqlite3.connect("lidercoins.db")
        c = db.cursor()
        c.execute(
            "UPDATE lidercoins SET number_of_coins = number_of_coins + ? WHERE full_name = ?",
            (self.add_coins_field.value, self.name.text),
        )
        db.commit()
        db.close()
        self.coins += int(self.add_coins_field.value)
        self.text.value += int(self.add_coins_field.value)
        with open(f"students_logs/{self.name.text}.txt", "a", encoding="utf-8") as f:
            now = datetime.now().strftime("%d.%m.%Y")
            f.write(
                f"{now}: {self.add_coins_field.value} {self.for_what_field.value}. Всего лидеркоинов сейчас {self.coins}\n"
            )
        self.add_coins_field.value = None
        self.for_what_field.value = None
        self.update()

    def save_operation_in_log(self, e):
        with open(f"students_logs/{self.name.text}.txt", "a", encoding="utf-8") as f:
            now = datetime.now().strftime("%d.%m.%Y")
            f.write(
                f"{now}: {e.control.text} {e.control.key}. Всего лидеркоинов сейчас {self.coins}\n"
            )

    def build(self):
        self.text = ft.Text(self.coins, width=50)
        buttons = []
        buttons_text = [
            "за задачу",
            "за победу",
            "за посещение",
            "за активность",
            "за плохое поведение",
            "за плохое поведение",
        ]
        for button in self.args:
            buttons.append(
                ft.ElevatedButton(
                    text=button,
                    on_click=self.quick_add_coins,
                    key=buttons_text[self.args.index(button)],
                ),
            )
        return ft.Row(
            [
                self.name,
                self.text,
                *buttons,
                self.add_coins_field,
                self.for_what_field,
                ft.ElevatedButton("Добавить", on_click=self.add_coins),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )


def create_folder_and_files(student_list: list):
    """создание папок и файлов"""
    makedirs("students_logs", exist_ok=True)
    for student in student_list:
        filename = f"students_logs/{student[0]}.txt"
        if not path.exists(filename):
            with open(filename, "w+", encoding="utf-8") as f:
                f.write("")


# ------------------- Работа с БД -------------------


def create_db():
    """создание базы данных"""
    global students
    db = sqlite3.connect("beginners.db")
    c = db.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS lidercoins (
        full_name TEXT,
        number_of_coins INTEGER
        )"""
    )

    for student in students:
        c.execute(
            "INSERT INTO lidercoins (full_name, number_of_coins) VALUES (?, ?)",
            (student, 0),
        )

    db.commit()
    db.close()


def get_coins_and_students():
    db = sqlite3.connect("lidercoins.db")
    c = db.cursor()
    c.execute("SELECT number_of_coins FROM lidercoins")
    coins = c.fetchall()
    c.execute("SELECT full_name FROM lidercoins")
    student_list = c.fetchall()
    db.close()
    return coins, student_list


# ------------------- Класс Counter -------------------


class Counter(ft.Row):
    def __init__(self, name, coins, *args):
        super().__init__(alignment=ft.MainAxisAlignment.CENTER)

        self.full_name = name
        self.coins = int(coins)  # Храним ТОЛЬКО число
        self.args = args

        self.name_btn = ft.ElevatedButton(
            name,
            bgcolor="#6495ED",
            color="#000000",
            width=240,
            on_click=self.add_coins,
        )

        self.add_coins_field = ft.TextField(
            width=70,
            dense=True,
            border_radius=20,
            text_align=ft.TextAlign.CENTER,
        )

        self.for_what_field = ft.TextField(
            width=200,
            dense=True,
            border_radius=20,
            text_align=ft.TextAlign.CENTER,
        )

        self.text_display = ft.Text(f"🪙{self.coins}", width=100)

        labels = [
            "за задачу",
            "за победу",
            "за посещение",
            "за плохое поведение",
            "купил(а) наклейку",
        ]

        self.quick_buttons = [
            ft.ElevatedButton(
                text=str(button),
                on_click=self.quick_add_coins,
                key=labels[i] if i < len(labels) else "",
            )
            for i, button in enumerate(self.args)
        ]

        self.controls = [
            self.name_btn,
            self.text_display,
            *self.quick_buttons,
            self.add_coins_field,
            self.for_what_field,
            ft.ElevatedButton("Добавить", on_click=self.add_coins),
        ]

    # --- Быстрые добавления ---
    def quick_add_coins(self, e: ft.ControlEvent):
        try:
            value = int(e.control.text)  # "+5" → 5
        except ValueError:
            return

        self.coins += value
        self.text_display.value = f"🪙{self.coins}"
        self.save_operation_in_log(e)

        db = sqlite3.connect("beginners.db")
        c = db.cursor()
        c.execute(
            "UPDATE lidercoins SET number_of_coins = ? WHERE full_name = ?",
            (self.coins, self.full_name),
        )
        db.commit()
        db.close()
        self.update()

    # --- Ручное добавление ---
    def add_coins(self, e: ft.ControlEvent):
        try:
            value = int(self.add_coins_field.value)
        except:
            return

        self.coins += value
        self.text_display.value = f"🪙{self.coins}"

        db = sqlite3.connect("beginners.db")
        c = db.cursor()
        c.execute(
            "UPDATE lidercoins SET number_of_coins = ? WHERE full_name = ?",
            (self.coins, self.full_name),
        )
        db.commit()
        db.close()

        with open(f"students_logs/{self.full_name}.txt", "a", encoding="utf-8") as f:
            now = datetime.now().strftime("%d.%m.%Y")
            f.write(
                f"{now}: +{value} {self.for_what_field.value}. Теперь 🪙{self.coins}\n"
            )

        self.add_coins_field.value = ""
        self.for_what_field.value = ""
        self.update()

    def save_operation_in_log(self, e: ft.ControlEvent):
        with open(f"students_logs/{self.full_name}.txt", "a", encoding="utf-8") as f:
            now = datetime.now().strftime("%d.%m.%Y")
            f.write(
                f"{now}: {e.control.text} ({e.control.key}). Теперь 🪙{self.coins}\n"
            )


# ------------------- Главная функция -------------------


def main(page: ft.Page):
    if not path.exists("lidercoins.db"):
        create_db()

    coins, student_list = get_coins_and_students()
    create_folder_and_files(student_list)

    page.title = "Лидеркоины"
    page.theme_mode = "DARK"
    page.scroll = True
    title = ft.Row(
        [
            ft.Text('Группа "Шахматы"', size=30),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    page.add(title)
    for student in student_list:
        page.controls.append(
            Counter(student[0], coins[student_list.index(student)][0], 1, 5, 10, 15, -1)
        )
    page.update()


ft.app(target=main)
