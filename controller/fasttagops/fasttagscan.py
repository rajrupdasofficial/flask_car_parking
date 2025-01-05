import cv2
from pyzbar.pyzbar import decode
import numpy as np

# Initialize video capture object
cap = cv2.VideoCapture(0)

# Set higher resolution for the video capture
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Failed to grab frame")
        break

    # Preprocess the frame: convert to grayscale and apply Gaussian blur
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)

    # Decode barcodes in the processed frame
    decoded_objects = decode(blurred_frame)

    for obj in decoded_objects:
        # Get the decoded data
        info_str = obj.data.decode('utf-8')  # Decode bytes to string
        dtype_str = obj.type
        
        print(f"Decoded Info: {info_str}, Type: {dtype_str}")
        
        # Display information on the frame
        cv2.putText(frame, f"{info_str} ({dtype_str})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Draw bounding box around detected barcode
        points = obj.polygon
        if len(points) == 4:  # Ensure it's a valid bounding box
            cv2.polylines(frame, [np.array(points)], isClosed=True, color=(0, 255, 0), thickness=2)

    # Show the resulting frame with detected barcodes
    cv2.imshow('Barcode Scanner', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()