### `TODO.md`

# 📋 Master Task List

#### Phase 1: Biometric Foundation (In Progress)

* [x] **Core Engine:** Establish GPU render loop and shared state management.
* [x] **UI Control:** Implement Dear ImGui for non-blocking visual parameter control.
* [x] **Eye Tracking:** Implement `tobii_worker.py` to stream gaze coordinates.
* [x] **Anchor Zoom:** Calculate mathematical offsets to pull the fractal zoom directly toward the user's gaze point.
* [ ] **Heart Rate Integration:** Refactor the Polar BLE test script into `biometrics/polar_worker.py`. Establish a robust background connection loop.
* [ ] **HRV Math:** Write a rolling-window calculation in `state.py` to convert raw RR intervals from the Polar sensor into standard HRV metrics (RMSSD or SDNN).

#### Phase 2: The Injection Engine (Shader Math)

* [ ] **Text/Image to SDF:** Write a Python utility to convert text strings and image masks into Signed Distance Fields (SDFs) or 2D distance textures.
* [ ] **Texture Uploading:** Create logic in `renderer.py` to seamlessly pass these new textures to the GPU without dropping frames.
* [ ] **Shader Blending (The Hard Part):** Update `fractal.glsl` to use `smooth minimum` math to organically melt the SDF textures into the fractal's complex plane.
* [ ] **Scale & Coordinate Tracking:** Solve the "infinite relativity" problem. When an image is injected, its coordinate space must lock to a specific zoom depth so it scales up smoothly as the user zooms past it, rather than sticking to the screen.

#### Phase 3: The AI Conductor

* [ ] **LLM Tool API:** Create a strict set of Python functions (e.g., `set_target_color`, `inject_phrase(text, x, y)`) that smoothly interpolate the variables in `state.py` over time (rather than snapping them instantly).
* [ ] **Async Loop:** Build `llm_logic/controller.py`. This loop will wake up every *X* seconds, take a snapshot of the HRV/Gaze data, and call the LLM API.
* [ ] **Prompt Engineering:** Design the system prompt detailing the LLM's goal (e.g., "Analyze the user's HRV trajectory. Use your tools to alter the visual state to maximize HRV.").
* [ ] **Image Vision (Optional):** Hook the render loop to save a low-res snapshot of the screen every few seconds to feed to a multimodal LLM, allowing it to "see" what it has created.

#### Phase 4: Optimization (The Deep Zoom)

* [ ] **Floating-Point Limit:** Implement Perturbation Theory and arbitrary-precision arithmetic (using libraries like `gmpy2` or custom GLSL structs) to break past the standard 32-bit/64-bit zoom limit so the fractal never pixelates.
* [ ] **NPU Offloading:** Investigate OpenVINO to run a small, quantized LLM (like Llama 3 8B) directly on the Meteor Lake NPU, entirely removing cloud latency and keeping biometric data local.

---

You have an incredibly solid repository started here. Whenever you are ready to pick this back up, I recommend we tackle the **Polar H10 background worker** next so we can get your heart rate data flowing into the GUI.

How does this documentation look to you? Are there any details or ideas you want me to add to the README before we close out this session?