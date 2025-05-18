import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import messagebox
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import math
import threading
import time
 
# Initialize MediaPipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Initialize Pycaw for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Get volume range for mapping
vol_range = volume.GetVolumeRange()
min_vol = vol_range[0]
max_vol = vol_range[1]

class VolumeControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gesture Volume Control")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        self.label = tk.Label(root, text="Gesture Volume Control", font=("Arial", 18))
        self.label.pack(pady=10)
        
        self.volume_label = tk.Label(root, text="Volume: 50%", font=("Arial", 14))
        self.volume_label.pack(pady=5)
        
        self.volume_bar = tk.Canvas(root, width=200, height=25, bg="grey")
        self.volume_bar.pack(pady=5)
        self.volume_bar_fill = self.volume_bar.create_rectangle(0, 0, 100, 25, fill="green")
        
        self.start_button = tk.Button(root, text="Start Gesture Control", font=("Arial", 12), command=self.start_gesture_control)
        self.start_button.pack(pady=10)
        
        self.stop_button = tk.Button(root, text="Stop Gesture Control", font=("Arial", 12), command=self.stop_gesture_control, state=tk.DISABLED)
        self.stop_button.pack(pady=5)
        
        self.instructions_button = tk.Button(root, text="How to Use", font=("Arial", 12), command=self.show_instructions)
        self.instructions_button.pack(pady=10)
        
        self.gesture_control_enabled = False
        self.thread = None
    
    def start_gesture_control(self):
        if not self.gesture_control_enabled:
            self.gesture_control_enabled = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.label.config(text="Gesture Control Enabled")
            self.thread = threading.Thread(target=self.run_gesture_control, daemon=True)
            self.thread.start()
    
    def stop_gesture_control(self):
        if self.gesture_control_enabled:
            self.gesture_control_enabled = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.label.config(text="Gesture Control Disabled")
    
    def show_instructions(self):
        instructions = (
            "1. **Adjust Volume**:\n"
            "- Hold up your hand in view of the camera.\n"
            "- Pinch your thumb and index finger together to decrease volume.\n"
            "- Spread your thumb and index finger apart to increase volume.\n\n"
            "2. **Mute/Unmute**:\n"
            "- Make a fist to mute the volume.\n"
            "- Open your hand to unmute."
        )
        messagebox.showinfo("Instructions", instructions)
    
    def run_gesture_control(self):
        cap = cv2.VideoCapture(0)
        prev_time = time.time()
        current_volume = volume.GetMasterVolumeLevelScalar()
        
        while self.gesture_control_enabled:
            success, img = cap.read()
            if not success:
                continue
            
            img = cv2.flip(img, 1)  # Mirror the image
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(img_rgb)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    # Get coordinates of thumb tip and index finger tip
                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    
                    # Convert normalized coordinates to pixel values
                    h, w, _ = img.shape
                    thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
                    index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
                    middle_x, middle_y = int(middle_tip.x * w), int(middle_tip.y * h)
                    pinky_x, pinky_y = int(pinky_tip.x * w), int(pinky_tip.y * h)
                    wrist_x, wrist_y = int(wrist.x * w), int(wrist.y * h)
                    
                    # Calculate distance between thumb and index finger
                    distance = math.hypot(index_x - thumb_x, index_y - thumb_y)
                    
                    # Map the distance to volume level
                    # Adjust these values based on your camera and hand size
                    min_distance = 30
                    max_distance = 200
                    distance = max(min_distance, min(distance, max_distance))
                    vol = np.interp(distance, [min_distance, max_distance], [0.0, 1.0])
                    
                    # Set volume
                    volume.SetMasterVolumeLevelScalar(vol, None)
                    
                    # Update volume label and bar in GUI
                    vol_percentage = int(vol * 100)
                    self.update_volume_display(vol_percentage)
                    
                    # Determine if fist (mute) or open hand (unmute)
                    # Simple heuristic: if distance is below a threshold, consider it a fist
                    if distance < 40:
                        volume.SetMute(1, None)  # Mute
                        self.update_volume_display(0, mute=True)
                        cv2.putText(img, 'Muted', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    else:
                        volume.SetMute(0, None)  # Unmute
                        cv2.putText(img, f'Volume: {vol_percentage}%', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # Optional: Draw a line between thumb and index finger
                    cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), (255, 0, 0), 2)
                    cv2.circle(img, (thumb_x, thumb_y), 5, (255, 0, 0), cv2.FILLED)
                    cv2.circle(img, (index_x, index_y), 5, (255, 0, 0), cv2.FILLED)
            
            # Display the webcam feed with annotations
            cv2.imshow("Gesture Volume Control", img)
            
            # Exit if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.gesture_control_enabled = False
                break
            
            # Limit the loop to reduce CPU usage
            time.sleep(0.01)
        
        cap.release()
        cv2.destroyAllWindows()
    
    def update_volume_display(self, vol, mute=False):
        def update():
            if mute:
                self.volume_label.config(text="Volume: Muted")
                self.volume_bar.itemconfig(self.volume_bar_fill, fill="red")
                self.volume_bar.coords(self.volume_bar_fill, 0, 0, 0, 25)
            else:
                self.volume_label.config(text=f"Volume: {vol}%")
                self.volume_bar.itemconfig(self.volume_bar_fill, fill="green")
                # Update the volume bar length based on volume percentage
                new_length = (vol / 100) * 200  # Assuming the bar width is 200
                self.volume_bar.coords(self.volume_bar_fill, 0, 0, new_length, 25)
        # Schedule the update in the main thread
        self.root.after(0, update)

# Main Application Entry Point
if __name__ == "__main__":
    root = tk.Tk()
    app = VolumeControlApp(root)
    root.mainloop()
