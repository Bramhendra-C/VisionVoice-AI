import cv2
import time
import datetime
# Import the speak function from the voice assistant module
import voice_assistant 

face_data = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
webcam = cv2.VideoCapture(0)

# Set the threshold for unfocused time
UNFOCUS_TIMEOUT = 10 

def get_face_unfocus_count():
    count = 0
    focused = True
    last_focus_time = time.time()
    
    # NEW STATE: Controls when the assistant speaks the time
    # Start as True so it speaks the time when the user first focuses.
    can_speak = True 
    
    while True:
        success, frame = webcam.read()
        if not success:
            break

        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_co = face_data.detectMultiScale(gray_img, scaleFactor=1.5, minNeighbors=5)

        thumb_size = (300, 300)

        # --- FOCUS/UNFOCUS LOGIC ---
        if len(face_co) > 0:
            # FACE DETECTED (FOCUSED)
            (x, y, w, h) = face_co[0]
            face_roi = frame[y:y+h, x:x+w]
            thumbnail = cv2.resize(face_roi, thumb_size)
            border_color = (0, 255, 0)
            
            last_focus_time = time.time() 
            
            # Implementation: Speak the time and remove access
            if focused:
                focused = False
            
            if can_speak:
                current_time = datetime.datetime.now().strftime('%I:%M:%S')
                # Call the imported speak function
                voice_assistant.speak(f"You are focused! The current time is {current_time}. Keep working!")
                # Now that it has spoken, remove access
                can_speak = False 
                
            label = "FOCUSED"
            label_color = (0, 255, 0)
            
        else:
            # NO FACE DETECTED (UNFOCUSED)
            blurred = cv2.GaussianBlur(frame, (45, 45), 0)
            thumbnail = cv2.resize(blurred, thumb_size)
            border_color = (0, 0, 255) 
            
            if not focused:
                focused = True
                count += 1
                
            # Implementation: Restore access if the user becomes unfocused
            if not can_speak:
                voice_assistant.speak("You are unfocused! Speaking access is now removed until you focus again.")
                can_speak = True # Restore access for the next focused instance
                
            unfocused_time = time.time() - last_focus_time
            
            label = f"UNFOCUSED - {int(unfocused_time)}s / {UNFOCUS_TIMEOUT}s"
            label_color = (0, 0, 255)
            
            # --- AUTOMATIC EXIT CONDITION ---
            if unfocused_time >= UNFOCUS_TIMEOUT:
                cv2.destroyAllWindows()
                print("Face unfocused for 10 seconds. Exiting Unfocus Count Mode.")
                return 
                
        # --- DISPLAY LOGIC ---
        thumbnail_with_border = cv2.copyMakeBorder(
            thumbnail, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=border_color
        )
        cv2.putText(thumbnail_with_border, label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, label_color, 2)

        h_thumb, w_thumb, _ = thumbnail_with_border.shape
        x_offset = frame.shape[1] - w_thumb - 10
        y_offset = 10
        frame[y_offset:y_offset+h_thumb, x_offset:x_offset+w_thumb] = thumbnail_with_border

        cv2.imshow('Face Detection - bramii', frame)

        if cv2.waitKey(1) == 49: # Exit on '1' key press
            break

    webcam.release()
    cv2.destroyAllWindows()