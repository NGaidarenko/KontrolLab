import random
import fightclass
import sqlite3


class BotFight(fightclass.Fight): #наследуется от класса Fight

    def BD_update(self, fighter1, fighter2):
        # Работа с базой данных. После завершения матча будет записывать
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


    #не изменяется
    def take_fighter(self):
        super(BotFight, self).take_fighter()


    def use_pokemon(self, owner, enemy):
        owner.attack(enemy)


    def Battle(self):
        massive = fightclass.Fight.take_fighter(self)
        warrior1 = massive[0]
        warrior2 = massive[1]
        winner = fightclass.RefereeMixin()

        # Бой идет
        while warrior1.health > 0 and warrior2.health > 0:
            ran_num = random.choice([1, 2])
            if ran_num == 1:
                warrior1.attack(warrior2)
            else:
                warrior2.attack(warrior1)

        if warrior1.health <= 0 or warrior2.health <= 0:
            BotFight.BD_update(self, warrior1, warrior2)  # Отличие в этой строке
            return
