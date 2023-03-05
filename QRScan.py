import cv2
import pyzbar.pyzbar as pyzbar
from datetime import datetime

# width = 2592
# height = 1944

camera = cv2.VideoCapture(0)
# camera.set(3,width)
# camera.set(4,height)
data = {}

def decodeCam(image):
  global data
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  barcodes = pyzbar.decode(gray)
  print(barcodes)
  for barcode in barcodes:
      barcodeData = barcode.data.decode()
      barcodeType = barcode.type
      data = {"date": str(datetime.now()), "data": barcodeData, "type": barcodeType}
  
  return data

def main():
  try:
    while True:
    # Read current frame
      ret, frame = camera.read()
      data = decodeCam(frame)
      if data != {}:
        break
    # When the code is stopped the below closes all the applications/windows that the above has created
    camera.release()
    cv2.destroyAllWindows()
    return data

  except KeyboardInterrupt:
    print('interrupted!')
