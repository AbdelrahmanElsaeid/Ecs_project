
from django.core.management.base import BaseCommand, CommandError
from src.utils.gpgutils import gen_keypair


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--owner', action='store', dest='owner', help='owner name of keypair', default=None)
        parser.add_argument('--secretfile', action='store', dest='secretfile', help='filename for secretkey', default=None)
        parser.add_argument('--publicfile', action='store', dest='publicfile', help='filename for publickey', default=None)

    def handle(self, *args, **options):
        if not options['owner']:
            raise CommandError('Error: Owner "--owner ownername" must be specified')
        if not options['secretfile']:
            raise CommandError('Error: Secretkeyfile "--secretfile filename" must be specified')
        if not options['publicfile']:
            raise CommandError('Error: Publickeyfile "--publicfile filename" must be specified')

        gen_keypair(options['owner'], options['secretfile'], options['publicfile'])











#------------------------------------------old Code--------------------------------------------------------


# from optparse import make_option
# from django.core.management.base import BaseCommand, CommandError
# from ecs.utils.gpgutils import gen_keypair


# class Command(BaseCommand):
#     option_list = BaseCommand.option_list + (
#         make_option('--owner', action='store', dest='owner', help='owner name of keypair', default=None),
#         make_option('--secretfile', action='store', dest='secretfile', help='filename for secretkey', default=None),
#         make_option('--publicfile', action='store', dest='publicfile', help='filename for publickey', default=None),
#     )
    
#     def handle(self, **options):
#         if not options['owner']:
#             raise CommandError('Error: Owner "--owner ownername" must be specified')
#         if not options['secretfile']: 
#             raise CommandError('Error: Secretkeyfile "--secretfile filename" must be specified')
#         if not options['publicfile']: 
#             raise CommandError('Error: Publickeyfile "--publicfile filename" must be specified')
        
#         gen_keypair(options['owner'], options['secretfile'], options['publicfile'])
