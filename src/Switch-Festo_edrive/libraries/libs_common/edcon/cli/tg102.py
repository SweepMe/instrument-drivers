"""CLI tool that performs a sequence on Telegram102 and EDrive classes."""
import sys
from edcon.edrive.telegram102_handler import Telegram102Handler


def add_tg102_parser(subparsers):
    """Adds arguments to a provided subparsers instance"""
    parser_tg102 = subparsers.add_parser('tg102')
    parser_tg102.set_defaults(func=tg102_func)
    parser_tg102.add_argument('-s', '--speed-setpoint', default="1000000000",
                              help='Speed setpoint to use (default: %(default)s).')
    parser_tg102.add_argument('-m', '--moment-reduction', default="0.0",
                              help='Moment reduction to use in percent (default: %(default)s).')


def tg102_func(com, args):
    """Executes subcommand based on provided arguments"""
    with Telegram102Handler(com) as tg102:
        tg102.telegram.momred.value = round(
            16384.0 * float(args.moment_reduction) / 100.0)

        if not tg102.acknowledge_faults():
            sys.exit(1)
        if not tg102.enable_powerstage():
            sys.exit(1)
        if not tg102.velocity_task(int(args.speed_setpoint), duration=3.0):
            sys.exit(1)
