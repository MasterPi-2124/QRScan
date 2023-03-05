import cv2
import pyzbar.pyzbar as pyzbar
from datetime import datetime

#width = 2592
#height = 1944

camera = cv2.VideoCapture(0)
#camera.set(3,width)
#camera.set(4,height)

def decodeCam(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    barcodes = pyzbar.decode(gray)
    for barcode in barcodes:
        barcodeData = barcode.data.decode()
        barcodeType = barcode.type
        print("["+str(datetime.now())+"] Type:{} | Data: {}".format(barcodeType, barcodeData))
        data = {
          "date": str(datetime.now()),
          "data": barcodeData
        }
        print(barcodeData)
        

try:
  # Read current frame
  ret, frame = camera.read()
  im=decodeCam(frame)
  cv2.imshow("code detector", frame)
    
  # When the code is stopped the below closes all the applications/windows that the above has created
  camera.release()
  cv2.destroyAllWindows()

except KeyboardInterrupt:
  print('interrupted!')
