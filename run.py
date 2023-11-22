import argparse

import tornado.ioloop

from flight.models import create_database
import flight.urls as application

def runserver(args):
    print('Starting server...')
    app = application.application()
    app.listen(8000, '0.0.0.0')
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print("Server interrupted. Shutting down...")
        tornado.ioloop.IOLoop.current().stop()

def migrate(args):
    create_database()
    print('Migration applied')

def main():
    parser = argparse.ArgumentParser(description='Custom Run Command')
    subparsers = parser.add_subparsers()

    runserver_parser = subparsers.add_parser('runserver', help='Run the server')
    runserver_parser.set_defaults(func=runserver)

    runmigrations_parser = subparsers.add_parser('migrate', help='Run migrations')
    runmigrations_parser.set_defaults(func=migrate)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()