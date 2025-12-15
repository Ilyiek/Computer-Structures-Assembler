. Test Case 4: PC-Relative Addressing
. Tests: Forward and backward references within PC-relative range

PCTEST  START   4000
INIT    LDA     ZERO        . Forward reference
        STA     COUNT
        
LOOP    LDA     COUNT       . Loop with backward jump
        ADD     ONE
        STA     COUNT
        COMP    LIMIT
        JLT     LOOP        . Backward reference
        JEQ     EXIT        . Forward reference
        J       LOOP
        
EXIT    LDA     RESULT
        RSUB

. Data within PC-relative range
ZERO    WORD    0
ONE     WORD    1
COUNT   RESW    1
LIMIT   WORD    10
RESULT  RESW    1

        END     INIT