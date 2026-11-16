#!/usr/bin/env python3
"""
Compila los programas de borde de pruebas/codegen/borde_*.caos, ejecuta el
code.tm en tm/tm.py y, si hay gcc, en tm/tm.c, y compara la salida con el
valor calculado a mano.

No modifica el compilador: solo lo invoca.

    python pruebas/codegen/correr_casos_borde.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
STUB = RAIZ / "external_compiler" / "compiler_stub.py"
TM_C = RAIZ / "tm" / "tm.c"

sys.path.insert(0, str(RAIZ))
from tm.tm import HALT, ZERODIVIDE, TMSimulator, parse_input  # noqa: E402


# (archivo, entradas, salida del programa, estado de la TM)
CASOS = [
    ("borde_01_precedencia_parentesis.caos", [],
     "14\n20\n64\n76\n13\n18\n36\n", HALT),
    ("borde_02_potencia_derecha_modulo.caos", [],
     "512\n2\n3\n24\n", HALT),
    ("borde_03_tipos_div_float_bool.caos", [],
     "3\n3.0\n3.5\n1\n0\n1\n", HALT),
    ("borde_04_relacionales.caos", [],
     "0\n1\n0\n1\n1\n0\n1\n1\n1\n1\n", HALT),
    ("borde_05_logicos_precedencia_y_not.caos", [],
     "0\n1\n0\n0\n1\n1\n", HALT),
    ("borde_06_cortocircuito_div0.caos", [],
     "0\n1\n1\n", HALT),
    ("borde_07_cortocircuito_cae_en_div0.caos", [],
     "", ZERODIVIDE),
    ("borde_08_if_else_anidado.caos", [],
     "2\n0\n4\n", HALT),
    ("borde_09_while_no_entra_y_anidado.caos", [],
     "5\n6\n3\n", HALT),
    ("borde_10_while_condicion_compuesta_no_entra.caos", [],
     "0\n", HALT),
    ("borde_11_do_until_bordes.caos", [],
     "4\n3\n4\n", HALT),
    ("borde_12_do_until_no_repite_si_verdadero.caos", [],
     "11\n", HALT),
    ("borde_13_cin_cout_tipos.caos", [4, 5, 1.5, 2],
     "9\n1.5\n1\nhola\tmundo\nlinea1\nlinea2\n4 y 1.5\n", HALT),
    ("borde_14_cin_negativos_modulo.caos", [-17, 5],
     "-2\n-3\n", HALT),
    ("borde_15_cin_modulo_signos.caos", [17, -5],
     "2\n-3\n", HALT),
    ("borde_16_inc_dec_y_real.caos", [],
     "11\n11.5\n", HALT),
    ("borde_17_if_sin_else_y_while_end.caos", [],
     "4\n6\n", HALT),
    ("borde_18_bool_cero_y_uno.caos", [0, 1, -4],
     "0\n1\n1\n", HALT),
    ("borde_19_parentesis_en_condicion.caos", [],
     "20\n", HALT),
    ("borde_20_asignacion_expr_mixta.caos", [],
     "19\n19.5\n", HALT),
]


def compilar(fuente: Path, fase: str, cwd: Path) -> tuple[int, dict[str, str], str]:
    r = subprocess.run(
        [sys.executable, str(STUB), str(fuente), "--phase", fase],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8",
    )
    archivos = {p.name: p.read_text(encoding="utf-8") for p in cwd.iterdir() if p.is_file()}
    return r.returncode, archivos, r.stderr


def ejecutar_py(tm_code: str, entradas: list) -> tuple[str, str]:
    pendientes = [str(e) for e in entradas]

    def leer(real: bool):
        if not pendientes:
            return None
        valor = parse_input(pendientes.pop(0), real)
        if valor is None:
            raise ValueError("entrada no válida para la TM")
        return valor

    salida: list[str] = []
    tm = TMSimulator(on_input=leer, on_output=salida.append)
    tm.load(tm_code)
    estado = tm.run(max_steps=2_000_000)
    return "".join(salida), estado


def tm_exe() -> Path | None:
    gcc = shutil.which("gcc")
    if not gcc:
        return None
    destino = Path(tempfile.gettempdir()) / "tm_casos_borde"
    r = subprocess.run(
        [gcc, "-std=c11", "-O2", str(TM_C), "-o", str(destino), "-lm"],
        capture_output=True, text=True,
    )
    return destino if r.returncode == 0 else None


def ejecutar_c(exe: Path, tm_code: str, entradas: list) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        archivo = Path(tmp) / "code.tm"
        archivo.write_text(tm_code, encoding="utf-8")
        stdin = "g\n" + "".join(f"{e}\n" for e in entradas) + "q\n"
        r = subprocess.run(
            [str(exe), str(archivo)], input=stdin.encode("utf-8"),
            capture_output=True, timeout=30,
        )
    texto = r.stdout.decode("utf-8", errors="replace").replace("\r\n", "\n")
    for prompt in (
        "TM  simulation (enter h for help)...\n",
        "Enter command: ",
        "Enter value for IN instruction: ",
        "Enter real value for INF instruction: ",
        "Simulation done.\n",
    ):
        texto = texto.replace(prompt, "")
    return texto


def verificar_archivo_actual(fallos: list[str]) -> None:
    """code.tm sigue al fuente de esta compilación y una fase anterior lo vacía."""
    a = AQUI / "borde_cache_a.caos"
    b = AQUI / "borde_cache_b.caos"
    with tempfile.TemporaryDirectory() as tmp:
        cwd = Path(tmp)
        codigo_a, archivos_a, err_a = compilar(a, "intermedio", cwd)
        tm_a = archivos_a.get("code.tm", "")
        codigo_b, archivos_b, err_b = compilar(b, "intermedio", cwd)
        tm_b = archivos_b.get("code.tm", "")
        codigo_s, archivos_s, _ = compilar(a, "semantico", cwd)
        tm_s = archivos_s.get("code.tm", "")
    if codigo_a != 0 or "File: borde_cache_a.caos" not in tm_a or "HALT" not in tm_a:
        fallos.append(f"cache A: no generó su code.tm ({err_a.strip()})")
    if codigo_b != 0 or "File: borde_cache_b.caos" not in tm_b or "borde_cache_a.caos" in tm_b:
        fallos.append(f"cache B: code.tm no corresponde al fuente actual ({err_b.strip()})")
    if codigo_s != 0 or tm_s != "":
        fallos.append("fase semantico: code.tm debía quedar vacío")


def main() -> int:
    fallos: list[str] = []
    exe = tm_exe()
    finales = {HALT: "HALT: 0,0,0\nHalted\n", ZERODIVIDE: "Division by 0\n"}
    print(f"{'Programa':<46} {'tm.py':<8} {'tm.c':<8}")
    print("-" * 64)
    for nombre, entradas, esperado, estado in CASOS:
        with tempfile.TemporaryDirectory() as tmp:
            codigo, archivos, err = compilar(AQUI / nombre, "intermedio", Path(tmp))
        tm_code = archivos.get("code.tm", "")
        if codigo != 0 or "HALT" not in tm_code:
            fallos.append(f"{nombre}: no generó code.tm (salida {codigo}) {err.strip()}")
            print(f"{nombre:<46} {'FALLA':<8} {'-':<8}")
            continue
        try:
            obtenido, estado_py = ejecutar_py(tm_code, entradas)
        except (ValueError, Exception) as exc:  # noqa: BLE001
            fallos.append(f"{nombre}: {exc}")
            print(f"{nombre:<46} {'FALLA':<8} {'-':<8}")
            continue
        ok_py = obtenido == esperado and estado_py == estado
        if not ok_py:
            fallos.append(
                f"{nombre}: tm.py obtuvo {estado_py!r} {obtenido!r}; "
                f"esperado {estado!r} {esperado!r}"
            )
        ok_c = True
        marca_c = "omitido"
        if exe:
            texto_c = ejecutar_c(exe, tm_code, entradas)
            ok_c = texto_c == esperado + finales[estado]
            marca_c = "OK" if ok_c else "FALLA"
            if not ok_c:
                fallos.append(f"{nombre}: tm.c obtuvo {texto_c!r}")
        print(f"{nombre:<46} {'OK' if ok_py else 'FALLA':<8} {marca_c:<8}")

    verificar_archivo_actual(fallos)
    if fallos:
        print()
        for fallo in fallos:
            print(fallo)
        return 1
    simulador = "tm.py y tm.c" if exe else "tm.py (sin gcc)"
    print()
    print(f"{len(CASOS)} casos correctos en {simulador}.")
    print("code.tm sigue al fuente actual; --phase semantico lo deja vacío.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
