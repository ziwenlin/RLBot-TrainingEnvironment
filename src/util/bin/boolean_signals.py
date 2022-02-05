from typing import Union


class BoolEdge:
    edge: bool = False
    value: bool = False

    def __init__(self, side=True):
        self.side = side

    def output(self, input):
        if self.side:
            return self.__eq__(input)
        return self.__ne__(input)

    def __bool__(self):
        return self.value

    def __eq__(self, other):
        if self.edge != other:
            self.edge = other
            if self.edge:
                self.value = not self.value
        return self.value

    def __ne__(self, other):
        if self.edge != other:
            self.edge = other
            if not self.edge:
                self.value = not self.value
        return self.value


if __name__ == '__main__':
    test = BoolEdge()
    print(test == True, True)
    print(test == False, False)
    print(test == True, True)
    print(test == False, False)
    print(test == True, True)
    print()
    test = BoolEdge()
    print(True == test, True)
    print(False == test, False)
    print(True == test, True)
    print(False == test, False)
    print(True == test, True)
