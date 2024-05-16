import random
import fighters
import asyncio
import sqlite3
import exceptions
import fighters



class RefereeMixin:
    def announce_winner(self, fighter):
        print(f"Победил {fighter.name}! \n")


class Fight:
    def take_fighter(self):
        list_of_fighters = ['Боксер', 'Дзюоист', 'Каратист']

        while True:
            print('Выберите бойца:')
            for i in range(len(list_of_fighters)):
                print(f'{i + 1}): {list_of_fighters[i]}')
            first_pick = (input())

            try:
                if first_pick == '1':
                    fighter_1 = fighters.Boxer("Боксер-1")
                    break
                elif first_pick == "2":
                    fighter_1 = fighters.Judoka("Дзюдоист-1")
                    break
                elif first_pick == '3':
                    fighter_1 = fighters.Karate("Каратист-1")
                    break
                else:
                    raise exceptions.IncorrectInputExcError("Значение введено некорректно")
            except exceptions.IncorrectInputExcError:
                print('Неправильный ввод')

        while True:
            print('Выберите второго бойца')
            for i in range(len(list_of_fighters)):
                print(f'{i + 1}): {list_of_fighters[i]}')
            second_pick = input()

            try:
                if second_pick == '1':
                    fighter_2 = fighters.Boxer("Боксер-2")
                    break
                elif second_pick == '2':
                    fighter_2 = fighters.Judoka("Дзюдоист-2")
                    break
                elif second_pick == '3':
                    fighter_2 = fighters.Karate("Каратист")
                    break
                else:
                    raise exceptions.IncorrectInputExcError
            except exceptions.IncorrectInputExcError:
                print('Неправильный ввод')

        return [fighter_1,
                fighter_2]  # возвращает массив из двух выбранных покемонов (они могут быть и одинаковыми - это нормально)

    async def BD_update(self, fighter1, fighter2):
        try:
            connection = sqlite3.connect('Fighter.db')

            cur = connection.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS tHistory(name_of_win, hp_of_win)")
            if fighter1.health <= 0:  # У первого бойца закончилось hp
                print(f"Боец {fighter1.name} проиграл \n")
                name = fighter2.name
                hp = fighter2.health
                win = (name, hp)
                cur.execute('INSERT INTO tHistory(name_of_win, hp_of_win) VALUES (?, ?)', win)

            if fighter2.health <= 0:  # у второго бойца закончилось hp
                print(f"Боец {fighter2.name} проиграл \n")
                name = fighter1.name
                hp = fighter1.health
                win = (name, hp)
                cur.execute('INSERT INTO tHistory(name_of_win, hp_of_win) VALUES (?, ?)', win)

            if (connection):
                connection.commit()
                connection.close()

        except sqlite3.Error:
            print('Не удалось сохранить данные матча \n')

    def Battle(self):
        massive = Fight.take_fighter(self)
        warrior1 = massive[0]
        warrior2 = massive[1]
        winner = RefereeMixin()

        # Бой идет
        while warrior1.health > 0 and warrior2.health > 0:
            ran_num = random.choice([1, 2])
            if ran_num == 1:
                warrior1.attack(warrior2)
            else:
                warrior2.attack(warrior1)

        if warrior1.health > 0:
            winner.announce_winner(warrior1)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(Fight.BD_update(self, warrior1, warrior2))
        else:
            winner.announce_winner(warrior2)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(Fight.BD_update(self, warrior1, warrior2))
