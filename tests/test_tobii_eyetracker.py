import time
from tobii_stream_engine import Api, Device, GazePoint, Stream

def on_gaze_point(timestamp: int, gaze_point: GazePoint) -> None:
    # This callback fires every time the tracker registers your eyes
    # gaze_point contains normalized X and Y coordinates (0.0 to 1.0)
    print(f"Timestamp: {timestamp} | Gaze: {gaze_point}")

def main() -> None:
    print("Initializing Tobii API...")
    api = Api()
    
    print("Searching for trackers...")
    device_urls = api.enumerate_local_device_urls()
    if not device_urls:
        print("Error: No Tobii device found. Make sure it is plugged in.")
        return
    
    print(f"Found tracker at: {device_urls[0]}")
    device = Device(api=api, url=device_urls[0])
    
    if not device.is_supported_stream(Stream.GAZE_POINT):
        print("Error: Gaze point streaming is not supported on this device.")
        return

    print("Subscribing to gaze stream. Look at the screen! (Press Ctrl+C to stop)")
    # Hook up our callback function
    device.subscribe_gaze_point(callback=on_gaze_point)
    
    try:
        # Start the blocking event loop to keep the script alive and listening
        device.run()
    except KeyboardInterrupt:
        print("\nStopping tracker...")
    finally:
        # Clean up the connection when we exit
        print("Disconnected.")

if __name__ == "__main__":
    main()