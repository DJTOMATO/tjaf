import pathlib
import re
import argparse
import json

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
    def __init__(self, path, encoding="UTF-8", a=False):
        self.text = pathlib.Path(path).read_text(encoding=encoding)
        self.common_headers = {}
        self.headers = [{},{},{},{},{},{},{}]
        self.humen_list = [[],[],[],[],[],[],[]]

        current_level = 3
        for line in self.text.splitlines():
            if re.match("^[a-zA-Z0-9]+:",line):
                key,value = line.split(":",1)
                if key not in ["COURSE","LEVEL","BALLOON","BALLOONNOR","BALLOONEXP","BALLOONMAS","SCOREINIT","SCOREDIFF","EXAM2"]:
                    header = (key,ValueWrapper(value))
                    self.common_headers.update([header])
                else:
                    if key == "COURSE" and (any(h != [] for h in self.humen_list) or not a):
                        levels = ["easy","normal","hard","oni","edit","tower","dan"]
                        if value.lower() in levels:
                            current_level = levels.index(value.lower())
                        elif value.isdigit():
                            current_level = ValueWrapper(value).as_int()

                    header = (key,ValueWrapper(value))
                    self.headers[current_level].update([header])
            elif line:
                self.humen_list[current_level].append(line)

    def has_branch(self, level):
        return any(h.split(" ",1)[0] == "#BRANCHSTART" for h in self.humen_list[level])

    def has_lyrics(self):
        return any(h.split(" ",1)[0] == "#LYRIC" for h in sum(self.humen_list[:5],[]))

    def to_mongo(self, song_id, order, a=False):
        title = self.common_headers["TITLE"].as_str()
        subtitle = None
        if "SUBTITLE" in self.common_headers:
            subtitle = self.common_headers["SUBTITLE"].as_str()
            if subtitle.startswith("--"):
                subtitle = subtitle.split("--",1)[1]
        level_names = ["easy","normal","hard","oni","ura"]
        preview = None
        if "DEMOSTART" in self.common_headers:
            preview = self.common_headers["DEMOSTART"].as_float()

        return {
            "title_lang": {
                "ja": title,
                "en": None,
                "cn": None,
                "tw": None,
                "ko": None
            },
            "subtitle_lang": {
                "ja": subtitle,
                "en": None,
                "cn": None,
                "tw": None,
                "ko": None
            },
            "courses": {
                level_names[level]: {
                    "stars": self.headers[level]["LEVEL"].as_float() if a else self.headers[level]["LEVEL"].as_int(),
                    "branch": self.has_branch(level)
                } if self.humen_list[level] != [] else None for level in range(5)
            },
            "enabled": True,
            "title": title,
            "subtitle": subtitle,
            "category_id": None,
            "type": "tja",
            "music_type": self.common_headers["WAVE"].as_file_ext(),
            "offset": -0.01,
            "skin_id": None,
            "preview": preview,
            "volume": 1,
            "maker_id": None,
            "lyrics": self.has_lyrics(),
            "hash": "",
            "id": song_id,
            "order": order
        }

def parse_args():
    parser = argparse.ArgumentParser(description='Process some options for tjaf.py')
    parser.add_argument('--make-songs-db', action='store_true')
    parser.add_argument('--songs-dir')
    parser.add_argument('--json-path')
    parser.add_argument('--float-stars', action='store_true', default=False)
    parser.add_argument('--skip-first-course-header', action='store_true', default=False)
    return parser.parse_args()

def app(args):
    if not args.make_songs_db:
        print("Example usage:\n$ python tjaf.py --make-songs-db --songs-dir songs --json-path test.json --float-stars --skip-first-course-header")
        return

    db = []

    for order, path in enumerate(sorted(pathlib.Path(args.songs_dir).rglob("*.tja"))):
        tja = Tja(path, a=args.skip_first_course_header)
        id = path.parent.name
        if id.isdigit():
            id = int(id)
        mongo = tja.to_mongo(id, order, a=args.float_stars)
        db += [ mongo ]

    pathlib.Path(args.json_path).write_text(json.dumps(db), encoding="UTF-8")

if __name__ == "__main__":
    app(parse_args())
