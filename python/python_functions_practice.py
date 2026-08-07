"""
============================================================================
PYTHON FUNCTIONS — HANDS-ON PRACTICE (Beginner → Advanced)
============================================================================
Covers EVERY type of function and function concept in Python:

  1. Built-in functions            9. Scope (local/global/nonlocal)
  2. User-defined functions (def) 10. Closures
  3. Parameters & arguments       11. Decorators
  4. Default & keyword args        12. Generators (yield)
  5. *args and **kwargs            13. Nested functions
  6. Return values (incl. multi)   14. Type hints & docstrings
  7. Lambda (anonymous)            15. Recursion
  8. Higher-order: map/filter/reduce  + a bank of PRACTICE PROGRAMS

HOW TO USE
----------
Run it:            python3 python_functions_practice.py
Practice:          each section has an example that runs, then EXERCISES.
                   Try each exercise yourself first; solutions are at the bottom
                   (search "SOLUTIONS"). Uncomment the demo() calls to see output.
============================================================================
"""


# ============================================================================
# 1. BUILT-IN FUNCTIONS  — Python ships with ~70 ready-to-use functions.
# ============================================================================
def demo_builtins():
    print("len:", len("hello"))                 # length
    print("type:", type(42))                     # the object's type
    print("abs:", abs(-7))                        # absolute value
    print("round:", round(3.14159, 2))           # round to 2 decimals
    print("min/max:", min(3, 9, 1), max(3, 9, 1))
    print("sum:", sum([1, 2, 3, 4]))
    print("sorted:", sorted([3, 1, 2]))          # returns a new sorted list
    print("range->list:", list(range(1, 6)))     # 1..5
    print("int/str/float:", int("10"), str(10), float("2.5"))
    print("enumerate:", list(enumerate(["a", "b"])))   # [(0,'a'),(1,'b')]
    print("zip:", list(zip([1, 2], ["a", "b"])))       # [(1,'a'),(2,'b')]
    print("any/all:", any([False, True]), all([True, True]))
# EXERCISES 1:
#   1a. Use built-ins to find the largest number in [12, 45, 7, 89, 34].
#   1b. Count how many characters are in "python programming" (excluding spaces).
#   1c. Given "3,7,2,9", turn it into a sorted list of integers -> [2,3,7,9].


# ============================================================================
# 2. USER-DEFINED FUNCTIONS — define your own with `def`.
# ============================================================================
def greet(name):
    """Return a greeting string (this line is a docstring)."""
    return f"Hello, {name}!"
# EXERCISES 2:
#   2a. Write area_of_rectangle(length, width) that returns length*width.
#   2b. Write is_even(n) that returns True/False.


# ============================================================================
# 3. PARAMETERS & ARGUMENTS — positional vs keyword.
# ============================================================================
def describe_pet(animal, name):
    return f"{name} is a {animal}"
def demo_params():
    print(describe_pet("dog", "Rex"))          # positional (order matters)
    print(describe_pet(name="Milo", animal="cat"))  # keyword (order-free)
# EXERCISES 3:
#   3a. Write full_name(first, last) and call it once positionally, once by keyword.


# ============================================================================
# 4. DEFAULT & KEYWORD ARGUMENTS — give parameters fallback values.
# ============================================================================
def power(base, exponent=2):                    # exponent defaults to 2
    return base ** exponent
def demo_default():
    print(power(5))         # 25  (uses default exponent=2)
    print(power(2, 10))     # 1024
# EXERCISES 4:
#   4a. Write greet_user(name, greeting="Hello") -> "Hello, <name>!".
#   4b. GOTCHA: never use a MUTABLE default like def f(x, items=[]).
#       Write append_item(item, items=None) that safely defaults to a new list.


# ============================================================================
# 5. *args AND **kwargs — accept ANY number of args / keyword args.
# ============================================================================
def add_all(*args):                 # args is a tuple
    return sum(args)
def make_profile(**kwargs):         # kwargs is a dict
    return ", ".join(f"{k}={v}" for k, v in kwargs.items())
def demo_varargs():
    print(add_all(1, 2, 3, 4, 5))                   # 15
    print(make_profile(name="Pramod", role="Engineer", years=14))
