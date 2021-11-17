import argparse


class Limiter(object):
    def __init__(self):
        args = self.create_parser().parse_args()
        self.debug = args.debug

    def create_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--debug', dest='debug', help='debug_mode', default=False, action='store_true')
        parser.add_argument('--verbose', dest='verbose', help='Print logs', default=False, action='store_true')

        return parser

    def run(self):
        print(self.debug)
        print('kaki')
        pass


if __name__ == '__main__':
    Limiter().run()
