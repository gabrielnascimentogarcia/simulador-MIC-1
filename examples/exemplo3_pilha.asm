; Exemplo 3: Pilha e Subrotinas
; Demonstra o uso de PUSH, POP, CALL e RETN

LOCO 10
PUSH        ; Empilha 10
LOCO 20
PUSH        ; Empilha 20

CALL 20     ; Chama subrotina no endereco 20
            ; Ao retornar, AC deve ter a soma (30)

STOD 100    ; Salva resultado
JUMP 0      ; Fim

; --- Subrotina de Soma ---
; Endereco 20
POP         ; Desempilha 20 para AC
STOD 200    ; Salva temp
POP         ; Desempilha 10 para AC
ADDD 200    ; Soma 10 + 20
RETN        ; Retorna com resultado no AC
