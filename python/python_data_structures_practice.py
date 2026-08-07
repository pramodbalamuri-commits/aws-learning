"""
============================================================================
PYTHON DATA STRUCTURES — HANDS-ON PRACTICE
============================================================================
Lists, Tuples, Sets, Dictionaries, Comprehensions, and the `collections`
helpers. Explanation -> runnable example -> EXERCISES (solutions at bottom).

    python3 python_data_structures_practice.py
============================================================================
"""


# ============================================================================
# 1. LISTS — ordered, mutable, allow duplicates.  []
# ============================================================================
def demo_lists():
    fruits = ["apple", "banana", "cherry"]
    fruits.append("date")            # add to end
    fruits.insert(1, "kiwi")         # insert at index
    fruits.remove("banana")          # remove by value
    popped = fruits.pop()            # remove & return last
    print("list:", fruits, "| popped:", popped)
    print("slice [1:3]:", fruits[1:3])
    print("sorted:", sorted([3, 1, 2]))
    fruits.sort()                    # sort in place
    print("sorted in place:", fruits)
    print("index/count:", fruits.index("apple"), fruits.count("apple"))
    nums = [1, 2, 3]
    nums.extend([4, 5])              # add multiple
    print("extended:", nums, "| reversed:", nums[::-1])
# EXERCISES 1:
#   1a. Given [5,2,8,1,9], get the 3 largest numbers.
#   1b. Remove duplicates from [1,2,2,3,3,3] while keeping order.
#   1c. Merge [1,2,3] and [4,5,6] into one list, then get its sum.


# ============================================================================
# 2. TUPLES — ordered, IMMUTABLE, allow duplicates.  ()
# ============================================================================
def demo_tuples():
    point = (3, 4)
    x, y = point                     # unpacking
    print("tuple:", point, "| x,y:", x, y)
    print("single-element tuple:", (5,))     # comma is required!
    coords = (1, 2, 3, 2, 1)
    print("count/index:", coords.count(2), coords.index(3))
    # tuples are great as dict keys and for returning multiple values
    def min_max(nums): return (min(nums), max(nums))
    print("returned tuple:", min_max([4, 8, 1]))
# EXERCISES 2:
#   2a. Swap two variables a=1, b=2 using tuple unpacking (no temp variable).
#   2b. Given [(1,"a"),(2,"b"),(3,"c")], extract just the numbers into a list.


# ============================================================================
# 3. SETS — unordered, UNIQUE items, fast membership.  {}  / set()
# ============================================================================
def demo_sets():
    a = {1, 2, 3, 4}
    b = {3, 4, 5, 6}
    print("union:", a | b)                   # {1,2,3,4,5,6}
    print("intersection:", a & b)            # {3,4}
    print("difference:", a - b)              # {1,2}
    print("symmetric diff:", a ^ b)          # {1,2,5,6}
    print("membership (fast):", 3 in a)
    a.add(10); a.discard(1)
    print("after add/discard:", a)
    print("dedupe a list:", set([1, 1, 2, 2, 3]))
# EXERCISES 3:
#   3a. Find the common elements between [1,2,3,4] and [3,4,5,6].
#   3b. Count the number of UNIQUE words in "the cat sat on the mat".
#   3c. Check if {1,2} is a subset of {1,2,3,4}.


# ============================================================================
# 4. DICTIONARIES — key:value pairs, fast lookup by key.  {k: v}
# ============================================================================
def demo_dicts():
    person = {"name": "Pramod", "role": "Engineer", "years": 14}
    print("access:", person["name"], "| get w/ default:", person.get("city", "N/A"))
    person["city"] = "Dallas"                # add / update
    del person["years"]                      # remove a key
    print("keys:", list(person.keys()))
    print("values:", list(person.values()))
    print("items:", list(person.items()))
    for k, v in person.items():
        print("   ", k, "->", v)
    print("in check:", "name" in person)
    # merge two dicts (3.9+)
    print("merged:", {"a": 1} | {"b": 2})
# EXERCISES 4:
#   4a. Count letter frequency in "banana" -> {'b':1,'a':3,'n':2}.
#   4b. Given {"a":1,"b":2,"c":3}, get the key with the MAX value.
#   4c. Invert {"a":1,"b":2} into {1:"a",2:"b"}.


