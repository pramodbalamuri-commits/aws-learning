"""
============================================================================
PYTHON BUILT-IN FUNCTIONS — REFERENCE + RUNNABLE EXAMPLES
============================================================================
Python's built-ins grouped by PURPOSE. Run it to see every example print.

    python3 python_builtins_reference.py

Each group has a demo function. Skim, run, then try the EXERCISES at the end.
============================================================================
"""


# ---------------------------------------------------------------------------
# GROUP 1 — Numbers & math
# ---------------------------------------------------------------------------
def g1_numbers():
    print("abs(-5):", abs(-5))               # absolute value -> 5
    print("round(3.14159,2):", round(3.14159, 2))
    print("pow(2,10):", pow(2, 10))          # 2**10 -> 1024
    print("divmod(17,5):", divmod(17, 5))    # (quotient, remainder) -> (3,2)
    print("min/max:", min(4, 2, 9), max(4, 2, 9))
    print("sum:", sum([1, 2, 3], 100))       # start value 100 -> 106
    print("int/float/complex:", int(3.9), float("2.5"), complex(2, 3))


# ---------------------------------------------------------------------------
# GROUP 2 — Type conversion & inspection
# ---------------------------------------------------------------------------
def g2_types():
    print("type:", type([]))                 # <class 'list'>
    print("isinstance:", isinstance(5, int)) # True
    print("str/int/float/bool:", str(10), int("42"), float("3.5"), bool(0))
    print("list/tuple/set/dict:",
          list("abc"), tuple([1, 2]), set([1, 1, 2]), dict(a=1, b=2))
    print("bin/oct/hex:", bin(10), oct(10), hex(255))
    print("ord/chr:", ord("A"), chr(97))     # char<->code: 65, 'a'
    print("id (memory):", type(id(5)))       # unique object id


# ---------------------------------------------------------------------------
# GROUP 3 — Iterables & sequences (the workhorses)
# ---------------------------------------------------------------------------
def g3_iterables():
    print("len:", len("hello"))
    print("range:", list(range(2, 11, 2)))   # start,stop,step -> [2,4,6,8,10]
    print("enumerate:", list(enumerate(["a", "b"], start=1)))
    print("zip:", list(zip([1, 2, 3], ["a", "b", "c"])))
    print("sorted:", sorted([3, 1, 2], reverse=True))
    print("reversed:", list(reversed([1, 2, 3])))
    print("map:", list(map(str.upper, ["a", "b"])))
    print("filter:", list(filter(lambda x: x > 2, [1, 2, 3, 4])))
    print("any/all:", any([0, 0, 1]), all([1, 2, 3]))
    print("next/iter:", next(iter([10, 20, 30])))   # first item via iterator


# ---------------------------------------------------------------------------
# GROUP 4 — Strings & output
# ---------------------------------------------------------------------------
def g4_strings():
    print("format:", "{:.2f}".format(3.14159))     # '3.14'
    print("f-string:", f"{7:03d}")                  # '007'
    print("repr vs str:", repr("hi\n"), str("hi\n").strip())
    print("ascii:", ascii("café"))                  # escapes non-ascii
    # print() options: sep and end
    print("a", "b", "c", sep="-", end=" <end>\n")


# ---------------------------------------------------------------------------
# GROUP 5 — Objects, attributes, introspection
# ---------------------------------------------------------------------------
class Sample:
    x = 10
    def hello(self):
        return "hi"
def g5_objects():
    s = Sample()
    print("hasattr:", hasattr(s, "x"))
    print("getattr:", getattr(s, "x"))
    setattr(s, "y", 99); print("after setattr y:", s.y)
    print("dir (first 3 attrs):", [a for a in dir(s) if not a.startswith("_")])
    print("callable:", callable(s.hello), callable(s.x))
    print("vars:", vars(s))                  # instance __dict__
    print("isinstance/issubclass:", issubclass(bool, int))


# ---------------------------------------------------------------------------
# GROUP 6 — Functional helpers
# ---------------------------------------------------------------------------
from functools import reduce
def g6_functional():
    print("reduce:", reduce(lambda a, b: a + b, [1, 2, 3, 4]))   # 10
    print("map+filter:", list(map(lambda x: x*x, filter(lambda x: x % 2, range(6)))))
    print("sorted by key:", sorted(["bb", "a", "ccc"], key=len))
    print("min by key:", min([("a", 3), ("b", 1)], key=lambda t: t[1]))


# ---------------------------------------------------------------------------
# GROUP 7 — Aggregation & logic
# ---------------------------------------------------------------------------
def g7_aggregate():
    nums = [5, 3, 8, 1]
    print("sum/min/max:", sum(nums), min(nums), max(nums))
    print("all positive:", all(n > 0 for n in nums))
    print("any even:", any(n % 2 == 0 for n in nums))
    print("sorted:", sorted(nums))


# ---------------------------------------------------------------------------
# GROUP 8 — Handy others you'll actually use
# ---------------------------------------------------------------------------
def g8_others():
    print("input(): (skipped — needs typing)  # value = input('Name: ')")
    print("format numbers:", format(1234567, ","))   # '1,234,567'
    print("enumerate for indexing:")
    for i, letter in enumerate("hi"):
        print("   ", i, letter)
    print("zip to build dict:", dict(zip(["a", "b"], [1, 2])))


# ---------------------------------------------------------------------------
# QUICK-REFERENCE TABLE (comment) — the ~70 built-ins by category
# ---------------------------------------------------------------------------
# Numbers/math : abs round pow divmod min max sum int float complex bool
# Convert/type : str list tuple set dict frozenset bytes bytearray
#                bin oct hex ord chr ascii format repr
# Iterables    : len range enumerate zip map filter sorted reversed
#                iter next all any slice
# Objects      : type isinstance issubclass hasattr getattr setattr delattr
#                dir vars id callable object super property staticmethod classmethod
# I/O          : print input open
# Introspect   : help globals locals eval exec compile __import__
# Functional   : (functools) reduce ; plus map/filter/sorted with key=
# Misc         : hash memoryview repr breakpoint


if __name__ == "__main__":
    for title, fn in [
        ("1 Numbers & math", g1_numbers),
        ("2 Type conversion", g2_types),
        ("3 Iterables", g3_iterables),
        ("4 Strings & output", g4_strings),
        ("5 Objects/introspection", g5_objects),
        ("6 Functional", g6_functional),
        ("7 Aggregation", g7_aggregate),
        ("8 Others", g8_others),
    ]:
        print(f"\n=== {title} ===")
        fn()


# ===========================================================================
# EXERCISES (solutions below)
# ===========================================================================
# E1. Use divmod to convert 137 minutes into (hours, minutes).
# E2. Use zip + dict to build {'a':1,'b':2,'c':3} from two lists.
# E3. Use sorted with key to sort ["apple","Fig","banana"] case-insensitively.
# E4. Use any/all: check if ALL numbers in [2,4,6] are even, and if ANY is > 5.
# E5. Use map to convert ["1","2","3"] into [1,2,3].
# E6. Use format to print 0.25 as a percentage string "25.00%".
#
# --- SOLUTIONS ---
# E1: divmod(137, 60)                      # (2, 17)
# E2: dict(zip(["a","b","c"], [1,2,3]))
# E3: sorted(["apple","Fig","banana"], key=str.lower)
# E4: all(n%2==0 for n in [2,4,6]); any(n>5 for n in [2,4,6])
# E5: list(map(int, ["1","2","3"]))
# E6: "{:.2%}".format(0.25)                # '25.00%'
