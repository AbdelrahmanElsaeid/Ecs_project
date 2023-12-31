import sys
import getpass

from django.core.management.base import CommandError
from django.core import exceptions
from django.core.validators import validate_email
from django.contrib.auth.management.commands.createsuperuser import Command as OrigCommand
from django.contrib.auth.models import User

from src.users.utils import create_user, hash_email

class Command(OrigCommand):
    def handle(self, *args, **options):
        username = options.get('username', None)
        email = options.get('email', None)
        interactive = options.get('interactive')

        if username:
            raise DeprecationWarning('there is no such thing as a username')

        if not interactive:
            if not email:
                raise CommandError('You must use --email with --noinput')
            try:
                validate_email(email)
            except exceptions.ValidationError:
                raise CommandError('Invalid email address.')

        password = ''

        if interactive:
            try:
                while 1:
                    if not email:
                        email = input('Email: ')
                    try:
                        validate_email(email)
                    except exceptions.ValidationError:
                        sys.stderr.write('Error: That e-mail address is invalid.\n')
                        email = None
                    else:
                        try:
                            User.objects.get(username=hash_email(email))
                        except User.DoesNotExist:
                            break
                        else:
                            print('Error: That e-mail address is already taken.', file=sys.stderr)
                            email = None

                while 1:
                    if not password:
                        password = getpass.getpass('Password:')
                        password2 = getpass.getpass('Password: (again):')
                        if password != password2:
                            print('Error: Your passwords didn\'t match.', file=sys.stderr)
                            password = None
                            continue
                    if password.strip() == '':
                        print('Error: Blank passwords aren\'t allowed.', file=sys.stderr)
                        password = None
                        continue
                    break

            except KeyboardInterrupt:
                print('Operation cancelled.', file=sys.stderr)
                sys.exit(1)


        u = create_user(email, is_superuser=True, is_staff = True, is_active=True)
        u.set_password(password)
        u.save()
        print('Superuser created successfully.')


