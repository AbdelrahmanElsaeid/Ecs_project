from django.shortcuts import render

# Create your views here.


import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import traceback
import logging
import sys
import hashlib
import uuid

from tempfile import TemporaryFile

from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.shortcuts import render, redirect

from src.utils import forceauth

from src.users.utils import sudo, user_group_required
from src.documents.models import Document
from src.utils.pdfutils import pdf_barcodestamp
from src.tasksv.models import Task

from src.signature.utils import SigningData, with_sign_data, get_pdfas_url


logger = logging.getLogger(__name__)


def _get_tasks(user):
    return Task.objects.for_user(user).filter(closed_at=None, assigned_to=user)

def _store_sign_data(sign_data, force_mock=False):
    sign_data = SigningData(sign_data)

    if sign_data['document_barcodestamp']:
        with TemporaryFile() as tmp_in:
            tmp_in.write(sign_data['pdf_data'])
            tmp_in.seek(0)
            stamped = pdf_barcodestamp(tmp_in, sign_data['document_uuid'])
            sign_data['pdf_data'] = stamped.read()

    sign_data['origdigest'] = hashlib.sha256(sign_data['pdf_data']).hexdigest()
    sign_data.store(minutes=5)
    return sign_data


@user_group_required("EC-Signing")
def init_batch_sign(request, task, data_func):
    if request.user.email.startswith('signing_mock') or settings.PDFAS_SERVICE == 'mock:':
        sign_data = data_func(request, task)
        rval = sign(request, sign_data)
        _get_tasks(request.user).get(pk=task.pk).done(choice=True)
        return rval
    tasks = [task.pk]
    tasks += list(_get_tasks(request.user).filter(task_type__workflow_node__uid=task.task_type.workflow_node.uid).exclude(pk=task.pk).order_by('created_at').values_list('pk', flat=True))
    sign_session = SigningData(tasks=tasks, data_func=data_func)
    sign_session.store(hours=1)
    return redirect('signature:batch_sign', sign_session_id=sign_session.id)


@user_group_required("EC-Signing")
@with_sign_data(data=False, session=True)
def batch_sign(request):
    tasks = request.sign_session['tasks']
    if not tasks:
        return redirect('dashboard:view_dashboard')

    task = _get_tasks(request.user).get(pk=tasks[0])
    data = request.sign_session['data_func'](request, task)
    data['sign_session_id'] = request.sign_session.id
    sign_data = _store_sign_data(data)

    if request.user.email.startswith('signing_fail'):
        return sign_error(request, pdf_id=sign_data.id, error='forced failure', cause='requested force_fail, so we failed')

    return render(request, 'signature/batch.html', {
        'sign_url': get_pdfas_url(request, sign_data),
        'pdf_id': sign_data.id,
    })


@user_group_required("EC-Signing")
@with_sign_data(session=True)
def batch_action(request, action=None):
    request.sign_data.delete()

    if action in ['skip', 'pushback']:
        task_pk = request.sign_session.pop_listitem('tasks', 0)
        task = _get_tasks(request.user).get(pk=task_pk)
        if action == 'pushback' and task:
            task.done(choice=False)
            with sudo():
                previous_task = task.trail.closed().exclude(pk=task.pk).order_by('-closed_at')[0]
                new_task = previous_task.reopen()
                new_task.review_for = previous_task.review_for
                new_task.save()
    elif action == 'cancel':
        request.sign_session.delete()

    url = reverse('dashboard:view_dashboard')
    if action in ['retry', 'skip', 'pushback']:
        url = reverse('signature:batch_sign', kwargs={'sign_session_id': request.sign_session.id})
    return redirect(url)


@user_group_required("EC-Signing")
def sign(request, sign_data, force_mock=False, force_fail=False):
    fail = force_fail or request.user.email.startswith('signing_fail')
    mock = force_mock or request.user.email.startswith('signing_mock') or settings.PDFAS_SERVICE == 'mock:'

    sign_data = _store_sign_data(sign_data)

    if fail:
        return sign_error(request, pdf_id=sign_data.id, error='forced failure', cause='requested force_fail, so we failed')
    elif mock:
        return sign_receive(request, pdf_id=sign_data.id, mock=mock)

    url = get_pdfas_url(request, sign_data)
    return redirect(url)

# FIXME allow only from same host as server
@csrf_exempt
@forceauth.exempt
@with_sign_data()
def sign_send(request):
    return HttpResponse(request.sign_data["pdf_data"], content_type='application/pdf')

@user_group_required("EC-Signing")
@with_sign_data()
def sign_preview(request):
    return HttpResponse(request.sign_data["html_preview"])

@user_group_required("EC-Signing")
@csrf_exempt
@with_sign_data()
def sign_receive(request, mock=False):
    ''' accessed by pdf-as when the pdf has been successfully signed '''
    try:
        with transaction.atomic():
            if mock:
                pdfurl_str = "mock:"
                pdf_data = request.sign_data['pdf_data']
            else:
                pdfurl_str = urllib.parse.unquote(request.GET['pdfurl'])
                if not pdfurl_str.startswith(settings.PDFAS_SERVICE):
                    raise RuntimeError("pdfurl does not start with settings.PDFAS_SERVICE: {0} != {1}".format(settings.PDFAS_SERVICE, pdfurl_str))
                sock_pdfas = urllib.request.urlopen(pdfurl_str)
                # TODO: verify "ValueCheckCode" and "CertificateCheckCode" in http header
                # ValueCheckCode= 0 => ok, 1=> err, CertificateCheckCode=0 => OK, 2-5 Verify Error, 99 Other verify Error, raise exception if verify fails
                pdf_data = sock_pdfas.read(int(request.GET['pdflength']))

            document = Document.objects.create_from_buffer(pdf_data,
                uuid=uuid.UUID(request.sign_data["document_uuid"]),
                stamp_on_download=False, doctype=request.sign_data['document_type'],
                original_file_name=request.sign_data["document_filename"],
                version=request.sign_data["document_version"]
            )
            parent_model = request.sign_data.get('parent_type')
            if parent_model:
                document.parent_object = parent_model.objects.get(pk=request.sign_data['parent_pk'])
                document.save()

            # called unconditionally, because the function can have side effects
            url = request.sign_data['success_func'](request, document=document)

            if request.sign_session:
                task_pk = request.sign_session.pop_listitem('tasks', 0)
                _get_tasks(request.user).get(pk=task_pk).done(choice=True)
            document = Document.objects.get(pk=document.pk)

    except Exception as e:
        logger.warn('Signing Error', exc_info=sys.exc_info())
        return sign_error(request, pdf_id=request.sign_data.id, error=repr(e)+ " url: {0}".format(pdfurl_str), cause=traceback.format_exc())

    else:
        request.sign_data.delete()
        if request.sign_session:
            url = reverse('signature:batch_sign', kwargs={'sign_session_id': request.sign_session.id})
        return redirect(url)


@user_group_required("EC-Signing")
@csrf_exempt
@with_sign_data()
def sign_error(request, error=None, cause=None):
    ''' accessed by pdf-as and our own code when an error occured '''
    error = error or urllib.parse.unquote_plus(request.GET.get('error', ''))
    cause = cause or urllib.parse.unquote_plus(request.GET.get('cause', ''))

    if request.sign_session is None:
        return HttpResponse('signing failed\n\nerror: {0}\ncause:\n{1}'.format(error, cause), content_type='text/plain')

    return render(request, 'signature/error.html', {
        'pdf_id': request.sign_data.id,
        'error': error,
        'cause': cause,
    })