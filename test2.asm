. Test Case 2: All Directives
. Tests: START, END, RESW, RESB, WORD, BYTE directives

PROG    START   2000
BEGIN   LDA     NUM1
        ADD     NUM2
        STA     RESULT
        
. Reserve storage
BUFFER  RESB    100         . Reserve 100 bytes
TABLE   RESW    50          . Reserve 50 words (150 bytes)

. Initialize data
NUM1    WORD    10          . One word = 3 bytes
NUM2    WORD    20
RESULT  RESW    1

. Byte constants
MSG1    BYTE    C'HELLO'    . Character constant
MSG2    BYTE    X'F1'       . Hex constant
BYTVAL  BYTE    X'05'

. More reserved storage
STACK   RESB    200
TEMP    RESW    10

        END     BEGIN