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
        *
    }
    /DISCARD/ : {
        *(.eh_frame)
    }
}

