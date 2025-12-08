# detector/vehicle_counter.py

class VehicleCounter:
    """Tracks vehicle count changes with hysteresis to avoid flickering"""
    
    def __init__(self, stability_frames=5):
        self.stability_frames = stability_frames
        self.current_count = 0
        self.candidate_count = 0
        self.candidate_frames = 0
        
    def update(self, detected_count):
        """
        Update with new detection count.
        Returns: (event, count) where event is 'INCREASE', 'DECREASE', or None
        """
        event = None
        
        # If detection matches current count, reset candidate
        if detected_count == self.current_count:
            self.candidate_count = detected_count
            self.candidate_frames = 0
        # If detection is different, track it
        elif detected_count == self.candidate_count:
            self.candidate_frames += 1
        # New different count, reset candidate
        else:
            self.candidate_count = detected_count
            self.candidate_frames = 1
            
        # Confirm change after stability threshold
        if self.candidate_frames >= self.stability_frames:
            old_count = self.current_count
            self.current_count = self.candidate_count
            
            if self.current_count > old_count:
                event = 'INCREASE'
            elif self.current_count < old_count:
                event = 'DECREASE'
                
            self.candidate_frames = 0
            
        return event, self.current_count
    
    def get_count(self):
        return self.current_count