# EXERCISES 5:
#   5a. Write multiply_all(*nums) returning the product of all numbers.
#   5b. Write build_url(base, **params) -> "base?k1=v1&k2=v2".


# ============================================================================
# 6. RETURN VALUES — return one value, many values, or nothing (None).
# ============================================================================
def min_max(numbers):
    return min(numbers), max(numbers)   # returns a TUPLE of two values
def demo_return():
    lo, hi = min_max([4, 8, 1, 9, 3])   # tuple unpacking
    print("lo:", lo, "hi:", hi)
# EXERCISES 6:
#   6a. Write divide(a, b) returning BOTH quotient and remainder.
#   6b. Write stats(nums) returning (count, total, average).


# ============================================================================
# 7. LAMBDA — small anonymous one-line functions.
# ============================================================================
square = lambda x: x * x
add = lambda a, b: a + b
def demo_lambda():
    print("square(6):", square(6))
    print("add(3,4):", add(3, 4))
    # commonly used inline for sorting keys:
    words = ["banana", "kiwi", "apple"]
    print("by length:", sorted(words, key=lambda w: len(w)))
# EXERCISES 7:
#   7a. Write a lambda `cube` that cubes a number.
#   7b. Sort [("Al",90),("Bo",75),("Cy",88)] by the score (2nd item), high->low.


# ============================================================================
# 8. HIGHER-ORDER FUNCTIONS — functions that take/return functions.
#    map(), filter(), reduce() are the classics.
# ============================================================================
from functools import reduce
def demo_hof():
    nums = [1, 2, 3, 4, 5, 6]
    print("map (double):", list(map(lambda x: x * 2, nums)))
    print("filter (even):", list(filter(lambda x: x % 2 == 0, nums)))
    print("reduce (sum):", reduce(lambda a, b: a + b, nums))
    # a function returning a function:
    def multiplier(n):
        return lambda x: x * n
    triple = multiplier(3)
    print("triple(10):", triple(10))
# EXERCISES 8:
#   8a. Use map to convert [1,2,3,4] into their squares.
#   8b. Use filter to keep only words longer than 3 chars.
#   8c. Use reduce to find the product of [1,2,3,4,5].


# ============================================================================
# 9. SCOPE — local, global, nonlocal (where names live).
# ============================================================================
counter = 0                      # global
def increment():
    global counter               # tell Python to use the global, not a new local
    counter += 1
def demo_scope():
    increment(); increment()
    print("global counter:", counter)   # 2
# EXERCISES 9:
#   9a. Explain (in a comment) what happens if you remove `global counter`.
#   9b. Write a function with a local variable of the same name and print both.


# ============================================================================
# 10. CLOSURES — an inner function that "remembers" the enclosing variables.
# ============================================================================
def make_counter():
    count = 0
    def counter_fn():
        nonlocal count           # modify the enclosing (not global) variable
        count += 1
        return count
    return counter_fn
def demo_closure():
    c = make_counter()
    print("closure:", c(), c(), c())   # 1 2 3  (state remembered)
# EXERCISES 10:
#   10a. Write make_multiplier(n) returning a function that multiplies its input by n.
#   10b. Write make_accumulator() that keeps a running total across calls.


# ============================================================================
# 11. DECORATORS — wrap a function to add behavior (logging, timing, auth).
# ============================================================================
import time
def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time()-start:.6f}s")
        return result
    return wrapper

@timer                                  # same as: slow = timer(slow)
def slow_add(a, b):
    time.sleep(0.05)
    return a + b
def demo_decorator():
    print("decorated result:", slow_add(2, 3))
# EXERCISES 11:
#   11a. Write a @debug decorator that prints the function name + args before calling.
#   11b. Write a @repeat(n) decorator (a decorator WITH an argument) that runs the
#        function n times. (Hint: three nested functions.)


# ============================================================================
# 12. GENERATORS — functions that `yield` values lazily (memory-efficient).
# ============================================================================
def count_up_to(n):
    i = 1
    while i <= n:
        yield i                  # pauses here, resumes on next()
        i += 1
