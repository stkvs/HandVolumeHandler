import mediapipe
import cv2
import math
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

#Use MediaPipe to draw the hand framework over the top of hands it identifies in Real-Time
drawingModule = mediapipe.solutions.drawing_utils
handsModule = mediapipe.solutions.hands

# Create a cache for audio sessions
session_cache = {}

# Function to get audio sessions and control volume
def get_audio_sessions():
    global session_cache
    sessions = AudioUtilities.GetAllSessions()
    active_sessions = []
    
    # Define browsers and music apps to include
    browser_names = ["chrome.exe", "firefox.exe", "msedge.exe", "opera.exe", "brave.exe", "safari.exe"]
    music_apps = ["spotify.exe", "music.ui.exe", "amazonmusic.exe", "tidal.exe", "deezer.exe", "iTunes.exe", "vlc.exe"]
    allowed_apps = browser_names + music_apps
    
    # Apps to explicitly exclude
    excluded_apps = ["discord.exe", "steam.exe", "steamwebhelper.exe", "discord.exe"]
    
    # Temporary dict to track current sessions
    current_sessions = {}
    
    for session in sessions:
        if session.Process and session.Process.name() != "System":
            process_name = session.Process.name().lower()
            # Only include browsers and music apps, explicitly exclude unwanted apps
            if (process_name in allowed_apps) and (process_name not in excluded_apps):
                volume_interface = session._ctl.QueryInterface(ISimpleAudioVolume)
                is_muted = volume_interface.GetMute()
                volume = volume_interface.GetMasterVolume() * 100
                
                # Keep track of all sessions, even if volume is 0
                session_info = {
                    'name': session.Process.name(),
                    'volume': volume,
                    'interface': volume_interface
                }
                
                # Add to current active sessions if volume > 0 and not muted
                if not is_muted and volume > 0:
                    active_sessions.append(session_info)
                
                # Update cache regardless of volume level
                session_id = f"{session.Process.name()}_{id(session)}"
                current_sessions[session_id] = session_info
                session_cache[session_id] = session_info
    
    # If no active sessions but we have cached sessions, use the cache
    if not active_sessions and session_cache:
        # Keep only sessions that still exist
        session_cache = {k: v for k, v in session_cache.items() if k in current_sessions}
        return list(session_cache.values())
    
    # Update cache with current sessions
    session_cache = current_sessions
    
    return active_sessions

#Use OpenCV functionality to create a Video stream and add some values
cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')

