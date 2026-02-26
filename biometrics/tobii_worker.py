import threading
from tobii_stream_engine import Api, Device, Stream

# Global references prevent Python's garbage collector from destroying the connection
_api = None
_device = None

def setup_and_start_tobii(state):
    global _api, _device
    try:
        print("Tobii: Initializing connection...")
        _api = Api()
        urls = _api.enumerate_local_device_urls()
        
        if not urls:
            print("Tobii: No devices found. Running without eye tracking.")
            return False
            
        url = urls[0]
        print(f"Tobii found at: {url}")
        
        # Initialize the device synchronously on the main thread!
        _device = Device(api=_api, url=url)
        
        def on_gaze_point(timestamp, gaze_point):
            try:
                if hasattr(gaze_point, 'position_xy'):
                    if hasattr(gaze_point.position_xy, 'x'):
                        raw_x = gaze_point.position_xy.x
                        raw_y = gaze_point.position_xy.y
                    else:
                        raw_x = gaze_point.position_xy[0]
                        raw_y = gaze_point.position_xy[1]
                else:
                    raw_x = gaze_point.x
                    raw_y = gaze_point.y
                    
                smoothing = 0.15
                state.gaze_x = (1.0 - smoothing) * state.gaze_x + (smoothing * raw_x)
                state.gaze_y = (1.0 - smoothing) * state.gaze_y + (smoothing * raw_y)
            except Exception:
                pass # Suppress spam if tracking drops

        if _device.is_supported_stream(Stream.GAZE_POINT):
            # Subscribe synchronously
            _device.subscribe_gaze_point(callback=on_gaze_point)
            
            # ONLY put the blocking listener loop in the background thread
            t = threading.Thread(target=_device.run, daemon=True)
            t.start()
            print("Tobii: Streaming started in background thread.")
            return True
        else:
            print("Tobii: Gaze stream not supported.")
            return False
            
    except Exception as e:
        print(f"Tobii Initialization Error: {e}")
        return False