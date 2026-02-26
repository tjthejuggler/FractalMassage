import os
import time
import math
import moderngl_window as mglw
import imgui
from moderngl_window.integrations.imgui import ModernglWindowRenderer
from engine.sdf_maker import create_text_sdf # NEW

class FractalRenderer(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "FractalMassage - Engine"
    window_size = (1280, 720)
    aspect_ratio = None
    resizable = True

    # Injected by main.py
    state = None 
    
    resource_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quad = mglw.geometry.quad_fs()
        
        # Shader will now compile without Segfaulting
        self.program = self.load_program(path='shaders/fractal.glsl')
        
        # Create a tiny 1x1 blank texture so the GPU has something to read initially
        self.sdf_tex = self.ctx.texture((1, 1), 1, b'\x00')
        self.sdf_tex.use(location=0)
        
        # Initialize the floating GUI
        imgui.create_context()
        self.imgui = ModernglWindowRenderer(self.wnd)

    def on_render(self, current_time, frame_time):
        self.ctx.clear(0.0, 0.0, 0.0)
        elapsed = time.time() - self.state.time_started

        # --- Handle New Text Injections ---
        if self.state.injection_needs_update:
            # Generate the math texture
            data, w, h = create_text_sdf(self.state.inject_text)
            self.sdf_tex = self.ctx.texture((w, h), 1, data)
            self.state.injection_needs_update = False
            self.state.inject_active = True

        # Send textures and math to the GPU
        if self.state.inject_active and hasattr(self, 'sdf_tex'):
            self.sdf_tex.use(location=0)
            self.program['sdf_texture'].value = 0
            self.program['inject_active'].value = 1 # CHANGED TO 1
            self.program['inject_pos'].value = (self.state.inject_x, self.state.inject_y)
            self.program['inject_scale'].value = self.state.inject_scale
        else:
            self.program['inject_active'].value = 0 # CHANGED TO 0


        # 1. Calculate the aspect ratio scale for UV mapping
        aspect_x = self.window_size[0] / min(self.window_size)
        aspect_y = self.window_size[1] / min(self.window_size)

        # 2. Determine our zoom anchor point
        if self.state.use_eye_tracker:
            # Map Tobii coordinates (0=top left, 1=bottom right) to OpenGL Shader space
            target_uv_x = (self.state.gaze_x - 0.5) * aspect_x
            target_uv_y = (0.5 - self.state.gaze_y) * aspect_y # Y is inverted in OpenGL
        else:
            # If disabled, zoom straight into the center
            target_uv_x = 0.0
            target_uv_y = 0.0

        # 3. Apply Continuous Zoom
        old_zoom = self.state.zoom
        zoom_multiplier = math.exp(self.state.zoom_speed * frame_time)
        self.state.zoom *= zoom_multiplier

        # 4. Apply Anchor Offset Math (Pulls the fractal towards the target point)
        self.state.offset_x += target_uv_x * (1.0 / old_zoom - 1.0 / self.state.zoom)
        self.state.offset_y += target_uv_y * (1.0 / old_zoom - 1.0 / self.state.zoom)

        # Send math to the GPU
        self.program['resolution'].value = (self.window_size[0], self.window_size[1])
        self.program['offset'].value = (self.state.offset_x, self.state.offset_y)
        self.program['zoom'].value = self.state.zoom
        self.program['max_iter'].value = self.state.max_iter
        self.program['time'].value = elapsed * self.state.pulse_speed
        
        self.program['power'].value = self.state.power
        self.program['color_tint'].value = (self.state.color_r, self.state.color_g, self.state.color_b)
        
        self.quad.render(self.program)
        self.render_ui()

    def render_ui(self):
        imgui.new_frame()
        imgui.begin("LLM Control Panel", True)
        
        # --- Eye Tracker Toggle ---
        _, self.state.use_eye_tracker = imgui.checkbox("Eye Tracker Zoom", self.state.use_eye_tracker)
        imgui.spacing()
        
        # Sliders
        _, self.state.zoom_speed = imgui.slider_float("Zoom Speed", self.state.zoom_speed, -1.0, 1.0)
        _, self.state.power = imgui.slider_float("Fractal Dimension", self.state.power, 1.0, 5.0)
        _, self.state.max_iter = imgui.slider_int("Detail (Max Iter)", self.state.max_iter, 10, 500)
        
        imgui.spacing()
        _, self.state.color_r = imgui.slider_float("Red", self.state.color_r, 0.0, 1.0)
        _, self.state.color_g = imgui.slider_float("Green", self.state.color_g, 0.0, 1.0)
        _, self.state.color_b = imgui.slider_float("Blue", self.state.color_b, 0.0, 1.0)
        _, self.state.pulse_speed = imgui.slider_float("Pulse Speed", self.state.pulse_speed, 0.0, 2.0)
        
        imgui.spacing()
        imgui.text("--- Biometrics Data ---")
        imgui.text(f"Heart Rate: {self.state.current_hr} BPM")
        imgui.text(f"Gaze Point: ({self.state.gaze_x:.2f}, {self.state.gaze_y:.2f})")

        # --- Injection Engine UI ---
        imgui.spacing()
        imgui.text("--- Text Injection ---")
        _, self.state.inject_text = imgui.input_text("Word", self.state.inject_text, 256)
        
        if imgui.button("Inject Here"):
            # Lock the coordinates and scale to EXACTLY where the user is looking right now
            self.state.inject_x = self.state.offset_x
            self.state.inject_y = self.state.offset_y
            self.state.inject_scale = self.state.zoom
            self.state.injection_needs_update = True
            
        if imgui.button("Clear Text"):
            self.state.inject_active = False

        imgui.end()
        imgui.render()
        self.imgui.render(imgui.get_draw_data())

    # --- Mouse & Keyboard Event Forwarding ---
    def on_mouse_drag_event(self, x, y, dx, dy):
        self.imgui.mouse_drag_event(x, y, dx, dy)
        # ONLY pan the fractal if we are not currently dragging a UI slider
        if not self.imgui.io.want_capture_mouse:
            aspect = self.window_size[0] / self.window_size[1]
            scale_x = dx / self.window_size[0]
            scale_y = dy / self.window_size[1]
            self.state.offset_x -= (scale_x * aspect) / self.state.zoom
            self.state.offset_y += scale_y / self.state.zoom

    def on_mouse_position_event(self, x, y, dx, dy):
        self.imgui.mouse_position_event(x, y, dx, dy)

    def on_mouse_press_event(self, x, y, button):
        self.imgui.mouse_press_event(x, y, button)

    def on_mouse_release_event(self, x, y, button):
        self.imgui.mouse_release_event(x, y, button)

    def on_key_event(self, key, action, modifiers):
        self.imgui.key_event(key, action, modifiers)

    def on_resize(self, width, height):
        self.imgui.resize(width, height)