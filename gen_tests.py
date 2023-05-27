from __future__ import annotations
import typing
import pathlib
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
    """
    Simply provides random inputs.
    
    No thoughts, head empty.
    """
    
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


class ImprovisedInputGenerator(DumbInputGenerator):
    """
    Tries to add a lot of edges first, hoping that
    then the queries are likely to succeed.
    """
    
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


class SmartInputGenerator(DumbInputGenerator):
    """
    Maintains a DSU and more often than not generates
    queries with non-trivial answers.
    
    To do so without maintating a complete solution,
    it uses a trick that after a trivial (-1) answer,
    the obfuscation is neutralized, so we can choose
    the nodes for the next request freely.
    
    Essentially, this generator yields either edge-addition
    requests, or pairs of a query with a non-trivial answer
    and a query with a trivial answer.
    """
    
    RETRIES: typing.Final[int] = 2000
    
    dsu: np.ndarray
    failures: int

    def __init__(self, n: int, q: int):
        super().__init__(n, q)
        
        self.dsu = np.arange(n, dtype=np.int32)
        self.failures = 0
    
    def generate(self) -> InputGenerator:
        while len(self.data) < self.q + 1:
            self.add_line(list(map(str, self.pick_generator()())))
        
        self.data = self.data[:self.q + 1]
        
        print(f"Failed {self.failures} times out of {self.q} requests")
        
        return self

    def dsu_root(self, node: int) -> int:
        if self.dsu[node] == node:
            return node
        
        root: int = self.dsu_root(self.dsu[node])
        self.dsu[node] = root
        return root
    
    def gen_add(self) -> typing.Sequence[typing.Any]:
        for _ in range(self.RETRIES):
            op, i, j, cost = super().gen_add()
            
            if self.dsu_root(i - 1) != self.dsu_root(j - 1):
                self.dsu[self.dsu_root(i - 1)] = self.dsu_root(j - 1)
                
                return (op, i, j, cost)
        
        raise RuntimeError("Failed to generate a valid edge-addition request")

    def _gen_good_eval(self) -> typing.Sequence[typing.Any]:
        for _ in range(self.RETRIES):
            op, i, j = super().gen_eval()
            
            if self.dsu_root(i - 1) == self.dsu_root(j - 1):
                return (op, i, j)
        
        raise RuntimeError("Failed to generate a good evaluation request")
    
    def gen_eval_pair(self) -> typing.Sequence[typing.Any]:
        try:
            self.add_line(list(map(str, self._gen_good_eval())))
        except RuntimeError:
            # print("Scheme failed, falling back to dumb generation")
            self.failures += 1
        
        # Note: in case of success, we just hope this won't randomly strike
        #       a non-trivial query, since that would mess us up a bit...
        return self.gen_eval()
    
    def pick_generator(self) -> typing.Callable[[], typing.Sequence[typing.Any]]:
        return np.random.choice(
            [self.gen_add, self.gen_eval, self.gen_eval_pair],
            p=[0.4, 0.2, 0.4],
        )


big_inputs: pathlib.Path = pathlib.Path(__file__).parent / "big_input.txt"
small_inputs: pathlib.Path = pathlib.Path(__file__).parent / "small_input.txt"

gen_cls: typing.Type[InputGenerator] = SmartInputGenerator
# generate(gen_cls, small_inputs, 2000, 2000)
generate(gen_cls, big_inputs, 160000, 200000)
