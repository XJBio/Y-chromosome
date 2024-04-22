import os


def check_path(path):
    if not os.path.exists(path):
        return False
    return True


def check_and_make_path(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        return False
    return True


def join_path(dir_path, name):
    return os.path.join(dir_path, name)
