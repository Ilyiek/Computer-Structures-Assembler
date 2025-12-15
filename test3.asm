. Test Case 3: Addressing Modes
. Tests: Immediate (#), Indirect (@), Indexed (,X)

ADDR    START   3000
MAIN    LDA     #5          . Immediate addressing
        LDB     @PTR        . Indirect addressing
        LDX     INDEX       . Simple addressing
        LDCH    BUFFER,X    . Indexed addressing
        STA     VALUE       . Simple addressing
        ADD     #10         . Immediate
        COMP    @LIMIT      . Indirect
        JEQ     DONE
        LDA     TABLE,X     . Indexed
        
DONE    RSUB

. Data area
VALUE   WORD    100
INDEX   WORD    5
PTR     WORD    VALUE
LIMIT   WORD    200
BUFFER  RESB    50
TABLE   RESW    20

        END     MAIN