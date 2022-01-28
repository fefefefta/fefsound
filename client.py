class Client:
    def __init__(self):
        self.login = None
        self.is_accessed = False

    def set_login(self, login):
        self.login = login

    def make_access(self):
        self.is_accessed = True

    def get_login(self):
        return self.login

    def get_is_accessed(self):
        return self.is_accessed