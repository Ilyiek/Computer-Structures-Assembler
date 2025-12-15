. Sample SIC/XE Program - Test Case 1
. Tests: Basic instructions, symbol table, addressing modes
. Expected Output: Object program with H, T, M, E records

COPY    START   1000
FIRST   LDA     ALPHA       . Load ALPHA
        ADD     BETA        . Add BETA
        STA     GAMMA       . Store in GAMMA
        LDB     #LENGTH     . Immediate addressing
        LDX     DELTA       . Load index register
        LDCH    BUFFER,X    . Indexed addressing
        +LDA    MAXLEN      . Format 4 (extended)
        COMP    #0          . Compare immediate
        JEQ     DONE        . Jump if equal
        J       FIRST       . Loop back
DONE    RSUB                . Return
        
. Data area
ALPHA   RESW    1           . Reserve 1 word
BETA    RESW    1
GAMMA   RESW    1
DELTA   WORD    5           . Initialize to 5
BUFFER  RESB    100         . Reserve 100 bytes
LENGTH  WORD    100
MAXLEN  WORD    1000
        
        END     FIRST       . First executable instruction