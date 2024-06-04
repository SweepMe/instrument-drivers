import sys
from pathlib import Path

import clr

SDK_PATH = Path(r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1")

sys.path.append(str(SDK_PATH))

clr.AddReference("EcoChemie.Autolab.Sdk")

import EcoChemie.Autolab.Sdk as autolab_sdk

autolab_instrument = autolab_sdk.Instrument()

autolab_instrument.HardwareSetupFile = str(SDK_PATH / "Hardware Setup Files" / "PGSTAT302N" / "HardwareSetup.AUT83940.xml")

autolab_instrument.AutolabConnection.EmbeddedExeFileToStart = str(SDK_PATH / "Hardware Setup Files" / "Adk.x")


def print_parameters(command):
    for parameter in command.CommandParameters.IdNames:
        print(" " * 7, f"'{parameter}'", command.CommandParameters[parameter].__class__.__name__)


def print_signals(command):
    for signal in command.Signals.IdNames:
        print(" " * 7, f"'{signal}'", command.Signals[signal].__class__.__name__)


def print_commands(procedure):
    for command in list(procedure.Commands.IdNames):
        print(f"  Command '{command}'")
        print("    - Parameters:")
        print_parameters(procedure.Commands[command])
        print("    - Signals:")
        print_signals(procedure.Commands[command])
        print()


def print_procedures():
    for procedure in (SDK_PATH / "Standard Nova Procedures").iterdir():
        if not procedure.is_file() or procedure.suffix != ".nox":
            continue
        print(f"Procedure '{procedure.stem}'")
        print_commands(autolab_instrument.LoadProcedure(str(procedure)))
        print()


def print_procedure_functions():
    for func in dir(autolab_sdk.IProcedure):
        if func.startswith("_"):
            continue
        print(getattr(autolab_sdk.IProcedure, func).__doc__ or func)


print("--------------------")
print("Procedure Parameters")
print("--------------------\n")
print_procedures()
print("-------------------")
print("Procedure Functions")
print("-------------------\n")
print_procedure_functions()