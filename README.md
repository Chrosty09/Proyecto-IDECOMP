# Proyecto IDECOMP — IDE y compilador del lenguaje CAOS

Proyecto de Compiladores II (UAA). IDE en Python/Tkinter con un compilador por fases para el lenguaje CAOS.

| Fase | Estado | Código |
|---|---|---|
| 1. Léxico | Completa | `external_compiler/lexer/` |
| 2. Sintáctico (AST) | Completa | `external_compiler/parser/` |
| 3. Semántico (tabla de símbolos, tipos) | Completa | `external_compiler/semantic/` |
| 4. Código TM y tres direcciones | Completa | `external_compiler/codegen/` |
| Ejecución | Simulador TM | `tm/tm.py` (IDE) y `tm/tm.c` (consola) |

La fase 4 recorre el árbol que ya validó el análisis semántico y escribe, por caminos paralelos:

- `code.tm`: instrucciones de la máquina TM. Es la entrada del simulador.
- `code.ci`: código de tres direcciones (temporales y etiquetas). Es una salida de estudio. El simulador no lo ejecuta.
- `intermediate.txt`: el mismo listado que `code.tm`.

El detalle de la arquitectura, las construcciones del lenguaje y la tabla de pruebas está en [`docs/generacion_codigo_y_pruebas.md`](docs/generacion_codigo_y_pruebas.md). La correspondencia con el compilador TINY de Louden está en [`docs/fase4-generacion-codigo.md`](docs/fase4-generacion-codigo.md).

## Requisitos

Python 3.10+ con Tkinter. Para el simulador en C hace falta `gcc`. Para regenerar el PDF de entrega: `pip install -r requirements.txt`.

## Uso desde el IDE

```
python ide/main.py
```

El IDE guarda el fuente y lanza `external_compiler/compiler_stub.py` con el directorio de trabajo `ide/outputs/`. Ahí quedan `code.tm`, `code.ci` y el resto de salidas. La pestaña **Codigo Intermedio** muestra el `code.tm` del archivo que acaba de compilarse. La pestaña **Codigo intermedio de tres direcciones** muestra el `code.ci`.

| Acción | Tecla | Qué pasa con `code.tm` |
|---|---|---|
| Análisis léxico | F5 | Se vacía. Esta fase no lo regenera. |
| Análisis sintáctico | F6 | Se vacía. |
| Análisis semántico | F7 | Se vacía. |
| Generación de código (TM) | F8 | Se escribe el listado del fuente actual, si no hay errores de análisis. |
| Ejecutar | F9 | Se recompila y el simulador integrado (`tm/tm.py`) ejecuta ese `code.tm`. Cada `IN`/`INF` pide el dato en un cuadro. |
| Abrir en TM (consola) | Shift+F9 | Se recompila y abre `tm/tm.c` compilado como `tm` o `tm.exe`. |

Cada acción vuelve a compilar el archivo guardado. El compilador borra sus salidas al empezar, así que el panel y `ide/outputs/code.tm` corresponden al fuente de esa compilación. Con errores léxicos, sintácticos o semánticos `code.tm` y `code.ci` quedan vacíos.

## Uso desde la consola

Los archivos de salida se escriben en el **directorio de trabajo**, con el nombre fijo `code.tm`. No se crea `<fuente>.tm` junto al programa.

Desde la raíz del repositorio, estas órdenes sí generan el `.tm` y lo ejecutan:

```
python external_compiler/compiler_stub.py pruebas/codegen/00_factorial.caos --phase intermedio
python tm/tm.py code.tm
```

En el simulador, `g` ejecuta hasta `HALT` y `q` sale. Para el factorial, la entrada del `cin` es un entero (por ejemplo `5`); la salida del programa es `120`.

Sin `--phase` el compilador corre todas las fases, incluida la generación, y también deja `code.tm` en el directorio actual:

```
python external_compiler/compiler_stub.py pruebas/codegen/06_operadores.caos
python tm/tm.py code.tm
```

El mismo listado en el simulador de C:

```
gcc -std=c11 -O2 tm/tm.c -o tm/tm -lm
./tm/tm code.tm
```

En Windows, `tm/compilar_tm.bat` produce `tm/tm.exe`. El comando equivalente es `tm\tm.exe code.tm`.

`--phase lexico`, `--phase sintactico` y `--phase semantico` analizan hasta esa fase y dejan `code.tm` vacío. El ejemplo histórico `python compiler_stub.py ../pruebas/TestSemantica.txt --phase semantico` solo corre el análisis: `TestSemantica.txt` además tiene errores semánticos, así que no debe producir código.

Para dejar las salidas en la misma carpeta que usa el IDE:

```
cd ide/outputs
python ../../external_compiler/compiler_stub.py ../../pruebas/codegen/00_factorial.caos --phase intermedio
python ../../tm/tm.py code.tm
```

Códigos de salida: 0 correcto, 1 léxico, 2 sintáctico, 3 semántico, 4 generación, 5 ejecución. La fase `ejecutar` del compilador de consola no lanza el simulador: escribe en `exec.txt` cómo ejecutarlo. Quien corre el programa es `tm/tm.py`, `tm/tm.c` o el IDE con F9. Más detalle de invocación en `external_compiler/README_run.txt`.

## Pruebas

```
cd external_compiler
python -m unittest test_semantico test_integracion test_parser_recovery test_codegen
cd ../ide
python -m unittest test_semantic_output
python ../pruebas/codegen/correr_casos_borde.py
python codigo_caos/probar_ejercicios.py
```

`correr_casos_borde.py` compila los programas `pruebas/codegen/borde_*.caos`, ejecuta su `code.tm` y compara la salida con el valor calculado a mano. `test_codegen` y `probar_ejercicios.py` cubren los programas de `pruebas/codegen/00`–`08` y los ejercicios de `codigo_caos/`.

## Estructura

- `ide/` — interfaz gráfica (editor, paneles, visor de árboles, simulador integrado).
- `external_compiler/` — léxico, sintáctico, semántico, generación (`codegen/`) y pruebas.
- `tm/` — simulador TM en Python (`tm.py`) y en C (`tm.c`).
- `pruebas/` — programas de prueba. `TestSemantica.txt` es la prueba oficial de la Fase 3. `pruebas/codegen/` incluye los programas de la Fase 4 y los casos de borde.
- `codigo_caos/` — ejercicios finales y el verificador que los ejecuta en la TM.
- `docs/` — documentación por fase, incluida la de generación y pruebas.
- `entrega/` — entregables de la Fase 3 (salidas, capturas, PDF y su generador).
