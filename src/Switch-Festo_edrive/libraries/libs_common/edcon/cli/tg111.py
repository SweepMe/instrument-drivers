"""CLI tool that performs a sequence on Telegram111 and EDrive classes."""
import sys
from edcon.edrive.telegram111_handler import Telegram111Handler


def add_tg111_parser(subparsers):
    """Adds arguments to a provided subparsers instance"""
    parser_tg111 = subparsers.add_parser('tg111')
    parser_tg111.set_defaults(func=tg111_func)

    parser_tg111.add_argument('-o', '--over_v', default="100.0",
                              help='Target position to be reached (default: %(default)s).')


def tg111_func(com, args):
    """Executes subcommand based on provided arguments"""
    with Telegram111Handler(com) as tg111:
        tg111.telegram.override.value = int(16384*(float(args.over_v)/100.0))
        tg111.telegram.mdi_acc.value = 16384
        tg111.telegram.mdi_dec.value = 16384
        if not tg111.acknowledge_faults():
            sys.exit(1)
        if not tg111.enable_powerstage():
            sys.exit(1)
        if not tg111.set_current_position_task():
            sys.exit(1)
        tg111.position_task(position=1000000, velocity=60000)
