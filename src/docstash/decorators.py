import uuid
from django.utils.functional import wraps
from django.shortcuts import redirect, get_object_or_404

from src.docstash.models import DocStash


def with_docstash(group=None):
    def _decorator(view):
        # if group != None:
        view_name1 = '.'.join((view.__module__, view.__name__))
        parts = view_name1.split('.')
        app_name = parts[1]  # Assuming the app name is the second part
        fun_name = parts[-1]  # Assuming the view name is the last part

        # Create the URL pattern in the format 'app_name:view_name'
        view_name = f'{app_name}:{fun_name}'
        # else:
            # view_name = group
        @wraps(view)
        def _inner(request, docstash_key=None, **kwargs):
            if not docstash_key:
                docstash = DocStash.objects.create(group=view_name, owner=request.user)
                #return redirect('core:create_submission_form', docstash_key=docstash.key, **kwargs)
                return redirect(view_name, docstash_key=docstash.key, **kwargs)
                #return redirect('notifications:create_notification', docstash_key=docstash.key, **kwargs)

            docstash = get_object_or_404(DocStash, group=view_name,
                owner=request.user, key=docstash_key)
            request.docstash = docstash
            return view(request, **kwargs)

        return _inner

    return _decorator

#create_notification


