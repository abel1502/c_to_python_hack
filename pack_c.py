from __future__ import annotations
import typing
import pathlib
import subprocess
import argparse
import jinja2
import contextlib
import itertools
import re
import shlex
import zlib


parser = argparse.ArgumentParser(
    description="A utility to compile and pack C code into a single Python file",
)

parser.add_argument(
    "c_source",
    type=pathlib.Path,
    help="Path to the C source file",
)

parser.add_argument(
    "-o", "--output",
    type=pathlib.Path,
    help="Path to the output Python file",
)

parser.add_argument(
    "-e", "--entry-point",
    type=str,
    default="solve",
    help="Name of the entry point function, defaults to 'solve'. The signature must be 'void()'",
)

parser.add_argument(
    "--cflags",
    type=str,
    default="",
    help="Additional flags for gcc",
)

parser.add_argument(
    "-c", "--compress",
    action="store_true",
    help="Compress the function code with zlib",
)


env = jinja2.Environment()
env.filters["repr"] = repr
env.filters["hex_4"] = lambda s: f"{s:#x}"
env.filters["zlib_compress"] = zlib.compress


TEMPLATE_PY: typing.Final[jinja2.Template] = env.from_string("""\
from __future__ import annotations
import typing
import sys
import ctypes
import struct
import mmap
{%- if compress %}
import zlib
{%- endif %}


func_code: bytearray = bytearray(
    {% if compress -%}
    zlib.decompress(
        {{ func_code | zlib_compress | repr }}
    )
    {%- else -%}
    {{ func_code | repr }}
    {%- endif %}
)

libc_relocs: dict[str, int] = dict(
    {%- for name, offs in libc_relocs.items() %}
    {{ name }}={{ offs | hex_4 }},
    {%- endfor %}
)

func_offs: int = {{ func_offs | hex_4 }}

libc = ctypes.CDLL("libc.so.6")

for name, offs in libc_relocs.items():
    ctypes_func: ctypes._FuncPointer = getattr(libc, name)
    ctypes_func_addr: int = ctypes.c_void_p.from_address(ctypes.addressof(ctypes_func)).value
    
    func_code[offs:offs + 8] = struct.pack("<Q", ctypes_func_addr)
    # print(f"{name} -> {ctypes_func_addr:#x}")
    del ctypes_func, ctypes_func_addr

assert len(func_code) <= 32 * mmap.PAGESIZE, "Payload too big"

# print(func_code.hex())

func_buf = mmap.mmap(-1, len(func_code), prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC)
func_ptr = ctypes.c_void_p.from_buffer(func_buf, func_offs)
func_type = ctypes.CFUNCTYPE(
    None,
)
func = func_type(ctypes.addressof(func_ptr))
func_buf.write(func_code)

# breakpoint()

# Magic
func()
""")


LINKER_SCRIPT: pathlib.Path = pathlib.Path(__file__).parent / "linker.ld"


def main():
    args = parser.parse_args()
    
    if not args.output:
        args.output = args.c_source.with_suffix(".py")
    
    # assert args.c_source.suffix == ".c", "Only C files are supported"
    
    with contextlib.ExitStack() as stack:
        source_path: pathlib.Path = args.c_source
        object_path: pathlib.Path = args.c_source.with_suffix(".obj")
        map_path: pathlib.Path = args.c_source.with_suffix(".map")
        
        stack.callback(lambda: map_path.unlink(missing_ok=True))
        stack.callback(lambda: object_path.unlink(missing_ok=True))
        subprocess.check_call([
            "gcc", f"{source_path}", "-o", f"{object_path}",
            "--std=c17", "-m64", "-finline-functions",
            "-Wno-builtin-declaration-mismatch", "-Wall", "-Wextra", "-Wno-unknown-pragmas",
            "-nostartfiles", "-nolibc", "-static-libgcc", "-fpie", "-ffreestanding",
            "-march=native", "-mmemcpy-strategy=rep_8byte:-1:noalign",
            "-T", f"{LINKER_SCRIPT}",
            "-O3",
            *shlex.split(args.cflags),
            "-Xlinker", f"-Map={map_path}",
        ])
        
        func_code: bytes = object_path.read_bytes()
        mapping: dict[str, int] = process_mapping(map_path.read_text())
        
        libc_relocs: dict[str, int] = gather_libc_relocs(mapping)
        
        func_offs: int = mapping[args.entry_point]
        
        # subprocess.check_call(["cp", f"{object_path}", "tmp.obj"])

    with args.output.open("w") as f:
        TEMPLATE_PY.stream(
            compress=args.compress,
            func_code=func_code,
            libc_relocs=libc_relocs,
            func_offs=func_offs,
        ).dump(f)


def process_mapping(mapping_text: str) -> dict[str, int]:
    mapping: dict[str, int] = {}
    
    for match in re.finditer(
        r"^\s*0x(?P<offs>[0-9a-f]+)\s+(?!\d)(?P<name>[a-zA-Z0-9_]+)(?: = \.)?\s*$",
        mapping_text,
        flags=re.MULTILINE,
    ):
        mapping[match.group("name")] = int(match.group("offs"), 16)
    
    return mapping


def gather_libc_relocs(mapping: dict[str, int]) -> dict[str, int]:
    libc_relocs: dict[str, int] = {}
    collect: bool = False
    
    for name, offs in mapping.items():
        if name == "__libc_imp_start":
            collect = True
            continue
        if name == "__libc_imp_end":
            collect = False
            break
        
        if collect:
            libc_relocs[name] = offs
    
    return libc_relocs


if __name__ == "__main__":
    exit(main())
