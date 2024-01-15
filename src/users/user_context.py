from threading import local

class UserContext(local):
    def __init__(self):
        self.current_user = None

current_user_store = UserContext()