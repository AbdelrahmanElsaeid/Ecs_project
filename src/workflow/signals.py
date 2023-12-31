from django.dispatch import Signal

workflow_started = Signal()
workflow_finished = Signal()
token_received = Signal()
token_consumed = Signal()
token_marked_deleted = Signal()
token_unlocked = Signal()
