from abc import ABC, abstractmethod
import random
import time



def register_scenario(func):
    def wrapper_for_dec(self, damage):
        timing = time.time()
        while True:
            if time.time() - timing > 1.0:
                return func(self, damage)

    return wrapper_for_dec


def check_condition(func):
    def wrapper(*args, **kwargs):
        if isinstance(args[1], Fighter) and (args[0].health < 0 or args[1].health < 0):
            print("Ошибка: здоровье бойцов не может быть отрицательным! \n")
            return None
        else:
            return func(*args, **kwargs)

    return wrapper


class Fighter(ABC):
    def __init__(self, name, health=100):
        self._name = name
        self._health = health

    @property
    def name(self):
        return self._name

    @property
    def health(self):
        return self._health

    @name.setter
    def name(self, value):
        self._name = value

    @health.setter
    def health(self, value):
        self._health = value

    @abstractmethod
    @check_condition
    def attack(self, opponent):
        pass

    @register_scenario
    def take_hit(self, damage):
        self._health -= damage
        if self._health < 0:
            self._health = 0
        print(f"У {self.name}: {self.health} HP.")


class RefereeMixin:
    def announce_winner(self, fighter):
        print(f"Победил {fighter.name}!")


class Boxer(Fighter):
    def attack(self, opponent):
        damage = random.randint(10, 25)
        opponent.take_hit(damage)
        print(f"{self.name} ударил {opponent.name}! \n")


class Judoka(Fighter):
    def attack(self, opponent):
        damage = random.randint(5, 40)
        opponent.take_hit(damage)
        print(f"{self.name} бросил {opponent.name}! \n")


class Karate(Fighter):
    def attack(self, opponent):
        damage = random.randint(10, 20)
        print(f"{self.name} снес {opponent.name}! \n")
        opponent.take_hit(damage)
