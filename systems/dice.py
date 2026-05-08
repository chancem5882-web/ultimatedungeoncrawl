import random


def d20():
    return random.randint(1, 20)


def roll(number, sides):

    total = 0

    for i in range(number):
        total += random.randint(1, sides)

    return total
