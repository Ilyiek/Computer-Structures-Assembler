. Test Case 6: Format 4 Instructions and Literals
. Tests: Extended format (+) and literal operands (=)

FMT4    START   6000
BEGIN   +LDA    DISTANT     . Format 4 (20-bit address)
        +STA    FARAWAY     . Format 4
        LDA     =C'EOF'     . Character literal
        LDB     =X'05'      . Hex literal
        +LDX    #4096       . Format 4 immediate
        LDCH    =C'A'       . Character literal
        COMP    =X'FF'      . Hex literal
        +JSUB   SUBR        . Format 4 subroutine call
        J       BEGIN
        
SUBR    +LDA    DISTANT
        RSUB

. Local data
LOCAL   WORD    100

. Large gap (forces Format 4 usage)
        RESB    4000

DISTANT WORD    500
FARAWAY RESW    1

        END     BEGIN