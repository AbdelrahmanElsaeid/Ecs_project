from django.urls import path, re_path

from src.billing import views

app_name='billing'




urlpatterns = [
    path('submissions/', views.submission_billing, name='submission_billing'),
    re_path(r'^invoice/(?P<invoice_pk>\d+)/$', views.view_invoice, name='view_invoice'),
    re_path(r'^invoice/(?P<invoice_pk>\d+)/pdf/$', views.invoice_pdf, name='invoice_pdf'),
    path('invoices/', views.invoice_list, name='invoice_list'),

    path('external_review/', views.external_review_payment, name='external_review_payment'),
    re_path(r'^payment/(?P<payment_pk>\d+)/$', views.view_checklist_payment, name='view_checklist_payment'),
    re_path(r'^payment/(?P<payment_pk>\d+)/pdf/$', views.checklist_payment_pdf, name='checklist_payment_pdf'),
    path('payments/', views.checklist_payment_list, name='checklist_payment_list'),
]
