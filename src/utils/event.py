import json


def message_encode(event, name, value):
    return json.dumps({"Type": event, "Name": name, "Value": bin(value)})


def message_decode(message):
    return json.loads(message)


class EventType:
    def __init__(self):
        self.data = "Data"
        self.add = "Add"
        self.sub = "Sub"
        self.mul = "Multiply"
        self.match = "Match"
        self.count = "Count"
        self.select = "Select"
        self.join = "Join"
        self.search = "Range_Search"
