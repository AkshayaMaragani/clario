import cv2
import mediapipe as mp
import numpy as np
import time
import pyautogui
import tkinter as tk
from tkinter import filedialog
import os
import webbrowser
from PIL import Image, ImageTk
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# --- System Audio Control Setup ---
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
vol_range = volume.GetVolumeRange()
min_vol, max_vol = vol_range[0], vol_range[1]

# --- Helper Function to Calculate Angle ---
def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180.0 else angle

# --- Constants and Initialization ---
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
cap = cv2.VideoCapture(0)

# --- State Management ---
last_action_time = 0
action_cooldown = 1.0
is_mic_muted = False

def get_gesture(hand_landmarks):
    landmarks = hand_landmarks.landmark
    thumb_angle = calculate_angle([landmarks[1].x, landmarks[1].y], [landmarks[2].x, landmarks[2].y], [landmarks[4].x, landmarks[4].y])
    index_angle = calculate_angle([landmarks[5].x, landmarks[5].y], [landmarks[6].x, landmarks[6].y], [landmarks[8].x, landmarks[8].y])
    middle_angle = calculate_angle([landmarks[9].x, landmarks[9].y], [landmarks[10].x, landmarks[10].y], [landmarks[12].x, landmarks[12].y])
    ring_angle = calculate_angle([landmarks[13].x, landmarks[13].y], [landmarks[14].x, landmarks[14].y], [landmarks[16].x, landmarks[16].y])
    pinky_angle = calculate_angle([landmarks[17].x, landmarks[17].y], [landmarks[18].x, landmarks[18].y], [landmarks[20].x, landmarks[20].y])
    thumb_extended, index_extended, middle_extended, ring_extended, pinky_extended = thumb_angle > 150, index_angle > 160, middle_angle > 160, ring_angle > 160, pinky_angle > 160
    
    if not thumb_extended and not index_extended and not middle_extended and not ring_extended and not pinky_extended: return "Fist"
    elif thumb_extended and not index_extended and not middle_extended and not ring_extended and not pinky_extended:
        return "Thumbs Up" if landmarks[4].y < landmarks[2].y else "Thumbs Down"
    elif not thumb_extended and index_extended and not middle_extended and not ring_extended and not pinky_extended:
        return "Point Right" if landmarks[8].x > landmarks[5].x else "Point Left"
    elif not thumb_extended and index_extended and middle_extended and not ring_extended and not pinky_extended: return "Peace Sign"
    elif not thumb_extended and index_extended and middle_extended and ring_extended and not pinky_extended: return "Three Fingers Up"
    elif not thumb_extended and index_extended and middle_extended and ring_extended and pinky_extended: return "Four Fingers Up"
    else: return "No Gesture"

def open_file():
    filepath = filedialog.askopenfilename()
    if filepath:
        if os.name == 'nt': os.startfile(filepath)
        else: webbrowser.open_new(filepath)

# --- App Class for Productivity Mode ---
class ProductivityApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Cogni-Flow AI - Productivity Mode")
        self.root.geometry("1280x720")
        self.continue_loop = True
        self.root.protocol("WM_DELETE_WINDOW", self.close_window) # Handle window close button

        self.root.grid_columnconfigure(0, weight=1); self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        left_frame = tk.Frame(root_window, bg='black'); left_frame.grid(row=0, column=0, sticky="nsew")
        right_frame = tk.Frame(root_window, bg='lightgrey'); right_frame.grid(row=0, column=1, sticky="nsew")
        
        self.video_label = tk.Label(left_frame); self.video_label.pack(expand=True)
        open_button = tk.Button(right_frame, text="Open PDF or Notes File", command=open_file, font=("Arial", 14)); open_button.pack(pady=20, padx=20)
        
        self.update_frame()

    def update_frame(self):
        global last_action_time, is_mic_muted
        success, frame = cap.read()
        if not success:
            if self.continue_loop: self.root.after(15, self.update_frame)
            return
        
        frame_rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        hand_results = hands.process(frame_rgb)
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        gesture = "No Gesture"
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame_bgr, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                gesture = get_gesture(hand_landmarks)
                
                current_time = time.time()
                if current_time - last_action_time > action_cooldown:
                    if gesture == "Four Fingers Up":
                        self.close_window(); return
                    # Actions are handled in both modes, so this can be simplified
                    elif gesture == "Peace Sign": pyautogui.hotkey('win', 'alt', 'r'); last_action_time = current_time
                    elif gesture == "Fist":
                        is_mic_muted = not is_mic_muted
                        pyautogui.hotkey('win', 'alt', 'm')
                        if is_mic_muted:
                            print("ACTION: Microphone MUTED")
                        else:
                            print("ACTION: Microphone UNMUTED")
                        last_action_time = current_time
                    elif gesture == "Thumbs Up": volume.SetMasterVolumeLevel(min(max_vol, volume.GetMasterVolumeLevel() + 2.0), None); last_action_time = current_time
                    elif gesture == "Thumbs Down": volume.SetMasterVolumeLevel(max(min_vol, volume.GetMasterVolumeLevel() - 2.0), None); last_action_time = current_time
                    elif gesture == "Point Right": pyautogui.press('right'); last_action_time = current_time
                    elif gesture == "Point Left": pyautogui.press('left'); last_action_time = current_time
        
        img = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)
        
        if self.continue_loop: self.root.after(15, self.update_frame)
        
    def close_window(self):
        global last_action_time
        self.continue_loop = False
        last_action_time = time.time() # Add cooldown after closing
        self.root.destroy()

# --- Main Program Manager ---
while True:
    # --- Normal Mode Loop ---
    mode_switch = False
    while True:
        success, frame = cap.read()
        if not success: continue

        frame_rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        hand_results = hands.process(frame_rgb)
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        gesture = "No Gesture"
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame_bgr, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                gesture = get_gesture(hand_landmarks)

                # --- ACTION DISPATCHER FOR NORMAL MODE ---
                current_time = time.time()
                if current_time - last_action_time > action_cooldown:
                    if gesture == "Three Fingers Up":
                        mode_switch = True; last_action_time = current_time; break
                    elif gesture == "Peace Sign": pyautogui.hotkey('win', 'alt', 'r'); last_action_time = current_time
                    elif gesture == "Fist":
                        is_mic_muted = not is_mic_muted
                        pyautogui.hotkey('win', 'alt', 'm')
                        if is_mic_muted:
                            print("ACTION: Microphone UNMUTED")
                        else:
                            print("ACTION: Microphone MUTED")
                        last_action_time = current_time
                    elif gesture == "Thumbs Up": volume.SetMasterVolumeLevel(min(max_vol, volume.GetMasterVolumeLevel() + 2.0), None); last_action_time = current_time
                    elif gesture == "Thumbs Down": volume.SetMasterVolumeLevel(max(min_vol, volume.GetMasterVolumeLevel() - 2.0), None); last_action_time = current_time
                    elif gesture == "Point Right": pyautogui.press('right'); last_action_time = current_time
                    elif gesture == "Point Left": pyautogui.press('left'); last_action_time = current_time

        if mode_switch: break

        cv2.putText(frame_bgr, gesture, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.imshow('Cogni-Flow AI - Normal Mode', frame_bgr)
        
        if cv2.waitKey(5) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            exit()

    # --- Launch Productivity Mode ---
    cv2.destroyAllWindows()
    root = tk.Tk()
    app = ProductivityApp(root)
    root.mainloop()