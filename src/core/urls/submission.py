from src.core.views import submissions as views
from src.tasksv.views import task_backlog, delete_task
from src.communication.views import new_thread
#----------------------new---------------

from django.contrib import admin
from django.urls import path , include, re_path
from django.conf.urls.static import static
from django.conf import settings

# app_name = 'core'  




urlpatterns = [
    re_path(r'^(?P<submission_pk>\d+)/tasks/log/$', task_backlog, name='task_backlog'),
    re_path(r'^(?P<submission_pk>\d+)/task/(?P<task_pk>\d+)/delete/$', delete_task, name='delete_task'),

    re_path(r'^(?P<submission_pk>\d+)/messages/new/$', new_thread, name='new_thread'),

    re_path(r'^list/all/$', views.all_submissions, name='all_submissions'),
    re_path(r'^list/xls/$', views.xls_export, name='xls_export'),
    re_path(r'^list/xls/(?P<shasum>[0-9a-f]{40})/$', views.xls_export_download, name='xls_export_download'),
    re_path(r'^list/assigned/$', views.assigned_submissions, name='assigned-submissions'),
    re_path(r'^list/mine/$', views.my_submissions, name='my_submissions'),

    re_path(r'^import/$', views.import_submission_form, name='import_submission_form'),
    re_path(r'^new/(?:(?P<docstash_key>.+)/)?$', views.create_submission_form, name='create_submission_form'),
    re_path(r'^delete/(?P<docstash_key>.+)/$', views.delete_docstash_entry, name='delete_docstash_entry'),
    re_path(r'^doc/upload/(?P<docstash_key>.+)/$', views.upload_document_for_submission, name='upload_document_for_submission'),
    re_path(r'^doc/delete/(?P<docstash_key>.+)/$', views.delete_document_from_submission, name='delete_document_from_submission'),

    re_path(r'^diff/forms/(?P<old_submission_form_pk>\d+)/(?P<new_submission_form_pk>\d+)/$', views.diff, name='diff'),

    re_path(r'^(?P<submission_pk>\d+)/$', views.view_submission, name='view_submission'),
    re_path(r'^(?P<submission_pk>\d+)/copy/$', views.copy_latest_submission_form, name='copy_latest_submission_form'),
    re_path(r'^(?P<submission_pk>\d+)/amend/(?P<notification_type_pk>\d+)/$', views.copy_latest_submission_form, name='amend_submission_form'),
    re_path(r'^(?P<submission_pk>\d+)/export/$', views.export_submission, name='export_submission'),
    re_path(r'^(?P<submission_pk>\d+)/presenter/change/$', views.change_submission_presenter, name='change_submission_presenter'),
    re_path(r'^(?P<submission_pk>\d+)/susar_presenter/change/$', views.change_submission_susar_presenter, name='change_submission_susar_presenter'),

    re_path(r'^(?P<submission_pk>\d+)/temp-auth/grant/$', views.grant_temporary_access, name='grant_temporary_access'),
    re_path(r'^(?P<submission_pk>\d+)/temp-auth/(?P<temp_auth_pk>\d+)/revoke/$', views.revoke_temporary_access, name='revoke_temporary_access'),
    re_path(r'^(?P<submission_pk>\d+)/review/checklist/(?P<blueprint_pk>\d+)/reopen/$', views.reopen_checklist, name='reopen_checklist'),

    re_path(r'^form/(?P<submission_form_pk>\d+)/$', views.readonly_submission_form, name='readonly_submission_form'),
    re_path(r'^form/(?P<submission_form_pk>\d+)/pdf/$', views.submission_form_pdf, name='submission_form_pdf'),
    re_path(r'^form/(?P<submission_form_pk>\d+)/pdf/view/$', views.submission_form_pdf_view, name='submission_form_pdf_view'),
    re_path(r'^form/(?P<submission_form_pk>\d+)/doc/(?P<document_pk>\d+)/$', views.download_document, name='download_document'),
    re_path(r'^form/(?P<submission_form_pk>\d+)/doc/(?P<document_pk>\d+)/view/$', views.view_document, name='view_document'),
    re_path(r'^form/(?P<submission_form_pk>\d+)/copy/$', views.copy_submission_form, name='copy_submission_form'),
    re_path(r'^form/(?P<submission_form_pk>\d+)/amend/(?P<notification_type_pk>\d+)/$', views.copy_submission_form, name='amend_submission_form'),
    re_path(r'^form/(?P<submission_form_pk>\d+)/review/checklist/(?P<blueprint_pk>\d+)/$', views.checklist_review, name='checklist_review'),
    re_path(r'^form/(?P<submission_form_pk>\d+)/review/checklist/show/(?P<checklist_pk>\d+)/$', views.show_checklist_review, name='show_checklist_review'),
    re_path(r'^form/(?P<submission_form_pk>\d+)/review/checklist/drop/(?P<checklist_pk>\d+)/$', views.drop_checklist_review, name='drop_checklist_review'),
    re_path(r'^(?P<submission_pk>\d+)/categorization/$', views.categorization, name='categorization'),
    re_path(r'^(?P<submission_pk>\d+)/categorization/reopen/$', views.reopen_categorization, name='reopen_categorization'),
    re_path(r'^(?P<submission_pk>\d+)/review/categorization/$', views.categorization_review, name='categorization_review'),
    re_path(r'^form/(?P<submission_pk>\d+)/review/initial/$', views.initial_review, name='initial_review'),
    re_path(r'^form/(?P<submission_pk>\d+)/review/paper_submission/$', views.paper_submission_review, name='paper_submission_review'),
    re_path(r'^form/(?P<submission_pk>\d+)/biased/$', views.biased_board_members, name='biased_board_members'),
    re_path(r'^form/(?P<submission_pk>\d+)/biased/remove/(?P<user_pk>\d+)/$', views.remove_biased_board_member, name='remove_biased_board_member'),
    re_path(r'^form/(?P<submission_form_pk>\d+)/review/vote/$', views.vote_review, name='vote_review'),
    re_path(r'^form/(?P<submission_form_pk>\d+)/vote/prepare/$', views.vote_preparation, name='vote_preparation'),
    re_path(r'^form/(?P<submission_form_pk>\d+)/vote/prepare/$', views.vote_preparation, name='vote_preparation'),
    re_path(r'^form/(?P<submission_form_pk>\d+)/vote/b2-prepare/$', views.b2_vote_preparation, name='b2_vote_preparation'),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^form/(?P<submission_form_pk>\d+)/pdf/debug/$', views.submission_form_pdf_debug, name='submission_form_pdf_debug'),
    ]
