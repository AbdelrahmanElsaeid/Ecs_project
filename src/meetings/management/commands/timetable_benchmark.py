import datetime, timeit, csv, os
from django.core.management.base import BaseCommand
from django.db import transaction

from django.contrib.auth.models import User
from src.meetings.models import Meeting

from src.utils.genetic_sort import GeneticSorter, inversion_mutation, swap_mutation, displacement_mutation


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, **options):
        submission_data = {}

        meeting = Meeting.objects.create(start=datetime.datetime(2010, 4, 13, 10), title="Test")
        entries_by_title = {}
        for name, submissions, comments in csv.reader(open(os.path.join(os.path.dirname(__file__), 'data', 'meeting100413.csv'), 'r'), delimiter=',', quotechar='"'):
            user = User.objects.create(username=name)
            for submission in submissions.split(','):
                title = "".join(submission.strip().split()[:1])
                if title in entries_by_title:
                    entry = entries_by_title[title]
                else:
                    entry = meeting.add_entry(title=title, duration=datetime.timedelta(minutes=10))
                    entries_by_title[title] = entry
                entry.participations.create(user=user)
        #print len(entries_by_title)

        setup = 'from meetings.models import Meeting;m = Meeting.objects.get(pk=%s);f = m.create_evaluation_func(lambda x: x);perm=list(m)' % meeting.pk
        print("%.3fms per metric constructor" % (timeit.timeit('f(perm)', setup, number=1000)))
        
        setup = 'from utils.genetic_sort import order_crossover'
        print("%.3fms per order_crossover" % (timeit.timeit('order_crossover((1,2,3,4,5,6,7,8,9), (9,8,7,6,5,4,3,2,1))', setup, number=1000)))

        setup = 'from utils.genetic_sort import swap_mutation'
        print("%.3fms per swap_mutuation" % (timeit.timeit('swap_mutation((1,2,3,4,5,6,7,8,9))', setup, number=1000)))
        
        setup = 'from utils.genetic_sort import inversion_mutation'
        print("%.3fms per swap_mutuation" % (timeit.timeit('inversion_mutation((1,2,3,4,5,6,7,8,9))', setup, number=1000)))
        
        setup = 'from utils.genetic_sort import displacement_mutation'
        print("%.3fms per displacement_mutation" % (timeit.timeit('displacement_mutation((1,2,3,4,5,6,7,8,9))', setup, number=1000)))
        
        get_metrics = meeting.create_evaluation_func(lambda x: x)
        evalf = meeting.create_evaluation_func(lambda metrics: 1000*1000 * (10.0 / (metrics._waiting_time_total + 1) + 0 / (metrics._waiting_time_max + 1)))
        entries, users = meeting.timetable
        sorter = GeneticSorter(entries, evalf, population_size=100, crossover_p=0.3, mutations={
            inversion_mutation: 0.002,
            swap_mutation: 0.02,
            displacement_mutation: 0.01,
        })
        print("===" * 25)
        try:
            for i in range(1000):
                result = sorter.run(5)
                metrics = get_metrics(result)
                if not i % 10:
                    print("%4s %8s %8s %8s %8s %8s %8s %4s %10s" % (
                        'gen', 'sum', 'avg', 'min', 'max', 'base', 'value', 'pop', 'secs/gen',
                    ))
                print("%4d %8d %8d %8d %8d %8d %8d %4d %10.4f" % (
                    sorter.generation_count, 
                    int(metrics.waiting_time_total.total_seconds() / 60),
                    int(metrics.waiting_time_avg.total_seconds() / 60),
                    int(metrics.waiting_time_min.total_seconds() / 60),
                    int(metrics.waiting_time_max.total_seconds() / 60),
                    int(evalf(entries)), 
                    int(evalf(result)), 
                    len(sorter.population),
                    sorter.time_per_generation
                ))
        except KeyboardInterrupt:
            pass

        transaction.set_rollback(True)
