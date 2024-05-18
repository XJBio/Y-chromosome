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


def join_and_make_path(dir_path, name):
    check_and_make_path(dir_path)
    check_and_make_path(join_path(dir_path, name))
    return join_path(dir_path, name)

