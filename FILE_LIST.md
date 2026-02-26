Here is the simple, complete list of the files we have officially coded and integrated into the project structure so far:

* **`main.py`**
* The entry point of the application. It initializes the shared state, starts the biometric background threads, and launches the ModernGL rendering window.


* **`engine/state.py`**
* The central "Brain". It contains the `FractalState` class, which holds all the live variables (zoom, coordinates, colors, heart rate, gaze point) and thread locks to keep everything running safely.


* **`engine/renderer.py`**
* The graphics engine. It handles passing variables to the GPU, calculating the continuous exponential zoom and anchor zoom, and drawing the floating `Dear ImGui` control panel.


* **`shaders/fractal.glsl`**
* The raw GPU math. It contains both the vertex and fragment shaders, calculating the fractal dimensions using polar coordinates and applying smooth procedural coloring.


* **`biometrics/tobii_worker.py`**
* The eye-tracking daemon. It connects to the Tobii API and runs continuously in the background, updating the `state.py` gaze coordinates while applying a smoothing filter.


* **`README.md`**
* The project overview, architecture breakdown, and installation instructions.


* **`TODO.md`**
* The master task list outlining our next steps for biometrics, SDF shader math, and LLM integration.



*(Note: We did create `engine/gui.py` earlier, but we successfully deleted it when we upgraded to the integrated ImGui control panel!)* Whenever you're ready to dive back in, we can start by adding `biometrics/polar_worker.py` to get that heart rate data flowing!