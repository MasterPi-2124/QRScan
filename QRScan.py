import cv2
import pyzbar.pyzbar as pyzbar
from datetime import datetime
import time

# width = 2592
# height = 1944

PERIOD = 20 # maaximum off 20 sec

camera = cv2.VideoCapture(0)
# camera.set(3,width)
# camera.set(4,height)
data = {}

def decodeCam(image):
  global data
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  barcodes = pyzbar.decode(gray)
  for barcode in barcodes:
      barcodeData = barcode.data.decode()
      barcodeType = barcode.type
      data = {"date": str(datetime.now()), "data": barcodeData, "type": barcodeType}
  
  return data

def main():
  try:
    start_time = time.time()
    while True:
    # Read current frame
      ret, frame = camera.read()
      data = decodeCam(frame)
      if data != {}:
        break
      if (time.time() - start_time >= PERIOD):
        break
    # When the code is stopped the below closes all the applications/windows that the above has created
    camera.release()
    cv2.destroyAllWindows()
    return data

  except KeyboardInterrupt:
    print('interrupted!')
