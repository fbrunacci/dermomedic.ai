from json import JSONEncoder

class DictEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
