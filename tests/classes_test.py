import pytest


class InsufficientFunds(Exception):
    pass


class BankAccount():
    def __init__(self, starting_balance=0):
        self.balance = starting_balance

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFunds("Insufficient funds in account")

        self.balance -= amount

    def collect_interest(self):
        self.balance *= 1.1


@pytest.fixture
def zero_bank_account():
    return BankAccount()


@pytest.fixture
def regular_bank_account():
    return BankAccount(50)


def test_bank_set_initial_amount(regular_bank_account):
    assert regular_bank_account.balance == 50


def test_bank_set_default_amount(zero_bank_account):
    assert zero_bank_account.balance == 0


def test_withdraw(regular_bank_account):
    regular_bank_account.withdraw(20)
    assert regular_bank_account.balance == 30


def test_deposit(regular_bank_account):
    regular_bank_account.deposit(20)
    assert regular_bank_account.balance == 70


def test_collect_interest(regular_bank_account):
    regular_bank_account.collect_interest()
    assert round(regular_bank_account.balance, 6) == 55


@pytest.mark.parametrize("deposited, withdrew, expected", [
    (200, 100, 100),
    (50, 15, 35),
    (1000, 900, 100)
])
def test_bank_transaction(zero_bank_account, deposited, withdrew, expected):
    zero_bank_account.deposit(deposited)
    zero_bank_account.withdraw(withdrew)
    assert zero_bank_account.balance == expected


def test_insufficient_funds(zero_bank_account):
    with pytest.raises(InsufficientFunds):
        zero_bank_account.withdraw(200)
