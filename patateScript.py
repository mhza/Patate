from time import sleep
import RPi.GPIO as GPIO
from picamera import PiCamera
from picamera.array import PiRGBArray
from keras.models import load_model
import numpy as np
#####################################

# Load Model:
model = load_model('model-1x3.h5')
print("Model Loaded")

#init GPIO with BCM numberings
GPIO.setmode(GPIO.BCM)
#init every used pins
GPIO.setup(12, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)

#set controls
MOT1v = GPIO.PWM(12, 50)
MOT1f = 19
MOT1b = 13
MOT2v = GPIO.PWM(16, 50)
MOT2f = 21
MOT2b = 20

# Video settings
camera = PiCamera()
camera.resolution = (160, 128)
camera.framerate = 60
camera.hflip = True
camera.vflip = True
rawCapture = PiRGBArray(camera, size=(160, 128))

# Starting loop
print("Ready ! (press Ctrl+C to start/stop)...")
try:
  while True:
    pass
except KeyboardInterrupt:
  pass

# Init engines
GPIO.output(MOT1f, 1)
GPIO.output(MOT2f, 1)
MOT1v.start(0)
MOT2v.start(0)
# Init speeds and memory
speed1 = 25
speed2 = 25
last = 1

try:
##  # Capture frames
  for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
##  # Grab Numpy Array
    img = frame.array
    image = np.array([img[50:, :, :]])
##  # Model prediction
    preds = model.predict(image)
    preds = np.argmax(preds, axis=1)
##  # Filter
    if (last == 0 and preds == 2) or (last == 2 and preds == 0):
        preds == 3
##  # Action
    if preds == 0:
        GPIO.output(MOT1f, 0)
        GPIO.output(MOT1b, 1)
        GPIO.output(MOT2f, 1)
        GPIO.output(MOT2b, 0)
        v1 = speed2
        v2 = speed2
    elif preds == 1:
        GPIO.output(MOT1f, 1)
        GPIO.output(MOT1b, 0)
        GPIO.output(MOT2f, 1)
        GPIO.output(MOT2b, 0)
        v1 = speed1
        v2 = speed1
    elif preds == 2:
        GPIO.output(MOT1f, 1)
        GPIO.output(MOT1b, 0)
        GPIO.output(MOT2f, 0)
        GPIO.output(MOT2b, 1)
        v1 = speed2
        v2 = speed2
    elif preds == 3:
        GPIO.output(MOT1f, 0)
        GPIO.output(MOT1b, 1)
        GPIO.output(MOT2f, 0)
        GPIO.output(MOT2b, 1)
        v1 = speed2
        v2 = speed2
    MOT1v.ChangeDutyCycle(v1)
    MOT2v.ChangeDutyCycle(v2)
    print(str(preds))
##  # Set memory
    last = preds
##  # Clear the stream
    image = np.delete(image, 0)
    rawCapture.truncate(0)
except KeyboardInterrupt:
  pass

# Stop the machine and release GPIO Pins
MOT1v.stop(0)
MOT2v.stop(0)
print("Stop")
GPIO.cleanup()
