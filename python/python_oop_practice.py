"""
============================================================================
PYTHON OBJECT-ORIENTED PROGRAMMING (OOP) — HANDS-ON PRACTICE
============================================================================
Classes, __init__, instance vs class attributes, methods, inheritance,
encapsulation, polymorphism, dunder (magic) methods, @property,
@classmethod / @staticmethod, and dataclasses.

    python3 python_oop_practice.py

Explanation -> runnable example -> EXERCISES (solutions at bottom).
============================================================================
"""


# ============================================================================
# 1. A CLASS, __init__, INSTANCE vs CLASS ATTRIBUTES, METHODS
# ============================================================================
class Dog:
    species = "Canis familiaris"        # CLASS attribute (shared by all dogs)

    def __init__(self, name, age):      # constructor — runs when you create one
        self.name = name                # INSTANCE attributes (per object)
        self.age = age

    def bark(self):                     # instance METHOD (self = the object)
        return f"{self.name} says Woof!"

    def describe(self):
        return f"{self.name} is {self.age} years old ({self.species})"

def demo_class():
    d = Dog("Rex", 3)                   # create an instance
    print(d.bark())
    print(d.describe())
    print("class attr:", Dog.species)
# EXERCISES 1:
#   1a. Write a Circle class with radius; add area() and circumference() methods.
#   1b. Write a BankAccount with balance; add deposit(amount) and withdraw(amount).


# ============================================================================
# 2. ENCAPSULATION — public / _protected / __private, and @property
# ============================================================================
class Account:
    def __init__(self, owner, balance):
        self.owner = owner              # public
        self._type = "savings"          # _protected (convention: "internal")
        self.__balance = balance        # __private (name-mangled)

    @property                           # getter — access like an attribute
    def balance(self):
        return self.__balance

    @balance.setter                     # setter — validate on assignment
    def balance(self, value):
        if value < 0:
            raise ValueError("Balance cannot be negative")
        self.__balance = value

def demo_encapsulation():
    a = Account("Pramod", 100)
    print("balance via property:", a.balance)
    a.balance = 250                     # goes through the setter
    print("updated balance:", a.balance)
    try:
        a.balance = -50                 # triggers validation
    except ValueError as e:
        print("blocked:", e)
# EXERCISES 2:
#   2a. Add a Temperature class with a celsius property whose setter rejects < -273.15.
#   2b. Add a read-only @property `fahrenheit` computed from celsius.


# ============================================================================
# 3. INHERITANCE — a subclass reuses/extends a parent; super().
# ============================================================================
class Animal:
    def __init__(self, name):
        self.name = name
    def speak(self):
        return "..."                    # to be overridden

class Cat(Animal):                      # Cat inherits from Animal
    def speak(self):                    # OVERRIDE the parent method
        return f"{self.name} says Meow"

class Puppy(Dog):                       # inherit from the Dog above
    def __init__(self, name, age, trick):
        super().__init__(name, age)     # call the parent's __init__
        self.trick = trick
    def show_trick(self):
        return f"{self.name} can {self.trick}"

def demo_inheritance():
    print(Cat("Milo").speak())
    p = Puppy("Buddy", 1, "roll over")
    print(p.bark())                     # inherited from Dog
    print(p.show_trick())               # new method
    print("isinstance Animal?", isinstance(Cat("x"), Animal))
# EXERCISES 3:
#   3a. Create a Shape base class and Rectangle/Square subclasses with area().
#   3b. Make Square reuse Rectangle via super() (a square is a rectangle).


# ============================================================================
# 4. POLYMORPHISM — same method name, different behavior per class.
# ============================================================================
class Circle:
    def __init__(self, r): self.r = r
    def area(self): return 3.14159 * self.r ** 2
class Rect:
    def __init__(self, w, h): self.w, self.h = w, h
    def area(self): return self.w * self.h

def demo_polymorphism():
    shapes = [Circle(2), Rect(3, 4), Circle(1)]
    for s in shapes:                    # same .area() call, different math
        print(f"{type(s).__name__} area: {s.area():.2f}")
# EXERCISES 4:
#   4a. Add a Triangle class with area(); include it in the loop above.


# ============================================================================
# 5. DUNDER (MAGIC) METHODS — make objects behave like built-ins.
# ============================================================================
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __repr__(self):                 # official string (for developers)
        return f"Vector({self.x}, {self.y})"
    def __str__(self):                  # friendly string (for print)
        return f"({self.x}, {self.y})"
    def __add__(self, other):           # enables  v1 + v2
        return Vector(self.x + other.x, self.y + other.y)
    def __eq__(self, other):            # enables  v1 == v2
        return self.x == other.x and self.y == other.y
    def __len__(self):                  # enables  len(v)
        return 2

