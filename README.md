# Clario
## Redefining focus and flow through offline AI

![Project Status](https://img.shields.io/badge/status-complete-brightgreen)

CLARIO is an intelligent, offline application that transforms your webcam into a hands-free command center. It allows you to control your digital environment with natural hand gestures, improving focus and efficiency for presentations, studying, and daily computer use.

## 📸 Demo

*It's highly recommended to record a short GIF or video of your app in action and place it here! This is the best way to show people what your project does.*



---

## ✨ Core Features

The application understands a variety of intuitive gestures to perform key system actions without touching your keyboard or mouse.

| Gesture | Action |
| :--- | :--- |
| **Peace Sign** ✌️ | Toggles Screen Recording (with audio) ON/OFF via Xbox Game Bar. |
| **Fist** 👊 | Mutes/Unmutes your microphone during a recording. |
| **Thumbs Up / Down** 👍👎 | Increases or decreases your computer's master volume. |
| **Point Left / Right** 👈👉 | Navigates presentation slides by pressing the arrow keys. |
| **Three Fingers Up** 🤟 | Switches to **Dual-Screen Productivity Mode**. |
| **Four Fingers Up** | Switches back to **Normal Mode**. |

---

## 🛠️ Technology Stack

This project was built using the following technologies:

* **Language:** `Python 3.11`
* **Core Libraries:**
    * `OpenCV` for capturing and displaying the webcam feed.
    * `MediaPipe` for real-time hand and pose landmark detection.
    * `Tkinter` for the dual-screen graphical user interface (GUI).
    * `pyautogui` for programmatic keyboard control.
    * `pycaw` for system audio and volume control.

---

## ⚙️ Setup and Installation

To run this project on your local machine, follow these steps:

**1. Clone the Repository**
git clone [https://github.com/AkshayaMaragani/clario.git](https://github.com/AkshayaMaragani/clario.git)
cd clario

**2. Install Dependencies**
This project requires Python 3.11. Once Python is installed, install the necessary libraries from the requirements.txt file.
py -3.11 -m pip install -r requirements.txt

**3. Run the Application**
py -3.11 app.py
