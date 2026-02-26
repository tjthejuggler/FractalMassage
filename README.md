
### `README.md`

# FractalMassage 🌀🧠

**FractalMassage** is an experimental, real-time biofeedback visualizer driven by generative AI. It merges mathematical procedural graphics (fractals) with live physiological data (eye-tracking and heart rate variability) to create a closed-loop system designed to induce flow states, lower heart rate, and improve HRV.

Ultimately, this system acts as a "canvas" for an LLM. The LLM continuously monitors the user's biometric reactions and uses a suite of tools to dynamically alter the fractal's shape, color, zoom speed, and seamlessly inject therapeutic text and imagery directly into the mathematical structure of the animation.

## 🏗️ Architecture

To maintain a buttery-smooth 60fps rendering pipeline while handling blocking hardware I/O and latency-heavy AI calls, the project uses a strictly decoupled, threaded architecture:

* **The Brain (`state.py`):** A thread-safe, centralized dictionary (class-based) holding the current state of the universe (zoom level, color tints, biometrics, active words).
* **The Renderer (`renderer.py` & `shaders/fractal.glsl`):** Runs on the main process thread. Uses `ModernGL` to execute raw GLSL shader code directly on the GPU. It includes a native `Dear ImGui` overlay for real-time human or AI parameter tweaking.
* **The Senses (`biometrics/`):** Daemon threads running in the background. They continuously poll hardware (Tobii eye trackers, Polar heart rate monitors) and silently update the Brain without interrupting the GPU.
* **The AI Controller (`llm_logic/` - *WIP*):** An asynchronous loop that analyzes the Brain's biometric history and issues commands to smoothly interpolate the visual state.

## 💻 Hardware Targeting

This project is currently optimized for cutting-edge mobile hardware, specifically targeting the **Intel Core Ultra 9 (Meteor Lake)** architecture running Kubuntu Linux (Wayland):

* **GPU:** Intel Arc iGPU (handling the heavy GLSL fragment shaders).
* **RAM:** 32GB LPDDR5 @ 7467 MT/s (crucial for shared memory bandwidth).
* **NPU:** Intel AI Boost NPU (slated for local LLM offloading).
* **Sensors:** Tobii Eye Tracker 5, Polar H10 / Verity Sense.

## 🚀 Installation & Usage

1. **System Dependencies:**
```bash
sudo apt update && sudo apt install python3-venv libglfw3-dev libsdl2-dev

```


2. **Environment Setup:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install moderngl moderngl-window numpy Pillow imgui tobii_stream_engine bleak

```


3. **Run the Engine:**
```bash
python3 main.py

```