#Add confidence values and extra settings to MediaPipe hand tracking
with handsModule.Hands(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=1) as hands:
    while True:
        ret, frame = cap.read()
         
        frame1 = cv2.resize(frame, (640, 480))
         
        results = hands.process(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))
        
        # Get active audio sessions
        active_sessions = get_audio_sessions()
         
        if results.multi_hand_landmarks != None:
            for handLandmarks in results.multi_hand_landmarks:
                drawingModule.draw_landmarks(frame1, handLandmarks, handsModule.HAND_CONNECTIONS)
                
                # Check if fingers are in the right position (index and thumb up, others down)
                indexTip = handLandmarks.landmark[8].y
                indexMid = handLandmarks.landmark[7].y
                thumbTip = handLandmarks.landmark[4].y
                
                # Get middle finger points (12, 11, 10)
                middleTip = handLandmarks.landmark[12].y
                middleMid = handLandmarks.landmark[11].y
                middleBase = handLandmarks.landmark[10].y
                
                # Get ring finger points (16, 15, 14)
                ringTip = handLandmarks.landmark[16].y
                ringMid = handLandmarks.landmark[15].y
                ringBase = handLandmarks.landmark[14].y
                
                # Get pinky finger points (20, 19, 18)
                pinkyTip = handLandmarks.landmark[20].y
                pinkyMid = handLandmarks.landmark[19].y
                pinkyBase = handLandmarks.landmark[18].y
                
                # Check if middle, ring, and pinky fingers are down (tips below base)
                middle_down = middleTip > middleBase
                ring_down = ringTip > ringBase
                pinky_down = pinkyTip > pinkyBase
                
                # Only allow volume control if other fingers are down
                valid_hand_position = middle_down and ring_down and pinky_down
                
                # Add visual indicator for hand position
                if valid_hand_position:
                    cv2.putText(frame1, "Volume Control: Active", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    cv2.putText(frame1, "Volume Control: Inactive", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                # Get coordinates for index finger tip (8) and thumb tip (4)
                indexTip_pixel = drawingModule._normalized_to_pixel_coordinates(handLandmarks.landmark[8].x, handLandmarks.landmark[8].y, 640, 480)
                thumbTip_pixel = drawingModule._normalized_to_pixel_coordinates(handLandmarks.landmark[4].x, handLandmarks.landmark[4].y, 640, 480)
                
                if indexTip_pixel and thumbTip_pixel:
                    # Draw a line between index and thumb tips
                    cv2.line(frame1, indexTip_pixel, thumbTip_pixel, (0, 255, 0), 2)

                    # Calculate Euclidean distance between thumb and index finger
                    distance = math.sqrt((indexTip_pixel[0] - thumbTip_pixel[0])**2 + 
                                    (indexTip_pixel[1] - thumbTip_pixel[1])**2)
                    
                    # Get coordinates for wrist (0) and middle finger MCP (9) to calculate hand size
                    wrist_pixel = drawingModule._normalized_to_pixel_coordinates(
                        handLandmarks.landmark[0].x, handLandmarks.landmark[0].y, 640, 480)
                    middle_mcp_pixel = drawingModule._normalized_to_pixel_coordinates(
                        handLandmarks.landmark[9].x, handLandmarks.landmark[9].y, 640, 480)
                    
                    # Calculate hand size reference (distance from wrist to middle finger MCP)
                    if wrist_pixel and middle_mcp_pixel:
                        hand_size = math.sqrt((wrist_pixel[0] - middle_mcp_pixel[0])**2 + 
                                        (wrist_pixel[1] - middle_mcp_pixel[1])**2)
                        
                        # Calculate relative distance (normalized by hand size)
                        relative_distance = distance / hand_size if hand_size > 0 else 0
                        
                        # Define a maximum relative distance threshold
                        max_relative_distance = 1.5
                        
                        # Calculate percentage closed based on relative distance
                        percentage_closed = max(0, min(100, 100 - (relative_distance / max_relative_distance * 100)))
                        
                        # Display the distances and percentage on the frame
                        cv2.putText(frame1, f"Rel Distance: {relative_distance:.2f}", (10, 60), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.putText(frame1, f"Closed: {percentage_closed:.1f}%", (10, 90), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        # Only set volume if hand is in the right position
                        if valid_hand_position:
                            # Set volume for active applications based on hand gesture
                            for i, session in enumerate(active_sessions):
                                # Convert percentage_closed to volume level (0.0 to 1.0)
                                volume_level = 1.0 - (percentage_closed / 100.0)
                                
                                # Set the volume for this application
                                try:
                                    session['interface'].SetMasterVolume(volume_level, None)
                                    session['volume'] = volume_level * 100
                                    
                                    # Display application name and volume on screen
                                    y_position = 120 + (i * 30)
                                    cv2.putText(frame1, f"{session['name']}: {volume_level*100:.1f}%", 
                                            (10, y_position), cv2.FONT_HERSHEY_SIMPLEX, 
                                            0.7, (0, 255, 0), 2)
                                except:
                                    pass


          
        # Display information about active audio sessions
        if not results.multi_hand_landmarks:
            cv2.putText(frame1, "Apps playing audio:", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            for i, session in enumerate(active_sessions):
                y_position = 90 + (i * 30)
                cv2.putText(frame1, f"{session['name']}: {session['volume']:.1f}%", 
                          (10, y_position), cv2.FONT_HERSHEY_SIMPLEX, 
                          0.7, (0, 255, 0), 2)
          
        # Show the current frame to the desktop
        cv2.imshow("Frame", frame1)
        key = cv2.waitKey(1) & 0xFF
         
        # If 'esc' is pressed on the keyboard, stop the system
        if key == 27:
            break