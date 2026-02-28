import cv2
from pyzbar.pyzbar import decode

def scan_qr_from_camera():
    """
    Opens the computer camera, scans QR codes in real-time,
    draws a rectangle around detected QR, and returns the QR content.
    """
    cap = cv2.VideoCapture(0)

    # Create a named window and keep it on top
    cv2.namedWindow("QR Scanner", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("QR Scanner", cv2.WND_PROP_TOPMOST, 1)

    qr_content = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        decoded_objects = decode(frame)
        for obj in decoded_objects:
            qr_content = obj.data.decode("utf-8")
            # Draw a rectangle around QR
            pts = obj.polygon
            pts = [(p.x, p.y) for p in pts]
            for i in range(len(pts)):
                cv2.line(frame, pts[i], pts[(i + 1) % len(pts)], (0, 255, 0), 3)
            break  # Stop after first QR

        cv2.imshow("QR Scanner", frame)

        key = cv2.waitKey(1) & 0xFF
        # Press 'q' to quit manually
        if key == ord('q') or qr_content:
            break

    cap.release()
    cv2.destroyAllWindows()  # Close window properly
    return qr_content