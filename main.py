import faulthandler
faulthandler.enable()

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import moderngl_window as mglw
from engine.state import FractalState
from engine.renderer import FractalRenderer
from biometrics.tobii_worker import setup_and_start_tobii

if __name__ == '__main__':
    global_state = FractalState()
    
    # 1. Fully initialize Tobii synchronously BEFORE the GPU touches the display server
    setup_and_start_tobii(global_state)
        
    # 2. Now it is 100% safe to lock the display server for ModernGL
    mglw.settings.RESOURCE_DIRS = [os.path.dirname(os.path.abspath(__file__))]
    FractalRenderer.state = global_state
    
    mglw.run_window_config(FractalRenderer)