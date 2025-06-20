import cv2
import numpy as np
import mediapipe as mp
from scipy.spatial import distance as dist

# Initialize Mediapipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Define the landmark indices for left and right eyes
LEFT_EYE_LANDMARKS = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_LANDMARKS = [33, 160, 158, 133, 153, 144]

# Drowsiness detection parameters
EAR_THRESHOLD = 0.25
CONSEC_FRAMES = 20  # Number of frames the eyes must be closed before drowsiness is detected
counter = 0
drowsy = False

# Open webcam
cap = cv2.VideoCapture(0)

def calculate_ear(eye):
    """Calculate the Eye Aspect Ratio (EAR)."""
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)




def sendSignal(val):
    if val==True:
        path = "/on" if on else "/off"
        try:
            r = requests.get(ESP_IP + path, timeout=1)
            print("Response:", r.text.strip())
        except requests.RequestException as e:
            print("Error:", e)


while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to RGB for Mediapipe processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Extract eye coordinates
            left_eye = [(int(face_landmarks.landmark[i].x * frame.shape[1]),
                         int(face_landmarks.landmark[i].y * frame.shape[0])) for i in LEFT_EYE_LANDMARKS]
            right_eye = [(int(face_landmarks.landmark[i].x * frame.shape[1]),
                          int(face_landmarks.landmark[i].y * frame.shape[0])) for i in RIGHT_EYE_LANDMARKS]

            # Compute EAR for both eyes
            left_EAR = calculate_ear(left_eye)
            right_EAR = calculate_ear(right_eye)
            avg_EAR = (left_EAR + right_EAR) / 2.0

            # Display EAR values
            cv2.putText(frame, f"EAR: {avg_EAR:.2f}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            # Draw eye contours
            cv2.polylines(frame, [np.array(left_eye, np.int32)], True, (0, 255, 0), 1)
            cv2.polylines(frame, [np.array(right_eye, np.int32)], True, (0, 255, 0), 1)

            # Drowsiness detection logic
            if avg_EAR < EAR_THRESHOLD:
                counter += 1
            else:
                counter = max(0, counter - 1)  # Decrease counter smoothly

            # Determine drowsiness status
            drowsy = counter >= CONSEC_FRAMES

    # Display drowsiness status
    status = "DROWSY: YES" if drowsy else "DROWSY: NO"
    if status:
        sendSignal(True)
    else:
        sendSignal(False)
    color = (0, 0, 255) if drowsy else (0, 255, 0)
    cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # Display frame counter
    cv2.putText(frame, f"Frames: {counter}/{CONSEC_FRAMES}",
                (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # Show the output frame
    cv2.imshow("Drowsiness Detection", frame)

    # Exit condition
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

