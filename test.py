import cv2
from cam import Camera

cam = Camera()
while True:
    frame = cam.get_frame()
    
    cv2.imshow("OBS Test", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