def demo_dunder():
    v1, v2 = Vector(1, 2), Vector(3, 4)
    print("str:", str(v1), "| repr:", repr(v1))
    print("add:", v1 + v2)              # calls __add__
    print("equal:", Vector(1, 2) == v1) # calls __eq__
    print("len:", len(v1))              # calls __len__
# EXERCISES 5:
#   5a. Add __mul__ to Vector so v * 3 scales it -> Vector(x*3, y*3).
#   5b. Add __getitem__ so v[0] returns x and v[1] returns y.


# ============================================================================
# 6. @classmethod AND @staticmethod
# ============================================================================
class Employee:
    company = "TKE"
    def __init__(self, name):
        self.name = name

    @classmethod                        # gets the CLASS (cls), not an instance
    def from_string(cls, csv):          # alternative constructor
        return cls(csv.split(",")[0])

    @staticmethod                       # no self/cls — just a utility grouped here
    def is_valid_name(name):
        return name.isalpha()

def demo_class_static():
    e = Employee.from_string("Pramod,Engineer")
    print("classmethod built:", e.name, "| company:", Employee.company)
    print("staticmethod:", Employee.is_valid_name("Pramod"), Employee.is_valid_name("P4"))
# EXERCISES 6:
#   6a. Add a @classmethod count-tracker: increment a class var each time __init__ runs.
#   6b. Add a @staticmethod that validates an email contains "@".


# ============================================================================
# 7. DATACLASSES — auto __init__/__repr__/__eq__ (3.7+).
# ============================================================================
from dataclasses import dataclass, field
@dataclass
class Product:
    name: str
    price: float
    tags: list = field(default_factory=list)   # safe mutable default
    def with_tax(self, rate=0.08):
        return round(self.price * (1 + rate), 2)

def demo_dataclass():
    p = Product("Laptop", 1000, ["electronics"])
    print("dataclass:", p)                     # auto __repr__
    print("with tax:", p.with_tax())
    print("equal:", Product("A", 1) == Product("A", 1))   # auto __eq__
# EXERCISES 7:
#   7a. Make a @dataclass Point(x, y) and add a distance_to(other) method.


if __name__ == "__main__":
    for title, fn in [
        ("1 Class basics", demo_class),
        ("2 Encapsulation/property", demo_encapsulation),
        ("3 Inheritance", demo_inheritance),
        ("4 Polymorphism", demo_polymorphism),
        ("5 Dunder methods", demo_dunder),
        ("6 class/static methods", demo_class_static),
        ("7 Dataclasses", demo_dataclass),
    ]:
        print(f"\n=== {title} ===")
        fn()


# ===========================================================================
# ============================  S O L U T I O N S  ==========================
# ===========================================================================
# 1a: class Circle:
#         def __init__(self, radius): self.radius = radius
#         def area(self): return 3.14159 * self.radius ** 2
#         def circumference(self): return 2 * 3.14159 * self.radius
# 1b: class BankAccount:
#         def __init__(self, balance=0): self.balance = balance
#         def deposit(self, amt): self.balance += amt
#         def withdraw(self, amt):
#             if amt > self.balance: raise ValueError("Insufficient funds")
#             self.balance -= amt
#
# 2a/2b: class Temperature:
#         def __init__(self, c): self.celsius = c
#         @property
#         def celsius(self): return self._c
#         @celsius.setter
#         def celsius(self, v):
#             if v < -273.15: raise ValueError("below absolute zero")
#             self._c = v
#         @property
#         def fahrenheit(self): return self._c * 9/5 + 32
#
# 3a/3b: class Shape:
#         def area(self): return 0
#      class Rectangle(Shape):
#         def __init__(self, w, h): self.w, self.h = w, h
#         def area(self): return self.w * self.h
#      class Square(Rectangle):
#         def __init__(self, side): super().__init__(side, side)
#
# 4a: class Triangle:
#         def __init__(self, b, h): self.b, self.h = b, h
#         def area(self): return 0.5 * self.b * self.h
#
# 5a: def __mul__(self, k): return Vector(self.x*k, self.y*k)
# 5b: def __getitem__(self, i): return (self.x, self.y)[i]
#
# 6a: class Employee:
#         count = 0
#         def __init__(self, name):
#             self.name = name
#             Employee.count += 1
# 6b: @staticmethod
#     def is_valid_email(email): return "@" in email
#
# 7a: @dataclass
#     class Point:
#         x: float
#         y: float
#         def distance_to(self, other):
#             return ((self.x-other.x)**2 + (self.y-other.y)**2) ** 0.5
# ===========================================================================
