# from optparse import make_option

# from django.core.management.base import BaseCommand, CommandError
# from django.template.loader import get_template

# from ecs.core.serializer import Serializer
# from ecs.utils.pdfutils import html2pdf


# class Command(BaseCommand):
#     option_list = BaseCommand.option_list + (
#         make_option('-o', action='store', dest='outfile', help='output file', default=None),
#         make_option('-t', dest='output_type', action='store', default='html', 
#             help="one of 'html' or 'pdf'"),
#     )

#     def handle(self, **options):
#         if options['output_type'] not in ['html', 'pdf']:
#             raise CommandError('Error: --type must be one of "html", "pdf"')
#         if not options['outfile']: 
#             raise CommandError('Error: Outputfile "-o filename" must be specified')
        
#         ecxf = Serializer()
#         tpl = get_template('docs/ecx/base.html')
#         html = tpl.render({
#             'version': ecxf.version,
#             'fields': ecxf.docs(),
#         })
            
#         with open(options['outfile'], 'wb') as f:                    
#             if options['output_type'] == "html":
#                 f.write(html.encode('utf-8'))
#             else:
#                 f.write(html2pdf(html))

#----------------------------------------------------------New code ----------------------------------------------------------


from argparse import FileType

from django.core.management.base import BaseCommand, CommandError
from django.template.loader import get_template

from src.core.serializer.base import Serializer
from src.utils.pdfutils import html2pdf


class Command(BaseCommand):
    help = "Your command description"

    def add_arguments(self, parser):
        parser.add_argument('-o', '--outfile', type=FileType('wb'), help='output file', default=None)
        parser.add_argument('-t', '--output_type', choices=['html', 'pdf'], default='html',
                            help="one of 'html' or 'pdf'")

    def handle(self, *args, **options):
        if options['output_type'] not in ['html', 'pdf']:
            raise CommandError('Error: --type must be one of "html", "pdf"')
        if not options['outfile']:
            raise CommandError('Error: Outputfile "-o filename" must be specified')

        ecxf = Serializer()
        tpl = get_template('docs/ecx/base.html')
        html = tpl.render({
            'version': ecxf.version,
            'fields': ecxf.docs(),
        })

        with options['outfile'] as f:
            if options['output_type'] == "html":
                f.write(html.encode('utf-8'))
            else:
                f.write(html2pdf(html))
