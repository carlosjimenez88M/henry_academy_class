######################################
# ---- Python como calculadora ---- #
#####################################

print(5 + 8)


calculo = (6 * 6) ** 2
print(calculo)

# ----- usando mi primer libreria ----- #
from math import sqrt
from re import L, error

# raiz_cuadrada = int(input("Escribre un numero"))
# operacion = sqrt(raiz_cuadrada)
# print(operacion)


# ---- una operacion dentro de una funcion ------ #

import logging


class ColorFormatter(logging.Formatter):
    """Traffic-light color formatter: cyan → green → yellow → red."""

    _COLORS = {
        logging.DEBUG: "\033[36m",  # cyan
        logging.INFO: "\033[32m",  # green
        logging.WARNING: "\033[33m",  # yellow
        logging.ERROR: "\033[31m",  # red
        logging.CRITICAL: "\033[1;31m",  # bold red
    }
    _RESET = "\033[0m"
    _FMT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def format(self, record: logging.LogRecord) -> str:
        color = self._COLORS.get(record.levelno, self._RESET)
        record = logging.makeLogRecord(record.__dict__)
        record.levelname = f"{color}{record.levelname}{self._RESET}"
        record.msg = f"{color}{record.msg}{self._RESET}"
        return logging.Formatter(self._FMT).format(record)


def get_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """Return a singleton color logger; handlers are attached only once."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(ColorFormatter())
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False
    return logger


logger = get_logger("data")


def encontrar_sqrt(valor=int(input("Escribe el valor: "))):
    try:
        logger.info("Empezo a procesar")
        valor_retorno = sqrt(valor)
        logger.info("Finalizo el proceso")
        return valor_retorno
    except:

        logger.error("Lo que coloco no es un valor o no tiene raiz cuadrada")
        pass


a1 = encontrar_sqrt()
print(a1)


# --- if statements ---- #

lista = ["Alicia", "Emilia", "Maria", "Chucho"]
lista[3] = "JuanPA"

for i in lista:
    print("El nombre es :", i)

eventos = list(range(0, 20, 2))

for i in eventos:
    print(i)
    evento_doble = i * i
    print(evento_doble)

dias_de_la_semana = ["Lunes", "Miercoles", "Viernes", "Sabado", "Domingo"]

for i in dias_de_la_semana:
    if i == "Lunes":
        print(i, " Por lo tanto toca ir a trabajar")
    elif i == "Miercoles":
        print(i, " Toca clase de cocina")
    elif i == "Sabado":
        print(i, "Toca ver el partido")
    elif i == "Domingo":
        print(i, "TOca Dormir hasta tarde")

# for i in dias_de_la_semana:
#    if i == "Sabado":
#        print("opcion1")
#    else:
#        print(i, "por lo tanto toca programar")

##################
# ---- Dict ---- #
##################

ages = {"JuanPa": 21, "Chantal": 19}
print(ages)
print(len(ages))
ages["JuanPa"] = 19
print(ages)
