import pytest


def subtract(num1: int, num2: int):
    return num1 - num2


def add(num1: int, num2: int):
    return num1 + num2


def divide(num1: int, num2: int):
    return num1/num2


def multiply(num1: int, num2: int):
    return num1*num2


def test_initial():
    assert 2 == 2


@pytest.mark.parametrize("num1, num2, expected", [
    (3, 2, 5),
    (0, -1, -1),
    (4, 6, 10)
])
def test_add(num1, num2, expected):
    assert add(num1, num2) == expected
