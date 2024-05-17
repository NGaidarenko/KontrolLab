import tkinter as tk
from tkinter import messagebox, scrolledtext
import random
import sqlite3
import threading
import fighters
import exceptions


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

        back_button = tk.Button(self.root, text="Назад", command=self.back_to_main_menu)
        back_button.grid(row=4, column=1)

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
        first_fighter_name = self.first_fighter_var.get()
        second_fighter_name = self.second_fighter_var.get()

        if first_fighter_name == "Выберите бойца" or second_fighter_name == "Выберите бойца":
            messagebox.showerror("Ошибка", "Пожалуйста, выберите двух разных бойцов.")
        else:
            try:
                first_fighter = self.select_fighter_class(first_fighter_name)
                second_fighter = self.select_fighter_class(second_fighter_name)
                clear_window(self.root)
                self.selected_fighters = [first_fighter, second_fighter]
                MatchWindow(self.root, self.selected_fighters[0], self.selected_fighters[1])
            except exceptions.IncorrectInputExcError:
                messagebox.showerror("Ошибка", "Произошла ошибка при выборе бойцов.")

    def back_to_main_menu(self):
        clear_window(self.root)
        InterFace(self.root)


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

        battle_log += f"Победил {winner.name}!"
        self.temp_label.config(text=battle_log)
        self.back_button.config(state=tk.NORMAL)

        self.BD_update(winner)

    def BD_update(self, winner):
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

        self.text_area = scrolledtext.ScrolledText(self.root,wrap=tk.WORD, width=55, height=20)
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


class BattleWindow:
    def __init__(self, root, thread_id, i):
        self.window = tk.Toplevel(root)
        self.i = i
        self.window.title(f"Бой в потоке {thread_id}")
        self.window.geometry(f"400x320")
        self.text_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, width=50, height=15)
        self.text_area.pack(pady=10)
        self.close_button = tk.Button(self.window, text="Закрыть", command=self.window.destroy)
        self.close_button.pack(pady=10)

    def update_battle_info(self, info):
        self.text_area.insert(tk.END, info + "\n")
        self.text_area.yview(tk.END)


class BotFightThread(threading.Thread):
    def __init__(self, thread_id, battle_window):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.battle_window = battle_window

    def run(self):
        self.battle_window.update_battle_info(f"Запуск боя в потоке {self.thread_id}")
        self.battle()

    def battle(self):
        fighters_1 = ['Боксер-1', 'Дзюдоист-1', 'Каратист-1']
        fighters_2 = ['Боксер-2', 'Дзюдоист-2', 'Каратист-2']

        fighter1 = self.select_fighter_class(random.choice(fighters_1))
        fighter2 = self.select_fighter_class(random.choice(fighters_2))
        while fighter1.health > 0 and fighter2.health > 0:
            ran_num = random.choice([1, 2])
            if ran_num == 1:
                fighter1.attack(fighter2)
                self.battle_window.update_battle_info(
                    f"{fighter1.name} ударил {fighter2.name}! У {fighter2.name}: {fighter2.health} HP")
            else:
                fighter2.attack(fighter1)
                self.battle_window.update_battle_info(
                    f"{fighter2.name} ударил {fighter1.name}! У {fighter1.name}: {fighter1.health} HP")

        if fighter1.health > 0:
            winner = fighter1
        else:
            winner = fighter2
        self.battle_window.update_battle_info(f"Победитель в потоке {self.thread_id}: {winner.name}")

    def select_fighter_class(self, fighter):
        if "Боксер" in fighter:
            return fighters.Boxer(fighter)
        elif "Дзюдоист" in fighter:
            return fighters.Judoka(fighter)
        elif "Каратист" in fighter:
            return fighters.Karate(fighter)
        else:
            raise exceptions.IncorrectInputExcError


class InterFace:
    def __init__(self, root):
        self.root = root
        self.root.title('Добро пожаловать в "Бойцовский клуб"')
        self.root.geometry("500x600+600+300")
        commands = ['Начать матч', 'Провести быстрые бои между ботами', 'Посмотреть историю матчей', 'Выйти']

        for i in range(len(commands)):
            button = tk.Button(self.root, text=f'{commands[i]}',
                               command=lambda option=i + 1: self.handle_button_click(option))
            button.pack(pady=5)

    def handle_button_click(self, option):
        if option == 1:
            clear_window(self.root)
            FighterSelectionWindow(self.root)
        elif option == 2:
            self.create_threads()
        elif option == 3:
            clear_window(self.root)
            MatchHistoryWindow(self.root)
        elif option == 4:
            exit()

    def create_threads(self):
        num_threads = 3
        self.threads = []
        self.battle_windows = []

        for i in range(num_threads):
            battle_window = BattleWindow(self.root, i, i)
            self.battle_windows.append(battle_window)
            thread = BotFightThread(i, battle_window)
            self.threads.append(thread)
            thread.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = InterFace(root)
    root.mainloop()
