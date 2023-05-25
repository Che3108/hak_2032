#!/usr/bin/python3

class Satellite(object):
    """
    Satellite - абстрактный класс для спутников

    HDD_size - объем запоминающего устройства в террабайтах
    Rx_speed - скорость получения данных в гигабит в секунду
    Tx_speed - скорость передачи данных в гигабит в секунду

    методы:
        __receive - наполнение спутника информацией
        __transfer - передача информации со спутника

    """
    def __init__(self, HDD_size, Rx_speed, Tx_speed):
        self.__HDD_size = int(1000000*HDD_size) # размер ЗУ в мегабайтах
        self.__Rx_speed = int(125*Rx_speed) # скорость получения в мегабайт в секунду
        self.__Tx_speed = int(125*Tx_speed) # скорость передачи в мегабайт в секунду
        self.__filled = 0 # объем занятого ЗУ в мегабайтах

    def __receive(self, seconds):
        """
        наполнение спутника информацией
        вход:
            seconds - время работыв секундах
        выход:
            - наполненность ЗУ в процентах
            - оставшеся время до полного заполнения ЗУ в секундах
            - объем занятого ЗУ в мегабайтах
            - остаток свободного места ЗУ в мегабайтах
        """
        self.__filled += self.__Rx_speed * seconds # вычисляем объем заполненной памяти 
        if self.__filled > self.__HDD_size: self.__filled = self.__HDD_size # если объем превышает размер ЗУ, то возвращаем объем ЗУ
        pecent_filled = round(self.__filled / self.__HDD_size, 2) * 100 # вычисляем процент наполненности
        free_space = self.__HDD_size - self.__filled # вычисляем остаток свободного места
        time_fill = int(free_space / self.__Rx_speed) # вычисляем оставшеяся время до наполнения
        return (pecent_filled, time_fill, self.__filled, free_space)

    def __transfer(self, seconds):
        """
        передача информации со спутника
        вход:
            seconds - время работы в секундах
        выход:
            - наполненность ЗУ в процентах
            - оставшеся время до полного опустошения ЗУ в секундах
            - объем занятого ЗУ в мегабайтах
            - остаток свободного места ЗУ в мегабайтах
        """
        self.__filled -= self.__Tx_speed * seconds # вычисляем объем слитой памяти 
        if self.__filled < 0: self.__filled = 0 # если объем меньше нуля, то возвращаем 0
        pecent_filled = round(self.__filled / self.__HDD_size, 2) * 100 # вычисляем процент наполненности
        free_space = self.__HDD_size - self.__filled # вычисляем остаток свободного места
        time_empty = int(self.__filled / self.__Tx_speed) # вычисляем оставшеяся время до полного опустошения
        return (pecent_filled, time_empty, self.__filled, free_space)


class KinoSputnik(Satellite):
    def __init__(self):
        super(KinoSputnik, self).__init__(1, 4, 1)

    def photography(self, seconds):
        return super(KinoSputnik, self)._Satellite__receive(seconds)

    def transmiting(self, seconds):
        return super(KinoSputnik, self)._Satellite__transfer(seconds)

class Zorkij(Satellite):
    def __init__(self):
        super(KinoSputnik, self).__init__(0.5, 4, 0.25)

    def photography(self, seconds):
        return super(KinoSputnik, self)._Satellite__receive(seconds)

    def transmiting(self, seconds):
        return super(KinoSputnik, self)._Satellite__transfer(seconds)

if __name__ == "__main__":
    s_1 = KinoSputnik()
    sec = 1500
    info = s_1.photography(sec)
    print(f'спутник фотографировал {sec} секунд.\n\tпроцент наполнения ЗУ: {info[0]}%\n\tоставшеяся время до полного наполнения ЗУ: {info[1]}\n\tвсего заполнено {info[2]} мегабайт\n\tосталось {info[3]} мегабайт')
    print()
    info = s_1.transmiting(sec)
    print(f'спутник передавал {sec} секунд.\n\tпроцент наполнения ЗУ: {info[0]}%\n\tоставшеяся время до полного опустошения ЗУ: {info[1]}\n\tвсего заполнено {info[2]} мегабайт\n\tосталось {info[3]} мегабайт')
    info = s_1.transmiting(0)
    print(f'спутник передавал {sec} секунд.\n\tпроцент наполнения ЗУ: {info[0]}%\n\tоставшеяся время до полного опустошения ЗУ: {info[1]}\n\tвсего заполнено {info[2]} мегабайт\n\tосталось {info[3]} мегабайт')

