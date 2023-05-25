from __future__ import annotations
import typing
import pathlib
import subprocess
import time
import abc

import numpy as np


class InputGenerator(abc.ABC):
    n: int
    q: int
    data: list[str]

    def __init__(self, n: int, q: int):
        self.n = n
        self.q = q
        self.data = [f"{n} {q}"]

    def write(self, file: pathlib.Path) -> InputGenerator:
        data = "\n".join(self.data)
    
        with open(file, "w") as f:
            print(data, file=f)
        
        return self
    
    @abc.abstractmethod
    def generate(self) -> InputGenerator:
        return self


def generate(gen: typing.Type[InputGenerator], file: pathlib.Path, *args, **kwargs) -> None:
    gen(*args, **kwargs).generate().write(file)


class DumbInputGenerator(InputGenerator):
    def generate(self) -> InputGenerator:
        for _ in range(self.q):
            self.add_line(list(map(str, self.pick_generator()())))
        
        return self
    
    def add_line(self, args: typing.Sequence[str]) -> None:
        self.data.append(" ".join(args))
    
    def gen_add(self) -> typing.Sequence[typing.Any]:
        n: int = self.n

        i: int = 1 + np.random.randint(n)
        j: int = 1 + np.random.randint(n)
        cost: int = 1 + np.random.randint(10 ** 9)

        return (1, i, j, cost)

    def gen_eval(self) -> typing.Sequence[typing.Any]:
        n: int = self.n

        i: int = 1 + np.random.randint(n)
        j: int = 1 + np.random.randint(n)

        return (2, i, j)

    def pick_generator(self) -> typing.Callable[[], typing.Sequence[typing.Any]]:
        return np.random.choice(
            [self.gen_add, self.gen_eval],
        )


class SmartInputGenerator(DumbInputGenerator):
    # TODO: Embed a complete solution in order to properly transform indices

    def __init__(self, n: int, q: int):
        super().__init__(n, q)

        # TODO: Init solution vars
    
    def add_line(self, args: typing.Sequence[str]) -> None:
        # TODO: update the solution's internal state

        super().add_line(args)

    def gen_good_eval(self) -> typing.Sequence[typing.Any]:
        # TODO: consult the solution's internal state

        raise NotImplementedError()
    
    def pick_generator(self) -> typing.Callable[[], typing.Sequence[typing.Any]]:
        return np.random.choice(
            [self.gen_add, self.gen_eval, self.gen_good_eval],
            p=[0.3, 0.2, 0.5],
        )


class ImprovisedInputGenerator(DumbInputGenerator):
    def generate(self) -> InputGenerator:
        q: int = self.q

        first_inserts: int = np.random.randint(int(
            min(q * 0.5, self.n ** 1.2 * 0.5)
        ))
        q -= first_inserts

        for _ in range(first_inserts):
            self.add_line(list(map(str, self.gen_add())))

        for _ in range(q):
            self.add_line(list(map(str, self.pick_generator()())))
        
        return self
    
    def pick_generator(self) -> typing.Callable[[], typing.Sequence[typing.Any]]:
        return np.random.choice(
            [self.gen_add, self.gen_eval],
            p=[0.3, 0.7],
        )


big_inputs: pathlib.Path = pathlib.Path(__file__).parent / "big_input.txt"
small_inputs: pathlib.Path = pathlib.Path(__file__).parent / "small_input.txt"

gen_cls: typing.Type[InputGenerator] = ImprovisedInputGenerator
# generate(gen_cls, small_inputs, 2000, 2000)
generate(gen_cls, big_inputs, 160000, 200000)
