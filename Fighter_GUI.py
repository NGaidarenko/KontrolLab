import asyncio
import tkinter as tk
from tkinter import messagebox
import random
import sqlite3

import Console_GUI
import fightclass
import fighters
import exceptions
import BotThread


def clear_window(window):
    for widget in window.winfo_children():
        widget.destroy()


class FighterSelectionWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Выбор бойцов")

        self.selected_fighters = []

        fighters_1 = ['Боксер-1', 'Дзюдоист-1', 'Каратист-1']
        fighters_2 = ['Боксер-2', 'Дзюдоист-2', 'Каратист-2']

        label = tk.Label(self.root, text="Выберите двух бойцов:")
        label.grid(row=0, column=0, columnspan=3)

        self.first_fighter_var = tk.StringVar()
        self.second_fighter_var = tk.StringVar()

        self.first_fighter_var.set("Выберите бойца")
        self.second_fighter_var.set("Выберите бойца")

        first_fighter_label = tk.Label(self.root, text="Первый боец:")
        first_fighter_label.grid(row=1, column=0)
        self.first_fighter_menu = tk.OptionMenu(self.root, self.first_fighter_var, *fighters_1)
        self.first_fighter_menu.grid(row=1, column=1)

        second_fighter_label = tk.Label(self.root, text="Второй боец:")
        second_fighter_label.grid(row=2, column=0)
        self.second_fighter_menu = tk.OptionMenu(self.root, self.second_fighter_var, *fighters_2)
        self.second_fighter_menu.grid(row=2, column=1)

        select_button = tk.Button(self.root, text="Выбрать", command=self.select_fighters)
        select_button.grid(row=3, column=1)

    def select_fighter_class(self, fighter):
        if "Боксер" in fighter:
            return fighters.Boxer(fighter)
        elif "Дзюдоист" in fighter:
            return fighters.Judoka(fighter)
        elif "Каратист" in fighter:
            return fighters.Karate(fighter)
        else:
            raise exceptions.IncorrectInputExcError

    def select_fighters(self):
        first_fighter = self.select_fighter_class(self.first_fighter_var.get())
        second_fighter = self.select_fighter_class(self.second_fighter_var.get())

        if first_fighter == "Выберите бойца" or second_fighter == "Выберите бойца":
            messagebox.showerror("Ошибка", "Пожалуйста, выберите двух разных бойцов.")
        else:
            clear_window(self.root)
            self.selected_fighters = [first_fighter, second_fighter]

            MatchWindow(self.root, self.selected_fighters[0], self.selected_fighters[1])


class MatchWindow:
    def __init__(self, root, fighter1, fighter2):
        self.root = root
        self.root.title("Бой")

        self.fighter1 = fighter1
        self.fighter2 = fighter2

        self.temp_label = tk.Label(self.root, text="")
        self.result_label = tk.Label(self.root, text="")
        self.temp_label.pack()
        self.result_label.pack()

        self.back_button = tk.Button(self.root, text="Назад", command=self.back_to_main_menu, state=tk.DISABLED)
        self.back_button.pack()

        self.start_battle()

    def start_battle(self):
        winner = None
        battle_log = ""

        #self.temp_label.config(text="")

        while self.fighter1.health > 0 and self.fighter2.health > 0:
            ran_num = random.choice([1, 2])
            if ran_num == 1:
                self.fighter1.attack(self.fighter2)
                battle_log += (f"{self.fighter1.name} нанес удар бойцу {self.fighter2.name}!\n"
                               f"{self.fighter2.name} имеет {self.fighter2.health} HP \n\n")
            else:
                self.fighter2.attack(self.fighter1)
                battle_log += (f"{self.fighter2.name} нанес удар бойцу {self.fighter1.name}!\n"
                               f"{self.fighter1.name} имеет {self.fighter1.health} HP\n\n")

            self.temp_label.config(text=battle_log)
            self.root.update()
            self.root.update_idletasks()

        if self.fighter1.health > 0:
            winner = self.fighter1
        else:
            winner = self.fighter2

        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(fightclass.Fight.BD_update(self.fighter1, self.fighter2))

        battle_log += f"Победил {winner.name}!"
        self.temp_label.config(text=battle_log)
        self.back_button.config(state=tk.NORMAL)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.BD_update(winner))

    async def BD_update(self, winner):
        try:
            connection = sqlite3.connect('Fighter.db')
            cur = connection.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS tHistory(name_of_win, hp_of_win)")

            if winner == self.fighter1:
                win_info = (self.fighter1.name, self.fighter1.health)
            else:
                win_info = (self.fighter2.name, self.fighter2.health)

            cur.execute('INSERT INTO tHistory(name_of_win, hp_of_win) VALUES (?, ?)', win_info)

            connection.commit()
            connection.close()

        except sqlite3.Error:
            print('Не удалось сохранить данные матча \n')

    def back_to_main_menu(self):
        clear_window(self.root)
        InterFace(self.root)


class MatchHistoryWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("История матчей")

        self.text_area = tk.Text(self.root, width=55, height=20)
        self.text_area.pack()

        self.back_button = tk.Button(self.root, text="Назад", command=self.back_to_main_menu)
        self.back_button.pack()

        self.show_match_history()

    def show_match_history(self):
        try:
            connection = sqlite3.connect('Fighter.db')
            cur = connection.cursor()
            print("База данных создана и подключена к SQLite")
            cur.execute("CREATE TABLE IF NOT EXISTS tHistory(name_of_win, hp_of_win)")

            self.text_area.insert(tk.END, "История прошлых матчей:\n")
            res = cur.execute('SELECT * FROM tHistory')
            for row in res.fetchall():
                self.text_area.insert(tk.END, f"Победил боец {row[0]}, оставшееся здоровье - {row[1]}\n")

            self.text_area.config(state=tk.DISABLED)

            connection.commit()
            connection.close()

        except sqlite3.Error:
            self.text_area.insert(tk.END, "Просмотреть историю матчей в данный момент невозможно")

    def back_to_main_menu(self):
        clear_window(self.root)
        InterFace(self.root)


class InterFace:
    def __init__(self, root):
        self.root = root
        self.root.title('Добро пожаловать в "Бойцовский клуб"')
        self.root.geometry("500x600+600+300")
        commands = ['Начать матч', 'Провести быстрые бои между ботами', 'Посмотреть историю матчей', 'Выйти']

        for i in range(len(commands)):
            button = tk.Button(self.root, text=f'{commands[i]}',
                               command=lambda option=i + 1: self.handle_button_click(option))
            button.pack()

    def handle_button_click(self, option):
        if option == 1:
            self.open_fighter_selection_window()
        elif option == 2:
            self.create_threads()
        elif option == 3:
            self.show_match_history()
        elif option == 4:
            self.root.destroy()

    def open_fighter_selection_window(self):
        clear_window(self.root)
        FighterSelectionWindow(self.root)

    def create_threads(self):
        for i in range(2):
            print(f'Бой номер {i + 1}')
            name = 'Thread'
            my_thread = Console_GUI.MyThread(name, i)
            my_thread.start()
            my_thread.join()

    def show_match_history(self):
        clear_window(self.root)
        MatchHistoryWindow(self.root)
        # try:
        #     connection = sqlite3.connect('Fighter.db')
        #     cur = connection.cursor()
        #     print("База данных создана и подключена к SQLite")
        #     cur.execute("CREATE TABLE IF NOT EXISTS tHistory(name_of_win, hp_of_win)")
        #
        #     print('Прошлые матчи:')
        #     res = cur.execute('SELECT * FROM tHistory')
        #     print(res.fetchall(), '\n')
        #
        #     connection.commit()
        #     connection.close()
        #
        # except sqlite3.Error:
        #     print('Просмотреть историю матчей в данный момент невозможно')


root = tk.Tk()
app = InterFace(root)
root.mainloop()