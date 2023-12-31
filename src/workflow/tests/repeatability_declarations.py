from src.workflow import Activity, register
from src.workflow.tests.models import Foo

register(Foo)


class A(Activity):
    class Meta:
        model = Foo

class B(Activity):
    def is_repeatable(self):
        return True

    class Meta:
        model = Foo

class C(Activity):
    class Meta:
        model = Foo

class D(Activity):
    def is_reentrant(self):
        return False

    class Meta:
        model = Foo

class E(Activity):
    class Meta:
        model = Foo
