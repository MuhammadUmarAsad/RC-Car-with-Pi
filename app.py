# Import necessary libraries
import RPi.GPIO as GPIO
from flask import Flask, render_template, Response
import picamera
import io
import time

# Initialize Flask app
app = Flask(__name__)

# Configure GPIO pins
GPIO.setmode(GPIO.BCM)

# GPIO pins for motor control
motor_pin1 = 17 
motor_pin2 = 18  
motor_pin3 = 27
motor_pin4 = 22

# Setup GPIO pins as output
GPIO.setup(motor_pin1, GPIO.OUT)
GPIO.setup(motor_pin2, GPIO.OUT)
GPIO.setup(motor_pin3, GPIO.OUT)
GPIO.setup(motor_pin4, GPIO.OUT)

# Initialize PiCamera
# Camera = PiCamera()

# Function to stop the motors
def stop_motors():
    GPIO.output(motor_pin1, GPIO.LOW)
    GPIO.output(motor_pin2, GPIO.LOW)
    GPIO.output(motor_pin3, GPIO.LOW)
    GPIO.output(motor_pin4, GPIO.LOW)



# Function to move forward
def move_forward():
    GPIO.output(motor_pin1, GPIO.HIGH)
    GPIO.output(motor_pin2, GPIO.LOW)
    GPIO.output(motor_pin3, GPIO.HIGH)
    GPIO.output(motor_pin4, GPIO.LOW)

# Function to move backward
def move_backward():
    GPIO.output(motor_pin3, GPIO.LOW)
    GPIO.output(motor_pin4, GPIO.HIGH)
    GPIO.output(motor_pin1, GPIO.LOW)
    GPIO.output(motor_pin2, GPIO.HIGH)
    pass

# Function to turn left
def turn_left():
    GPIO.output(motor_pin1, GPIO.HIGH)
    GPIO.output(motor_pin4, GPIO.HIGH)
    GPIO.output(motor_pin2, GPIO.LOW)
    GPIO.output(motor_pin3, GPIO.LOW)

# Function to turn right
def turn_right():
    GPIO.output(motor_pin3, GPIO.HIGH)
    GPIO.output(motor_pin2, GPIO.HIGH)
    GPIO.output(motor_pin4, GPIO.LOW)
    GPIO.output(motor_pin1, GPIO.LOW)

def generate_frames():
    with picamera.PiCamera() as camera:
        # Set camera resolution as needed
        camera.resolution = (640, 480)
        time.sleep(2)

        while True:
            # Capture frames from the camera
            stream = io.BytesIO()
            camera.capture(stream, format='jpeg')
            camera.framerate = 60
            # Reset the stream position to the beginning
            stream.seek(0)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + stream.read() + b'\r\n')


# Flask routes
@app.route('/')
def index():
    return render_template('rc_car.html')

@app.route('/control/<direction>')
def control(direction):
    stop_motors()  # Stop the motors before any new movement
    if direction == 'forward':
        move_forward()
    elif direction == 'backward':
        move_backward()
    elif direction == 'left':
        turn_left()
    elif direction == 'right':
        turn_right()
    elif direction == 'stop':
        stop_motors()
    else:
        return 'Invalid direction'

    return f'Moving {direction}'

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Run the Flask app
if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0')
    finally:
        # Add this line before the GPIO cleanup in your script
        camera.close()
        GPIO.cleanup()
