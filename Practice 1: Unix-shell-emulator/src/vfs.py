class VFS:
    """Виртуальная файловая система (в разработке)"""

    def __init__(self):
        self.current_path = "/"
        self.name = "VFS"

    def get_current_path(self):
        return self.current_path

    def set_current_path(self, path):
        self.current_path = path