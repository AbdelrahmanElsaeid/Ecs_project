from optparse import make_option
from django.core.management.base import BaseCommand
from src.core.models import Submission
from src.workflow.models import Graph

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--submission', '-s', dest='submission_pk', action='store', type='int', help="A submission id"),
    )

    def handle(self, submission_pk=None, **options):
        s = Submission.objects.get(id=submission_pk)
        print(s.ec_number, s.project_title)
        wf = Graph.objects.get().create_workflow(data=s)
        wf.start()
