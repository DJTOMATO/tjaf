import pathlib
import re

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

    def __str__(self):
        return f"VW({self.as_simple_str()})"

    def __repr__(self):
        return f"ValueWrapper({self.as_str()})"

class Tja():
    def __init__(self, text):
        self.text = text
        self.common_headers = {}
        self.headers = [{},{},{},{},{},{},{}]

        current_level = 3
        for line in text.splitlines():
            if re.match("^[a-zA-Z0-9]+:",line):
                key,value = line.split(":",1)
                if key not in ["COURSE","LEVEL","BALLOON","BALLOONNOR","BALLOONEXP","BALLOONMAS","SCOREINIT","SCOREDIFF","EXAM2"]:
                    header = (key,ValueWrapper(value))
                    self.common_headers.update([header])
                else:
                    if key == "COURSE":
                        levels = ["easy","normal","hard","oni","edit","tower","dan"]
                        if value.lower() in levels:
                            current_level = levels.index(value.lower())
                        elif value.isdigit():
                            current_level = ValueWrapper(value).as_int()

                    header = (key,ValueWrapper(value))
                    self.headers[current_level].update([header])
