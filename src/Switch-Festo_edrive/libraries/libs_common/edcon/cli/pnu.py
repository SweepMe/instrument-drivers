"""CLI Tool to read or write PNUs of a EDrive device."""


def add_pnu_parser(subparsers):
    """Adds arguments to a provided subparsers instance"""
    parser_pnu = subparsers.add_parser('pnu')
    parser_pnu.set_defaults(func=pnu_func)

    parser_pnu.add_argument("-p", "--pnu", default="3490",
                            help="PNU to use for read/write (default: %(default)s).")
    parser_pnu.add_argument("-s", "--subindex", default="0",
                            help="Subindex to use for read/write (default: %(default)s).")

    subparsers_pnu = parser_pnu.add_subparsers(dest='subcommand', required=True,
                                               title='action commands',
                                               description="Action to perform on the PNU")

    # Options for reading PNU
    parser_read = subparsers_pnu.add_parser('read')
    parser_read.add_argument(
        '-r', '--raw', help='Raw read of provided number of items')

    # Options for writing PNU
    parser_write = subparsers_pnu.add_parser('write')
    parser_write.add_argument('value', help='Value to be written')


def pnu_func(com, args):
    """Executes subcommand based on provided arguments"""
    pnu = int(args.pnu)
    subindex = int(args.subindex)
    if args.subcommand == 'read':
        if args.raw:
            pnu_value = com.read_pnu_raw(
                pnu, subindex, num_elements=int(args.raw))
            if pnu_value:
                print(f"Length: {len(pnu_value)}")
        else:
            pnu_value = com.read_pnu(pnu, subindex)
        print(f"Value: {pnu_value}")

    elif args.subcommand == 'write':
        com.write_pnu(pnu, subindex, args.value)
