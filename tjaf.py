import pathlib

class ValueWrapper():
    def __init__(self, value):
        self.value = value

    def as_str(self):
        return str(self.value)

    def as_file_ext(self):
        path_str = self.as_str()
        path = pathlib.Path(path_str)
        return path.suffix.split(".",1)[1]

    def as_simple_str(self):
        raw = self.as_str()
        no_comment = raw.split("//",1)[0]
        return no_comment.strip()

    def as_int(self):
        return int(self.as_simple_str() or 0)

    def as_float(self):
        return float(self.as_simple_str() or 0)
