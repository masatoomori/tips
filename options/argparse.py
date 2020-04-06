import argparse


def main():
    parser = argparse.ArgumentParser(
        prog='<script name>',
        usage='',
        description='',
        epilog='',
        add_help=True
    )
    parser.add_argument('-c', '--choices',
                        choices=['option 1', 'option 2'],
                        help='choose option from list',
                        default='option 1')
    parser.add_argument('-f', '--flag',
                        help='on/off flag',
                        action='store_true')
    parser.add_argument('-n', '--number',
                        help='store int type',
                        type=int)
    parser.add_argument('-l', '--lambda',
                        help='store type defined by lambda',
                        type=lambda x: x)
    parser.add_argument('-m', '--multiple_items',
                        help='store multiple times in list',
                        nargs='*')
    parser.add_argument('-r', '--required',
                        help='required arg',
                        required=True)
    args = parser.parse_args()


if __name__ == '__main__':
    main()
