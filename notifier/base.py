# notifier/base.py

from abc import ABC, abstractmethod

class Notifier(ABC):
    @abstractmethod
    def send(self, title, message, image_path=None):
        pass
