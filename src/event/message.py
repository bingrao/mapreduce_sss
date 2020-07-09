class Message:
    def __init__(self, msgType, name, value):
        self.msgType = msgType
        self.name = name
        self.value = value


class DataMessage(Message):
    def __init__(self, msgType, name, value):
        super(DataMessage, self).__init__(msgType, name, value)
        pass


class ControlMessage(Message):
    def __init__(self, msgType, name, value):
        super(ControlMessage, self).__init__(msgType, name, value)
        pass
