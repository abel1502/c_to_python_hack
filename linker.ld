OUTPUT_FORMAT("binary")

SECTIONS
{
    . = 0;
    __libc_imp_start = .;
    .libc-imp : {
        *(.libc-imp)
    }
    __libc_imp_end = .;
    .text : {
        *(.text)
        *(.data)
        *(.rodata)
        *(.bss)
        *(COMMON)
        
        start_ctors = .;
        *(.ctor*)
        end_ctors = .;
        start_dtors = .;
        *(.dtor*)
        end_dtors = .;
    }
    /DISCARD/ : {
        *(.eh_frame)
    }
}