# ============================================================================
# 5. COMPREHENSIONS — concise ways to build lists/sets/dicts.
# ============================================================================
def demo_comprehensions():
    print("list:", [x * x for x in range(1, 6)])                 # squares
    print("with filter:", [x for x in range(10) if x % 2 == 0])  # evens
    print("nested:", [(i, j) for i in range(2) for j in range(2)])
    print("set comp:", {c for c in "banana"})                    # unique chars
    print("dict comp:", {x: x**2 for x in range(1, 4)})          # {1:1,2:4,3:9}
    print("transform:", [w.upper() for w in ["a", "b", "c"]])
    # generator expression (lazy, memory-efficient)
    print("gen sum:", sum(x for x in range(1, 101)))             # 5050
# EXERCISES 5:
#   5a. Build a list of cubes for 1..10 using a comprehension.
#   5b. From ["apple","kiwi","fig","banana"], keep words with len > 3 (comprehension).
#   5c. Build a dict {n: "even"/"odd"} for n in 1..5.


# ============================================================================
# 6. collections — specialized structures worth knowing.
# ============================================================================
from collections import Counter, defaultdict, namedtuple, deque, OrderedDict
def demo_collections():
    print("Counter:", Counter("banana"))              # counts each char
    print("most_common:", Counter("banana").most_common(1))
    dd = defaultdict(list)                              # auto-creates [] for new keys
    dd["fruits"].append("apple")
    print("defaultdict:", dict(dd))
    Point = namedtuple("Point", ["x", "y"])           # lightweight class
    p = Point(3, 4); print("namedtuple:", p, p.x, p.y)
    dq = deque([1, 2, 3]); dq.appendleft(0); dq.append(4)
    print("deque (fast both ends):", dq)
# EXERCISES 6:
#   6a. Use Counter to find the most common word in "a b a c a b".
#   6b. Use defaultdict(int) to count occurrences of items in [1,1,2,3,3,3].


if __name__ == "__main__":
    for title, fn in [
        ("1 Lists", demo_lists),
        ("2 Tuples", demo_tuples),
        ("3 Sets", demo_sets),
        ("4 Dictionaries", demo_dicts),
        ("5 Comprehensions", demo_comprehensions),
        ("6 collections", demo_collections),
    ]:
        print(f"\n=== {title} ===")
        fn()


# ===========================================================================
# ============================  S O L U T I O N S  ==========================
# ===========================================================================
# 1a: sorted([5,2,8,1,9], reverse=True)[:3]          # [9,8,5]
# 1b: list(dict.fromkeys([1,2,2,3,3,3]))             # [1,2,3]  (keeps order)
# 1c: sum([1,2,3] + [4,5,6])                          # 21
#
# 2a: a, b = b, a
# 2b: [n for n, _ in [(1,"a"),(2,"b"),(3,"c")]]      # [1,2,3]
#
# 3a: set([1,2,3,4]) & set([3,4,5,6])                # {3,4}
# 3b: len(set("the cat sat on the mat".split()))     # 5
# 3c: {1,2}.issubset({1,2,3,4})                      # True
#
# 4a: from collections import Counter; Counter("banana")
#     # or:  d={}; [d.__setitem__(c, d.get(c,0)+1) for c in "banana"]
# 4b: max({"a":1,"b":2,"c":3}, key=lambda k: {"a":1,"b":2,"c":3}[k])  # 'c'
#     # cleaner: d={"a":1,"b":2,"c":3}; max(d, key=d.get)
# 4c: {v: k for k, v in {"a":1,"b":2}.items()}
#
# 5a: [n**3 for n in range(1, 11)]
# 5b: [w for w in ["apple","kiwi","fig","banana"] if len(w) > 3]
# 5c: {n: ("even" if n % 2 == 0 else "odd") for n in range(1, 6)}
#
# 6a: Counter("a b a c a b".split()).most_common(1)  # [('a', 3)]
# 6b: dd = defaultdict(int)
#     for x in [1,1,2,3,3,3]: dd[x] += 1
#     dict(dd)                                        # {1:2, 2:1, 3:3}
# ===========================================================================
