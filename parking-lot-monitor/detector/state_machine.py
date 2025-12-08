# detector/state_machine.py

class PresenceStateMachine:
    def __init__(self, frames_required=5):
        self.frames_required = frames_required
        self.present_count = 0
        self.absent_count = 0
        self.state = False  # False = no vehicle, True = vehicle present

    def update(self, vehicle_present):
        event = None

        if vehicle_present:
            self.present_count += 1
            self.absent_count = 0
        else:
            self.absent_count += 1
            self.present_count = 0

        # Vehicle ENTERS lot
        if not self.state and self.present_count >= self.frames_required:
            self.state = True
            event = "ENTER"

        # Vehicle EXITS lot
        if self.state and self.absent_count >= self.frames_required:
            self.state = False
            event = "EXIT"

        return event
