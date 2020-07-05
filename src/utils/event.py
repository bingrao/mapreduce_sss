import pickle


class MessageEvent:
    """
    Message Event format: {"Type": type, "Name": name, "Value": value}
    """
    def __init__(self):
        # Event Type
        self.type = EventType()

    @staticmethod
    def serialization(event, name, value):
        return pickle.dumps({"Type": event, "Name": name, "Value": value})

    @staticmethod
    def deserialization(message):
        return pickle.loads(message)


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
