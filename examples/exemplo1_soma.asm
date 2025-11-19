; Exemplo 1: Soma Simples
; Este programa carrega o valor 10, soma com 20 e salva na memoria.

LOCO 10     ; Carrega a constante 10 no Acumulador (AC)
STOD 500    ; Salva o valor do AC (10) na memoria no endereco 500
LOCO 20     ; Carrega a constante 20 no AC
ADDD 500    ; Soma o valor da memoria[500] (que eh 10) com o AC (20)
            ; Agora AC deve valer 30
STOD 501    ; Salva o resultado (30) na memoria no endereco 501
JUMP 0      ; Loop infinito (volta para o inicio)
