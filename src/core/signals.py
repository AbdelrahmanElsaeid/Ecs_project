from django.dispatch import Signal

on_study_change = Signal() # sender=Submission, kwargs: submission, old_form, new_form
on_study_submit = Signal() # sender=Submission, kwargs: submission, form, user
on_presenter_change = Signal() # sender=Submission, kwargs: submission, old_presenter, new_presenter
on_susar_presenter_change = Signal() # sender=Submission, kwargs: submission, old_susar_presenter, new_susar_presenter
on_initial_review = Signal() # sender=Submission, kwargs: submission, form
on_categorization = Signal() # sender=Submission, kwargs: submission
