from django.contrib.auth.models import Group
from src.utils import Args, camel_split
from src.workflow.models import Graph, Node, Edge
from src.tasksv.models import TaskType
from copy import deepcopy

def workflow_graph_needs_upgrade(graph, nodes, edges):
    existing_nodes = {}
    nodes = deepcopy(nodes)
    for name, args in nodes.items():
        args.setdefault('uid', name)
        args.pop('group', None)
        try:
            existing_nodes[name] = args.apply(graph.get_node)
        except (Node.DoesNotExist, Node.MultipleObjectsReturned):
            return True
    edges = deepcopy(edges)
    for node_names, args in edges:
        if not args:
            args = Args()
        from_name, to_name = node_names
        args.update(existing_nodes[to_name])
        try:
            args.apply(existing_nodes[from_name].get_edge)
        except Edge.DoesNotExist:
            return True
    return False


def setup_workflow_graph(model, nodes=None, edges=None, force=True, **kwargs):
    """
    created a new workflow graph if a graph with the same structure does not already exists. 
    old graphs will loose their auto_start=True flag.
    """
    if isinstance(edges, dict):
        edges = edges.items()
    try:
        graph, created = Graph.objects.get_or_create(model=model, **kwargs)
    except Graph.MultipleObjectsReturned:
        raise ValueError("There is more than one graph for %s with %s" % (model, kwargs))
    if not created:
        # FIXME: workflow_graph_needs_upgrade is broken because it alters the Args instance.
        if not force and not workflow_graph_needs_upgrade(graph, nodes, edges):
            return False
        graph.auto_start = False
        graph.save()
        graph = Graph.objects.create(model=model, **kwargs)
    
    node_instances = {}
    for name, args in nodes.items():
        args.setdefault('name', " ".join(camel_split(args[0].__name__)))
        args.setdefault('uid', name)
        group = args.pop('group', None)
        is_delegatable = args.pop('is_delegatable', None)
        is_dynamic = args.pop('is_dynamic', None)
        node = args.apply(graph.create_node)
        node_instances[name] = node
        if group:
            task_type = TaskType.objects.get(workflow_node=node)
            task_type.group = Group.objects.get(name=group)
            task_type.save()
        if not is_delegatable is None:
            task_type = TaskType.objects.get(workflow_node=node)
            task_type.is_delegatable = is_delegatable
            task_type.save()
        if not is_dynamic is None:
            task_type = TaskType.objects.get(workflow_node=node)
            task_type.is_dynamic = is_dynamic
            task_type.save()
    for node_names, args in edges:
        if not args:
            args = Args()
        from_name, to_name = node_names
        args.update(node_instances[to_name])
        args.apply(node_instances[from_name].add_edge)
    return True
