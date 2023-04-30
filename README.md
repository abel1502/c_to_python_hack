## C-to-Python packer

This is a small utility I've written for my algorithms course. Essentially, it
takes some C source code, compiles into into a bare-bone form, and then crafts
a python file that would load the precompiled bytecode into some mmap'd memory
and then execute it. It is intended to be used in programming contests, where
the only language allowed is Python, but you want to use C for performance.

To use this, you only need `pack_c.py` and `linker.ld` from this repository.
The rest of the files are artifacts from my own usage.

The additional requirements to run this are:
 - `gcc`
 - `python` (has to be Python 3. Tested on python3.10)
 - `jinja2`