def demo_generator():
    print("generator:", list(count_up_to(5)))      # [1,2,3,4,5]
    gen = (x * x for x in range(1, 6))             # generator EXPRESSION
    print("gen expr:", list(gen))
# EXERCISES 12:
#   12a. Write a generator fibonacci(n) that yields the first n Fibonacci numbers.
#   12b. Write a generator even_numbers(limit) yielding evens up to limit.


# ============================================================================
# 13. NESTED FUNCTIONS — a function defined inside another.
# ============================================================================
def outer(msg):
    def inner():
        return msg.upper()
    return inner()
def demo_nested():
    print("nested:", outer("hello"))   # HELLO
# EXERCISES 13:
#   13a. Write validate_password(pwd) with an inner helper has_digit(s).


# ============================================================================
# 14. TYPE HINTS & DOCSTRINGS — professional, self-documenting functions.
# ============================================================================
def calculate_discount(price: float, percent: float = 10.0) -> float:
    """Return the price after applying a percentage discount.

    Args:
        price: original price.
        percent: discount percent (default 10).
    Returns:
        Discounted price as a float.
    """
    return price - (price * percent / 100)
def demo_typed():
    print("discounted:", calculate_discount(200, 25))   # 150.0
    print("docstring:", calculate_discount.__doc__.splitlines()[0])
# EXERCISES 14:
#   14a. Add type hints to your area_of_rectangle from section 2.


# ============================================================================
# 15. RECURSION — a function that calls itself (base case + recursive case).
# ============================================================================
def factorial(n):
    if n <= 1:                   # base case (stops recursion)
        return 1
    return n * factorial(n - 1)  # recursive case
def demo_recursion():
    print("factorial(5):", factorial(5))    # 120
# EXERCISES 15:
#   15a. Write recursive_sum(nums) that sums a list recursively.
#   15b. Write count_down(n) that prints n, n-1, ... 1 recursively.


# ============================================================================
# PRACTICE PROGRAMS — classic problems to combine everything above.
# Try each; solutions are in the SOLUTIONS block at the bottom.
# ============================================================================
# P1.  is_prime(n)            -> True if n is prime.
# P2.  reverse_string(s)      -> reversed string (try with slicing AND a loop).
# P3.  is_palindrome(s)       -> True if s reads the same both ways.
# P4.  count_vowels(s)        -> number of vowels in s.
# P5.  fizzbuzz(n)            -> print 1..n; "Fizz"/"Buzz"/"FizzBuzz" rules.
# P6.  word_count(sentence)   -> dict of {word: count}.
# P7.  celsius_to_fahrenheit(c) and fahrenheit_to_celsius(f).
# P8.  gcd(a, b)              -> greatest common divisor (recursion friendly).
# P9.  flatten(nested_list)   -> flatten [[1,2],[3,[4]]] -> [1,2,3,4] (recursion).
# P10. second_largest(nums)   -> the 2nd largest unique number.


# ---------------------------------------------------------------------------
# RUN THE DEMOS — uncomment the ones you want to see, then run the file.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Python Functions Practice ===\n")
    demos = [
        ("1  Built-ins", demo_builtins),
        ("3  Parameters", demo_params),
        ("4  Defaults", demo_default),
        ("5  *args/**kwargs", demo_varargs),
        ("6  Return values", demo_return),
        ("7  Lambda", demo_lambda),
        ("8  Higher-order", demo_hof),
        ("9  Scope", demo_scope),
        ("10 Closure", demo_closure),
        ("11 Decorator", demo_decorator),
        ("12 Generator", demo_generator),
        ("13 Nested", demo_nested),
        ("14 Type hints", demo_typed),
        ("15 Recursion", demo_recursion),
    ]
    for title, fn in demos:
        print(f"\n--- {title} ---")
        fn()


