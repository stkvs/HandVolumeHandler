# Hand Volume Handler

A computer vision application that allows you to control audio volume with hand gestures.

## Description

Hand Volume Handler is a Python application that uses your webcam to detect hand gestures and control the volume of audio applications running on your computer. Using the power of MediaPipe for hand tracking and pycaw for audio control, this application allows you to adjust volume levels with natural hand movements.

## Features

- Real-time hand tracking and gesture recognition
- Volume control using the pinch gesture (distance between thumb and index finger)
- Automatic detection of compatible audio applications (browsers and music players)
- Visual feedback showing current hand position, gesture recognition, and volume levels
- Audio session caching to maintain control even when applications temporarily stop producing sound

## Requirements

- Python 3.7+
- Webcam
- Windows OS (pycaw is Windows-specific)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/stkvs/HandVolumeHandler.git
cd HandVolumeHandler
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

#### Run the script
```bash
python main.py
```

#### Changing Volume:

1. Position your hand infront of the camera.
2. To activate the volume changing close your Middle, Ring and Pinky finger
3. Bring your Index and Thumb finger closer together or further apart to change volume
4. To stop changing volume, open your hand with all fingers extended. 

#### Ending the script:

3. Press 'ESC' to exit the application.

## How It Works

1. **Hand Detection**: The application uses MediaPipe to detect and track hand landmarks in real-time from your webcam feed.

2a. **Gesture Recognition**: The system identifies a specific hand gesture (index finger and thumb extended, other fingers folded down) as the control position. By utilising the points listed on the MediaPipe documentation:

![Points on hand recognised by MediaPipe](https://mediapipe.dev/images/mobile/hand_landmarks.png)

2b. **How it works:** Utilising the specific points of 8 (Index Finger) and 4 (Thumb Tip) to handle volume changes and points 12 (Middle Finger), 16 (Ring Finger) and 20 (Pinky Finger) to check if they are below the Index finger will then ensure the volume control is on.

3. **Audio Control**: Using pycaw (Python Core Audio Windows), the application adjusts the volume of active audio sessions for browsers and music applications.

## Supported Applications

The following applications are supported for volume control:

### Browsers:
- Chrome
- Firefox
- Microsoft Edge
- Opera
- Brave
- Safari

### Music Applications:
- Spotify
- Windows Music
- Amazon Music
- Tidal
- Deezer
- iTunes
- VLC

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT