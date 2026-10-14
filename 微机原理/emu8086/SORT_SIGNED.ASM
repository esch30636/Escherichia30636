;==============================================================
; 例4.40 改写版：有符号数冒泡排序（小 -> 大）
; 数据: -12, 7, -19, 8, -24
; 适配: emu8086 (EXE 格式)
;==============================================================
DATA    SEGMENT
        LIST    DW  -12, 7, -19, 8, -24   ; 数组字单元（有符号）
        COUNT   EQU ($-LIST)/2            ; 数组长度 n = 10/2 = 5
        MSG1    DB  'Before: $'
        MSG2    DB  0DH,0AH,'After : $'
        DIGITS  DB  10 DUP(0)             ; 显示数字用的缓冲区
DATA    ENDS

CODE    SEGMENT
        ASSUME  CS: CODE, DS: DATA
BEGIN:  MOV     AX, DATA
        MOV     DS, AX                    ; 设置 DS

        MOV     DX, OFFSET MSG1
        CALL    PRINT_STR
        CALL    PRINT_ARRAY               ; 显示排序前

        MOV     CX, COUNT-1               ; CX <- 比较轮数（大循环次数 = 4）
LOOP1:  MOV     DX, CX                    ; DX <- 大循环次数（保存）
        MOV     BX, 0                     ; 地址指针
LOOP2:  MOV     AX, LIST[BX]              ; AX <- LIST(i)
        CMP     AX, LIST[BX+2]            ; LIST(i) < LIST(i+1) ?（有符号比较）
        JL      NO_CHANGE                 ; 否（>=），转（大数已在前，不必换）
        XCHG    AX, LIST[BX+2]            ; 否，交换
        MOV     LIST[BX], AX
NO_CHANGE:
        ADD     BX, 2                     ; BX 增2，取下个数
        LOOP    LOOP2                     ; 一轮没比完，转，继续比
        MOV     CX, DX                    ; 一轮比完，CX <- 比较轮数
        LOOP    LOOP1                     ; CX <- CX-1，非0则转下轮比较

        MOV     DX, OFFSET MSG2
        CALL    PRINT_STR
        CALL    PRINT_ARRAY               ; 显示排序后

        MOV     AX, 4C00H
        INT     21H                       ; 返回DOS

;--------------------------------------------------------------
; PRINT_STR : 显示 DS:DX 处 '$' 结尾的字符串
;--------------------------------------------------------------
PRINT_STR PROC
        MOV     AH, 9
        INT     21H
        RET
PRINT_STR ENDP

;--------------------------------------------------------------
; PRINT_BYTE : 显示 AL 中的字符
;--------------------------------------------------------------
PRINT_BYTE PROC
        PUSH    AX
        PUSH    DX
        MOV     DL, AL
        MOV     AH, 2
        INT     21H
        POP     DX
        POP     AX
        RET
PRINT_BYTE ENDP

;--------------------------------------------------------------
; PRINT_CRLF : 回车换行
;--------------------------------------------------------------
PRINT_CRLF PROC
        PUSH    AX
        PUSH    DX
        MOV     DL, 0DH
        MOV     AH, 2
        INT     21H
        MOV     DL, 0AH
        MOV     AH, 2
        INT     21H
        POP     DX
        POP     AX
        RET
PRINT_CRLF ENDP

;--------------------------------------------------------------
; PRINT_NUM : 以十进制显示 AX 中的有符号数（自动带负号）
;--------------------------------------------------------------
PRINT_NUM PROC
        PUSH    AX
        PUSH    BX
        PUSH    CX
        PUSH    DX
        PUSH    SI

        CMP     AX, 0
        JGE     PN_POS
        PUSH    AX                    ; 负数：先输出 '-'，再取绝对值
        MOV     AL, '-'
        CALL    PRINT_BYTE
        POP     AX
        NEG     AX
PN_POS: MOV     SI, 10                ; SI 指向 DIGITS 末尾
        MOV     CX, 0                 ; CX = 位数
PN_DIV: MOV     DX, 0
        MOV     BX, 10
        DIV     BX                    ; AX=商, DX=余数
        ADD     DL, '0'               ; 余数转 ASCII
        DEC     SI
        MOV     [SI], DL              ; 从后往前存放
        INC     CX
        CMP     AX, 0
        JNE     PN_DIV
PN_OUT: MOV     DL, [SI]              ; 从高位到低位输出
        MOV     AH, 2
        INT     21H
        INC     SI
        LOOP    PN_OUT

        POP     SI
        POP     DX
        POP     CX
        POP     BX
        POP     AX
        RET
PRINT_NUM ENDP

;--------------------------------------------------------------
; PRINT_ARRAY : 依次显示 LIST 中的 5 个有符号数
;--------------------------------------------------------------
PRINT_ARRAY PROC
        PUSH    AX
        PUSH    BX
        PUSH    CX
        PUSH    SI
        MOV     SI, 0                 ; 下标（字节偏移）
        MOV     CX, COUNT
PA_1:   MOV     AX, LIST[SI]
        CALL    PRINT_NUM
        MOV     AL, ' '
        CALL    PRINT_BYTE
        ADD     SI, 2
        LOOP    PA_1
        CALL    PRINT_CRLF
        POP     SI
        POP     CX
        POP     BX
        POP     AX
        RET
PRINT_ARRAY ENDP

CODE    ENDS
        END     BEGIN
