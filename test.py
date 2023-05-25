from __future__ import annotations
import typing
import pathlib
import subprocess
import time


# inputs = pathlib.Path(__file__).parent / "input.txt"
inputs = pathlib.Path(__file__).parent / "big_input.txt"
# inputs = pathlib.Path(__file__).parent / "small_input.txt"


def compare() -> bool:
    true_result: str = subprocess.check_output(
        ["./good.exe"],
        stdin=open(inputs, "r", encoding="utf-8"),
        encoding="utf-8",
        timeout=10,  # To catch infinite recursion
    ).split()
    
    my_result: str = subprocess.check_output(
        # ["python", "hack.py"],
        ["python", "solution.bak.py"],
        stdin=open(inputs, "r", encoding="utf-8"),
        encoding="utf-8",
    ).split()

    with open("out.txt", "w") as f:
        print("\n".join(my_result), file=f)
    
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
        ["python", "-m", "cProfile", "-s", "cumulative", "hack.py", "-o", "profile_results.prof"],
        stdin=open(inputs, "r", encoding="utf-8"),
        stdout=subprocess.DEVNULL,
        encoding="utf-8",
    )
    
    print(results)

# profile()