# ===========================================================================
# ============================  S O L U T I O N S  ==========================
# ===========================================================================
# Peek only after you've tried! These are ONE correct way; many exist.
#
# 1a: max([12,45,7,89,34])                         # 89
# 1b: len("python programming".replace(" ", ""))   # 17
# 1c: sorted(int(x) for x in "3,7,2,9".split(","))
#
# 2a: def area_of_rectangle(length, width): return length * width
# 2b: def is_even(n): return n % 2 == 0
#
# 3a: def full_name(first, last): return f"{first} {last}"
#     full_name("Pramod", "Balamuri"); full_name(last="B", first="Pramod")
#
# 4a: def greet_user(name, greeting="Hello"): return f"{greeting}, {name}!"
# 4b: def append_item(item, items=None):
#         if items is None: items = []
#         items.append(item); return items
#
# 5a: def multiply_all(*nums):
#         result = 1
#         for n in nums: result *= n
#         return result
# 5b: def build_url(base, **params):
#         query = "&".join(f"{k}={v}" for k, v in params.items())
#         return f"{base}?{query}" if params else base
#
# 6a: def divide(a, b): return a // b, a % b
# 6b: def stats(nums): return len(nums), sum(nums), sum(nums)/len(nums)
#
# 7a: cube = lambda x: x ** 3
# 7b: sorted([("Al",90),("Bo",75),("Cy",88)], key=lambda t: t[1], reverse=True)
#
# 8a: list(map(lambda x: x**2, [1,2,3,4]))
# 8b: list(filter(lambda w: len(w) > 3, words))
# 8c: reduce(lambda a, b: a*b, [1,2,3,4,5])        # 120
#
# 9a: without `global`, `counter += 1` raises UnboundLocalError (Python treats
#     counter as a NEW local because it's assigned inside the function).
#
# 10a: def make_multiplier(n): return lambda x: x * n
# 10b: def make_accumulator():
#          total = 0
#          def add(x):
#              nonlocal total; total += x; return total
#          return add
#
# 11a: def debug(func):
#          def wrapper(*a, **k):
#              print(f"Calling {func.__name__} with {a} {k}")
#              return func(*a, **k)
#          return wrapper
# 11b: def repeat(n):
#          def decorator(func):
#              def wrapper(*a, **k):
#                  for _ in range(n): result = func(*a, **k)
#                  return result
#              return wrapper
#          return decorator
#
# 12a: def fibonacci(n):
#          a, b = 0, 1
#          for _ in range(n):
#              yield a; a, b = b, a + b
# 12b: def even_numbers(limit):
#          for i in range(0, limit + 1, 2): yield i
#
# 13a: def validate_password(pwd):
#          def has_digit(s): return any(c.isdigit() for c in s)
#          return len(pwd) >= 8 and has_digit(pwd)
#
# 14a: def area_of_rectangle(length: float, width: float) -> float:
#          return length * width
#
# 15a: def recursive_sum(nums):
#          return 0 if not nums else nums[0] + recursive_sum(nums[1:])
# 15b: def count_down(n):
#          if n < 1: return
#          print(n); count_down(n - 1)
#
# --- PRACTICE PROGRAMS ---
# P1: def is_prime(n):
#         if n < 2: return False
#         for i in range(2, int(n**0.5) + 1):
#             if n % i == 0: return False
#         return True
# P2: def reverse_string(s): return s[::-1]
# P3: def is_palindrome(s): s=s.lower().replace(" ",""); return s == s[::-1]
# P4: def count_vowels(s): return sum(1 for c in s.lower() if c in "aeiou")
# P5: def fizzbuzz(n):
#         for i in range(1, n+1):
#             print("FizzBuzz" if i%15==0 else "Fizz" if i%3==0 else "Buzz" if i%5==0 else i)
# P6: def word_count(sentence):
#         counts = {}
#         for w in sentence.lower().split(): counts[w] = counts.get(w, 0) + 1
#         return counts
# P7: def celsius_to_fahrenheit(c): return c * 9/5 + 32
#     def fahrenheit_to_celsius(f): return (f - 32) * 5/9
# P8: def gcd(a, b): return a if b == 0 else gcd(b, a % b)
# P9: def flatten(nested):
#         out = []
#         for item in nested:
#             out.extend(flatten(item)) if isinstance(item, list) else out.append(item)
#         return out
# P10: def second_largest(nums):
#         u = sorted(set(nums), reverse=True)
#         return u[1] if len(u) > 1 else None
# ===========================================================================
