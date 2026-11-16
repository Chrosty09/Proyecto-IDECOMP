================================================================================
 README_run.txt — Cómo invocar el compilador del IDE CAOS
================================================================================

DESCRIPCIÓN
-----------
compiler_stub.py es el punto de entrada del pipeline de compilación del
lenguaje CAOS. Fases: léxico, sintáctico, semántico, generación de código TM
y de tres direcciones, y un aviso de ejecución. La ejecución del programa la
hace el simulador TM (tm/tm.py en el IDE, tm/tm.c en consola), no este script.
El IDE lo invoca con CompilerRunner (subprocess) y cwd = ide/outputs/.
(El nombre del archivo se conserva por compatibilidad con el IDE.)

El detalle de la generación y de las pruebas está en
docs/generacion_codigo_y_pruebas.md.


INVOCACIÓN
----------
Sintaxis general:

    python compiler_stub.py <ruta_fuente> [--phase <fase>]

Argumentos:

    <ruta_fuente>         Ruta (absoluta o relativa) al archivo .caos a compilar.
                          Este argumento es OBLIGATORIO.

    --phase <fase>        (Opcional) Ejecuta únicamente hasta la fase indicada.
                          Valores válidos:
                              lexico       → Solo análisis léxico
                              sintactico   → Léxico + análisis sintáctico
                              semantico    → + análisis semántico
                              intermedio   → + code.tm, code.ci e intermediate.txt
                              ejecutar     → Pipeline completo (también genera el .tm)
                          Si se omite --phase, se ejecuta el pipeline completo.

                          lexico, sintactico y semantico dejan code.tm vacío:
                          al empezar se truncan todas las salidas y esas fases
                          no vuelven a escribir el .tm. intermedio y ejecutar
                          lo llenan si no hubo errores de análisis.


DIRECTORIO DE TRABAJO
---------------------
Los archivos se escriben en el directorio de trabajo del proceso, con nombres
fijos. El IDE usa cwd = ide/outputs/, así que ahí queda ide/outputs/code.tm.
Desde una consola quedan en el directorio desde el que se lanzó el comando.
No se crea <fuente>.tm junto al programa.


ARCHIVOS DE SALIDA
------------------
    tokens.txt          Tabla de tokens
    syntax.txt          Árbol sintáctico
    semantic.txt        Análisis semántico
    symbols.txt         Tabla de símbolos
    errors.txt          Errores de todas las fases
    code.tm             Instrucciones para la TM. Entrada del simulador.
    code.ci             Código de tres direcciones. El simulador no lo ejecuta.
    intermediate.txt    El mismo listado que code.tm
    exec.txt            Aviso de cómo ejecutar code.tm. No es la salida del programa.

Con errores de análisis, o si la fase pedida es anterior a intermedio,
code.tm y code.ci quedan vacíos.


FORMATO DE errors.txt
---------------------
Cada error debe ir precedido de una etiqueta de fase entre corchetes:

    [LEXICO] [4:7] Carácter inválido '@'
    [SINTACTICO] [12:5] Se esperaba ';' al final de la sentencia
    [SEMANTICO] [18:3] Variable 'x' no declarada
    [GENERACION] Construcción que no se pudo traducir a TM

Las etiquetas no distinguen mayúsculas/minúsculas.
El IDE también reconoce la palabra "intermedio" dentro de la etiqueta como
error de generación.


CÓDIGOS DE RETORNO
------------------
    0   Éxito total (o hasta la fase indicada).
    1   Error en análisis léxico.
    2   Error en análisis sintáctico.
    3   Error en análisis semántico.
    4   Error en generación de código.
    5   Error en la fase ejecutar.
   -1   Timeout (IDE mató el proceso).
   -2   Compilador no encontrado.
   -3   Error interno inesperado.


EJEMPLO DE USO (desde la raíz del repositorio)
----------------------------------------------
    # Genera ./code.tm y ./code.ci
    python external_compiler/compiler_stub.py pruebas/codegen/00_factorial.caos --phase intermedio

    # Ejecuta ese code.tm. En el simulador: g para correr, q para salir.
    python tm/tm.py code.tm

    # El mismo simulador en C
    gcc -std=c11 -O2 tm/tm.c -o tm/tm -lm
    ./tm/tm code.tm

    # Solo hasta semántica: code.tm queda vacío
    python external_compiler/compiler_stub.py pruebas/TestSemantica.txt --phase semantico
================================================================================
