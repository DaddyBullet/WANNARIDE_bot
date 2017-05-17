

class Wonnarider(object):
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.ride_type = None
        self.start_time = None
        self.exp_time = None
        self.location = None
        self.radius = None

    def quitQueue(self):
        pass

    def findWonnariders(self):
        pass

    def sendWonnariders(self):
        pass

    def setRideType(self, rt):
        self.ride_type = rt

    def setLocation(self):
        pass

    def setRadius(self, r):
        self.radius = r

    def setExpTime(self):
        pass

    def reenterQueue(self):
        pass