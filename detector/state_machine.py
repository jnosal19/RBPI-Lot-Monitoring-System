# detector/state_machine.py

from config import FRAMES_REQUIRED_INSIDE, FRAMES_REQUIRED_OUTSIDE

class PresenceStateMachine:
    def __init__(self):
        self.state = "ABSENT"
        self.frames_in = 0
        self.frames_out = 0

    def update(self, vehicle_present):
        """
        Input: vehicle_present = True/False
        Output: "ENTER", "EXIT", or None
        """

        if vehicle_present:
            self.frames_in += 1
            self.frames_out = 0
        else:
            self.frames_out += 1
            self.frames_in = 0

        if self.state == "ABSENT" and self.frames_in >= FRAMES_REQUIRED_INSIDE:
            self.state = "PRESENT"
            return "ENTER"

        if self.state == "PRESENT" and self.frames_out >= FRAMES_REQUIRED_OUTSIDE:
            self.state = "ABSENT"
            return "EXIT"

        return None
