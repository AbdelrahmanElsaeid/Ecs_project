from django.urls import path,re_path

from src.meetings import views
app_name = 'meetings'




urlpatterns = [
    re_path(r'^reschedule/submission/(?P<submission_pk>\d+)/$', views.reschedule_submission, name='reschedule_submission'),

    re_path(r'^new/$', views.create_meeting, name='create_meeting'),
    re_path(r'^next/$', views.next, name='next'),
    re_path(r'^list/upcoming/$', views.upcoming_meetings, name='upcoming_meetings'),
    re_path(r'^list/past/$', views.past_meetings, name='past_meetings'),
    re_path(r'^(?P<meeting_pk>\d+)/$', views.meeting_details, name='meeting_details'),
    re_path(r'^(?P<meeting_pk>\d+)/constraints_for_user/(?P<user_pk>\d+)/$', views.edit_user_constraints, name='edit_user_constraints'),
    re_path(r'^(?P<meeting_pk>\d+)/edit/$', views.edit_meeting, name='edit_meeting'),
    re_path(r'^(?P<meeting_pk>\d+)/open_tasks/$', views.open_tasks, name='open_tasks'),
    re_path(r'^(?P<meeting_pk>\d+)/submissions/$', views.submission_list, name='submission_list'),
    re_path(r'^(?P<meeting_pk>\d+)/notifications/$', views.notification_list, name='notification_list'),
    re_path(r'^(?P<meeting_pk>\d+)/document/(?P<document_pk>\d+)/$', views.download_document, name='download_document'),
    re_path(r'^(?P<meeting_pk>\d+)/document/(?P<document_pk>\d+)/view/$', views.view_document, name='view_document'),
    re_path(r'^(?P<meeting_pk>\d+)/documents/zip/$', views.download_zipped_documents, name='download_zipped_documents'),
    re_path(r'^(?P<meeting_pk>\d+)/documents/(?P<submission_pk>\d+)/zip/$', views.download_zipped_documents, name='download_zipped_submission_documents'),

    re_path(r'^(?P<meeting_pk>\d+)/timetable/$', views.timetable_editor, name='timetable_editor'),
    re_path(r'^(?P<meeting_pk>\d+)/timetable/optimize/(?P<algorithm>random|brute_force|ga)/$', views.optimize_timetable, name='optimize_timetable'),
    re_path(r'^(?P<meeting_pk>\d+)/timetable/optimize/(?P<algorithm>random|brute_force|ga)/long/$', views.optimize_timetable_long, name='optimize_timetable_long'),
    re_path(r'^(?P<meeting_pk>\d+)/timetable/entry/new/$', views.add_timetable_entry, name='add_timetable_entry'),
    re_path(r'^(?P<meeting_pk>\d+)/timetable/entry/add/$', views.add_free_timetable_entry, name='add_free_timetable_entry'),
    re_path(r'^(?P<meeting_pk>\d+)/timetable/entry/move/$', views.move_timetable_entry, name='move_timetable_entry'),
    re_path(r'^(?P<meeting_pk>\d+)/timetable/entry/(?P<entry_pk>\d+)/delete/$', views.remove_timetable_entry, name='remove_timetable_entry'),
    re_path(r'^(?P<meeting_pk>\d+)/timetable/entry/(?P<entry_pk>\d+)/update/$', views.update_timetable_entry, name='update_timetable_entry'),
    re_path(r'^(?P<meeting_pk>\d+)/timetable/entry/(?P<entry_pk>\d+)/users/(?P<user_pk>\d+)/toggle/$', views.toggle_participation, name='toggle_participation'),

    re_path(r'^(?P<meeting_pk>\d+)/assistant/$', views.meeting_assistant, name='meeting_assistant'),
    re_path(r'^(?P<meeting_pk>\d+)/assistant/start/$', views.meeting_assistant_start, name='meeting_assistant_start'),
    re_path(r'^(?P<meeting_pk>\d+)/assistant/stop/$', views.meeting_assistant_stop, name='meeting_assistant_stop'),
    re_path(r'^(?P<meeting_pk>\d+)/assistant/(?P<top_pk>\d+)/$', views.meeting_assistant_top, name='meeting_assistant_top'),
    re_path(r'^(?P<meeting_pk>\d+)/assistant/quickjump/$', views.meeting_assistant_quickjump, name='meeting_assistant_quickjump'),
    re_path(r'^(?P<meeting_pk>\d+)/assistant/comments/$', views.meeting_assistant_comments, name='meeting_assistant_comments'),
    re_path(r'^(?P<meeting_pk>\d+)/assistant/other_tops/$', views.meeting_assistant_other_tops, name='meeting_assistant_other_tops'),

    # re_path(r'^(?P<meeting_pk>\d+)/agenda/pdf/$', views.agenda_pdf, name='agenda_pdf'),
    path('<int:meeting_pk>/agenda/pdf/', views.agenda_pdf, name='agenda_pdf'),
    re_path(r'^(?P<meeting_pk>\d+)/agenda/send/$', views.send_agenda_to_board, name='send_agenda_to_board'),
    re_path(r'^(?P<meeting_pk>\d+)/expedited_reviewer_invitations/send/$', views.send_expedited_reviewer_invitations, name='send_expedited_reviewer_invitations'),
    re_path(r'^(?P<meeting_pk>\d+)/timetable_pdf/$', views.timetable_pdf, name='timetable_pdf'),
    re_path(r'^(?P<meeting_pk>\d+)/timetablepart/$', views.timetable_htmlemailpart, name='timetable_htmlemailpart'),
    re_path(r'^(?P<meeting_pk>\d+)/protocol/edit/$', views.edit_protocol, name='edit_protocol'),
    re_path(r'^(?P<meeting_pk>\d+)/protocol/pdf/render/$', views.render_protocol_pdf, name='render_protocol_pdf'),
    re_path(r'^(?P<meeting_pk>\d+)/protocol/pdf/$', views.protocol_pdf, name='protocol_pdf'),
    re_path(r'^(?P<meeting_pk>\d+)/protocol/send/$', views.send_protocol, name='send_protocol'),
]
