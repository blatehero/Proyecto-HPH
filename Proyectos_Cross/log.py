import os
import traceback


ruta_log = os.path.join(
    os.path.dirname(__file__),
    "errores.log"
)


def log(mensaje):

    with open(
        ruta_log,
        "a",
        encoding="utf-8"
    ) as archivo:

        archivo.write(
            str(mensaje) + "\n"
        )


def limpiar_log():

    with open(
        ruta_log,
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write("")


def log_error():

    with open(
        ruta_log,
        "a",
        encoding="utf-8"
    ) as archivo:

        archivo.write("\n")
        archivo.write("=" * 80)
        archivo.write("\nERROR\n")
        archivo.write(traceback.format_exc())
        archivo.write("\n")
        archivo.write("=" * 80)
        archivo.write("\n")