import threading
from tobii_stream_engine import Api, Device, GazePoint, Stream

def _run_tobii_loop(state):
    def on_gaze_point(timestamp: int, gaze_point: GazePoint) -> None:
        try:
            # The CFFI wrapper nests the coordinates inside 'position_xy'
            if hasattr(gaze_point, 'position_xy'):
                # Check if it's an object with .x/.y, or a tuple with [0]/[1]
                if hasattr(gaze_point.position_xy, 'x'):
                    raw_x = gaze_point.position_xy.x
                    raw_y = gaze_point.position_xy.y
                else:
                    raw_x = gaze_point.position_xy[0]
                    raw_y = gaze_point.position_xy[1]
            else:
                raw_x = gaze_point.x
                raw_y = gaze_point.y
                
            # Apply our Exponential Moving Average to smooth out micro-jitters
            smoothing = 0.15
            state.gaze_x = (1.0 - smoothing) * state.gaze_x + (smoothing * raw_x)
            state.gaze_y = (1.0 - smoothing) * state.gaze_y + (smoothing * raw_y)
            
        except Exception as e:
            # If it fails, print the actual object layout so we can debug it instantly
            print(f"Tobii Data Error: {e}")
            print(f"GazePoint structure: {dir(gaze_point)}")

    try:
        api = Api()
        device_urls = api.enumerate_local_device_urls()
        
        if not device_urls:
            print("Tobii: No device found. Eye tracking disabled.")
            return
            
        device = Device(api=api, url=device_urls[0])
        
        # Verify the device supports the gaze stream before subscribing
        if not device.is_supported_stream(Stream.GAZE_POINT):
            print("Tobii: Gaze point stream not supported on this specific device.")
            return
            
        device.subscribe_gaze_point(callback=on_gaze_point)
        print(f"Tobii Eye Tracker Connected: {device_urls[0]}")
        
        # This blocks the background thread, keeping the connection alive
        device.run() 
    except Exception as e:
        print(f"Tobii Initialization Error: {e}")

def start_tobii_thread(state):
    """Launches the Tobii tracker in a background thread so the GPU doesn't freeze."""
    t = threading.Thread(target=_run_tobii_loop, args=(state,), daemon=True)
    t.start()