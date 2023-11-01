import time

class Message:
    def __init__ (self, thread, user, text, timestamp = None):
        self.thread = thread
        self.timestamp = timestamp or time.time()
        self.user = user
        self.text = text

    def as_dict (self):
        return {
            "timestamp": self.timestamp,
            "user": str(self.user.id),
            "text": self.text
        }
