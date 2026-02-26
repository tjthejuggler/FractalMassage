import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import moderngl_window as mglw
from engine.state import FractalState
from engine.renderer import FractalRenderer
from biometrics.tobii_worker import start_tobii_thread # NEW

if __name__ == '__main__':
    global_state = FractalState()
    
    # NEW: Start the eye tracker in the background!
    start_tobii_thread(global_state)
    
    mglw.settings.RESOURCE_DIRS = [os.path.dirname(os.path.abspath(__file__))]
    FractalRenderer.state = global_state
    
    mglw.run_window_config(FractalRenderer)