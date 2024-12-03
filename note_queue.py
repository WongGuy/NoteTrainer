# note_queue.py

class NoteQueue:
    def __init__(self, note_generator, queue_size):
        self.note_generator = note_generator
        self.queue_size = queue_size
        # Initialize the target note
        self.target_note = self.note_generator.get_note('')
        # Initialize the note queue
        self.note_queue = self.note_generator.get_note_queue(self.queue_size, self.target_note)
    
    def get_target_note(self):
        return self.target_note
    
    def get_note_queue(self):
        return self.note_queue.copy()
    
    def process_correct_note_detected(self):
        # Move the first note in the note queue to be the new target note
        self.target_note = self.note_queue.pop(0)
        # Add a new random note to the end of the queue
        last_note = self.note_queue[-1] if self.note_queue else self.target_note
        new_note = self.note_generator.get_note(last_note)
        self.note_queue.append(new_note)
    
    def reset_queue(self):
        self.target_note = self.note_generator.get_note('')
        self.note_queue = self.note_generator.get_note_queue(self.queue_size, self.target_note)
