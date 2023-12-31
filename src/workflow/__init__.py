# import imp
# from importlib import import_module
# import django
# # django.setup()
# from django.conf import settings
# from django.dispatch import receiver
# from django.db.models.signals import post_save, class_prepared
# from django.db.models import Model
# from django.contrib.contenttypes.models import ContentType

# from src.workflow.controllers import Activity, FlowController, guard

# __all__ = ('Activity', 'FlowController', 'NodeController', 'register', 'guard', 'autostart_disabled')

# _registered_models = {}
# _autostart_disabled = False

# def register(model, autostart_if=None):
#     if model in _registered_models:
#         return
#     _registered_models[model] = autostart_if or (lambda obj, created: created)
#     from workflow.descriptors import WorkflowDescriptor
#     model.workflow = WorkflowDescriptor()
    
# def autodiscover():
#     import workflow.patterns
#     for app in settings.INSTALLED_APPS:
#         try:
#             app_path = import_module(app).__path__
#         except AttributeError:
#             continue
#         try:
#             imp.find_module('workflow', app_path)
#         except ImportError:
#             continue
#         module = import_module("%s.workflow" % app)

# @receiver(post_save)
# def _post_save(sender, **kwargs):
#     if _autostart_disabled or sender not in _registered_models:
#         return
#     autostart_if = _registered_models[sender]
#     obj = kwargs['instance']
#     # XXX: 'raw' is passed during fixture loading, but that's an undocumented feature - see django bug #13299 (FMD1)
#     if not kwargs.get('raw') and autostart_if(obj, kwargs['created']):
#         from workflow.models import Workflow, Graph
#         cts = [ContentType.objects.get_for_model(cls) for cls in sender.__mro__ if issubclass(cls, Model) and cls != Model and not cls._meta.abstract]
#         graphs = Graph.objects.filter(content_type__in=cts, auto_start=True)
#         for graph in graphs:
#             wf = graph.create_workflow(data=obj)
#             wf.start()


# # HACK
# import warnings
# from contextlib import contextmanager

# @contextmanager
# def autostart_disabled():
#     warnings.warn("Disabling workflow autostart is not thread safe", UserWarning, stacklevel=2)
#     globals()['_autostart_disabled'] = True
#     yield
#     globals()['_autostart_disabled'] = False


# default_app_config = 'ecs.workflow.apps.WorkflowAppConfig'