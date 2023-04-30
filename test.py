from __future__ import annotations
import typing
import pathlib
import random
import subprocess
import time


def generate(file: pathlib.Path, n: int, q: int) -> None:
    data = [f"{n} {q}"]
    
    for i in range(q):
        op = random.randrange(2) + 1
        if op == 1:
            args = (op, 1 + random.randrange(n), 1 + random.randrange(n), random.randrange(10 ** 9) + 1)
        else:
            args = (op, 1 + random.randrange(n), 1 + random.randrange(n))
        data.append(" ".join(map(str, args)))

    data = "\n".join(data)
    
    with open(file, "w") as f:
        print(data, file=f)

big_inputs: pathlib.Path = pathlib.Path(__file__).parent / "big_input.txt"
small_inputs: pathlib.Path = pathlib.Path(__file__).parent / "small_input.txt"

# generate(big_inputs, 200000, 200000)
# generate(small_inputs, 2000, 2000)


inputs = pathlib.Path(__file__).parent / "input.txt"


def compare() -> bool:
    true_result: str = subprocess.check_output(
        ["./good.exe"],
        stdin=open(inputs, "r", encoding="utf-8"),
        encoding="utf-8",
        timeout=10,  # To catch infinite recursion
    ).split()
    
    my_result: str = subprocess.check_output(
        ["python", "tmp.py"],
        stdin=open(inputs, "r", encoding="utf-8"),
        encoding="utf-8",
    ).split()
    
    if my_result != true_result:
        print("WA")
        print("my_result:", my_result)
        print("true_result:", true_result)
        return False
    
    print("OK")
    return True

compare()


def profile() -> None:
    results: str = subprocess.check_output(
        ["python", "-m", "cProfile", "-s", "cumulative", "tmp.py"],
        # stdin=open(inputs, "r", encoding="utf-8"),
        encoding="utf-8",
    )
    
    print(results)

# profile()
