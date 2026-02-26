import sys
import traceback

def run_control_window(shared_state):
    try:
        import tkinter as tk

        root = tk.Tk()
        root.title("FractalMassage - LLM Control Panel")
        root.geometry("400x400")
        
        def update_val(key, value):
            shared_state[key] = float(value)

        def make_slider(label, key, min_v, max_v, res):
            frame = tk.Frame(root)
            frame.pack(fill='x', padx=10, pady=5)
            tk.Label(frame, text=label).pack(side='left')
            
            slider = tk.Scale(frame, from_=min_v, to=max_v, resolution=res, orient='horizontal',
                              command=lambda v, k=key: update_val(k, v))
            slider.set(shared_state[key])
            slider.pack(side='right', expand=True, fill='x')

        make_slider("Zoom Speed", 'zoom_speed', -1.0, 1.0, 0.01)
        make_slider("Fractal Dimension (Shape)", 'power', 1.0, 5.0, 0.01)
        make_slider("Color - Red", 'color_r', 0.0, 1.0, 0.01)
        make_slider("Color - Green", 'color_g', 0.0, 1.0, 0.01)
        make_slider("Color - Blue", 'color_b', 0.0, 1.0, 0.01)
        make_slider("Pulse Speed", 'pulse_speed', 0.0, 2.0, 0.01)
        
        root.mainloop()

    except Exception as e:
        print("\n" + "="*50)
        print("GUI PROCESS CRASHED!")
        print(traceback.format_exc())
        print("="*50 + "\n")
        sys.exit(1)