import time
import threading

class FractalState:
    def __init__(self):
        # Navigation & Zoom
        self.offset_x = -0.75
        self.offset_y = 0.0
        self.zoom = 1.0
        self.zoom_speed = 0.15
        
        # Visuals & LLM Controls
        self.max_iter = 150 
        self.power = 2.0         
        self.color_r = 0.0       
        self.color_g = 0.1       
        self.color_b = 0.2       
        self.pulse_speed = 0.2
        
        self.time_started = time.time()
        self.lock = threading.Lock()
        
        # --- Biometrics ---
        self.use_eye_tracker = False # NEW: UI Toggle
        self.gaze_x = 0.5 
        self.gaze_y = 0.5 
        self.current_hr = 0
        self.rr_intervals = []

        # --- Injection Engine ---
        self.inject_text = "BREATHE"
        self.inject_active = False
        self.injection_needs_update = False
        self.inject_x = 0.0
        self.inject_y = 0.0
        self.inject_scale = 1.0