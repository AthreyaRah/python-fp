"""Classes & OOP from first principles - the practice snippet.

Run it:  python code/foundations/19_classes_and_oop/demo.py

Mental model:
- A class is an object that acts as (a) a factory for instances and (b) a
  namespace holding methods and class attributes.
- Each instance has its own `__dict__` for instance attributes. Attribute lookup
  checks the instance first, then the class (and its bases).
- `self` is explicit and ordinary: `obj.method(x)` is exactly
  `type(obj).method(obj, x)`.
- `__new__` CREATES the instance; `__init__` INITIALISES the already-created one
  (and must return None).
- @classmethod gets the class as `cls`; @staticmethod gets nothing special;
  @property makes a method look like an attribute.
"""

from __future__ import annotations


class Account:
    open_count = 0  # class attribute: one object, shared by the class

    def __init__(self, owner: str, balance: int = 0) -> None:
        self.owner = owner          # instance attributes: per object
        self._balance = balance
        Account.open_count += 1     # rebind on the CLASS, deliberately

    def deposit(self, amount: int) -> None:
        self._balance += amount

    @property
    def balance(self) -> int:       # read like an attribute: account.balance
        return self._balance

    @balance.setter
    def balance(self, value: int) -> None:
        if value < 0:
            raise ValueError("balance cannot be negative")
        self._balance = value

    @classmethod
    def from_record(cls, record: str) -> Account:   # alternative constructor
        owner, amount = record.split(":")
        return cls(owner.strip(), int(amount))

    @staticmethod
    def is_valid_owner(name: str) -> bool:
        return name.isalpha() and len(name) >= 2

    def __repr__(self) -> str:
        return f"Account(owner={self.owner!r}, balance={self._balance})"


def instance_vs_class_dict() -> None:
    a = Account("Ada", 100)
    print("instance __dict__:", a.__dict__)
    print("'deposit' in instance dict?", "deposit" in a.__dict__,
          "| in class dict?", "deposit" in Account.__dict__)


def method_call_is_sugar() -> None:
    a = Account("Bo", 50)
    a.deposit(25)
    Account.deposit(a, 25)              # exactly the same call
    print("after two deposits of 25:", a.balance)


def alternative_constructor() -> None:
    a = Account.from_record("Cy: 300")
    print("from_record:", a)


def property_validation() -> None:
    a = Account("Di", 10)
    a.balance = 999
    print("set balance to 999 ->", a.balance)
    try:
        a.balance = -5
    except ValueError as exc:
        print("set balance to -5 ->", exc)


def main() -> None:
    instance_vs_class_dict()
    print()
    method_call_is_sugar()
    print()
    alternative_constructor()
    print()
    property_validation()
    print()
    print("Account.open_count =", Account.open_count)
    print("is_valid_owner('Ada'):", Account.is_valid_owner("Ada"))


if __name__ == "__main__":
    main()
