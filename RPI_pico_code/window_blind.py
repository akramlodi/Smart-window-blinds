import machine
import network
import usocket as socket
import utime as time
import _thread
import json 

#define constants
threshold_brightness = 2
threshold_range = 0.5
conversion_factor = 3.3 / 65535
brightness_factor = conversion_factor * 100

# Define needed ADC pins and Red LED (in this code Red LED is sometimes called as buzzer) pins
inside_photoresistor_pin = 26
outside_photoresistor_pin = 27
thermistor_pin = 28
redLED_pin = machine.Pin(15, machine.Pin.OUT)
redLED_status = "Off"

# Function to get the Red LED status
def get_redLED_status():
    return "On" if redLED_pin.value() == 1 else "Off"

def get_inside_status():
    return ((250 - inside_photoresistor_val)/250)

def get_outside_status():
    return ((250 - outside_photoresistor_val)/250)

def get_temperature_status():
    return temperature2

# Function to periodically check the ADC value and control the redLED
def check_adc_and_control_redLED():
    global redLED_status  # Declare redLED_status as global
    global inside_photoresistor_val
    global outside_photoresistor_val
    global temperature2
    adc1 = machine.ADC(inside_photoresistor_pin)
    adc2 = machine.ADC(outside_photoresistor_pin)
    adc3 = machine.ADC(thermistor_pin)
    
    while True:
        adc1_value = adc1.read_u16()
        inside_photoresistor_val = adc1_value * brightness_factor
        print("Inside Photoresistor Value:", inside_photoresistor_val)

        adc2_value = adc2.read_u16()
        outside_photoresistor_val = adc2_value * brightness_factor
        print("Outside Photoresistor Value:", outside_photoresistor_val)

        # just to check if its working
        adc3_value = adc3.read_u16()
        thermistor_val = adc3_value * conversion_factor
        temperature = 27-(thermistor_val - 0.706)/0.001721 
        print("Thermistor Value:", temperature)

        sensor_temp = machine.ADC(4)
        reading = sensor_temp.read_u16() * conversion_factor
        temperature2 = 27 - (reading - 0.706)/0.001721
        print(temperature2)

        if (((inside_photoresistor_val - outside_photoresistor_val) < 50) and (outside_photoresistor_val < 100)):
            print("Brightness ratio met, turning on blinds")
            redLED_pin.on()
            while True:
                adc2_value = adc2.read_u16()
                outside_photoresistor_val = adc2_value * brightness_factor
                print("Outside Photoresistor Value:", outside_photoresistor_val)
                redLED_pin.on()
                if outside_photoresistor_val > 100:
                    redLED_pin.off()
                    break
                time.sleep(1)
        else:
            print("Outside brightness ratio, turning off blinds")
            redLED_pin.off()

        redLED_status = get_redLED_status()  # Update redLED_status
        print("Red LED Status:", redLED_status)

        time.sleep(1)

# Create a network connection
ssid = 'SMART_BLINDS'       #Set access point name 
password = '69420'      #Set your access point password
ap = network.WLAN(network.AP_IF)
ap.config(essid=ssid, password=password)
ap.active(True)            #activating

while ap.active() == False:
    pass
print('Connection is successful')
print(ap.ifconfig())

# Define HTTP response
def web_page():
    redLED_status = get_redLED_status()
    buzzer_color = "red" if redLED_status == "On" else "gray"
    
    html = """<html><head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <!-- Title of the webpage -->
        <title>Smart Window blinds</title>
    
    <!-- Internal CSS styles -->
    <style>

    h1 { 
        margin-top: 10px;
        color: #111; 
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 50px; font-weight: bold; 
        letter-spacing: -1px; line-height: 1; 
        text-align: center;
        background-color: #3AB54A;
        border-radius: 10px;
    }

    .card {
        margin: 10px;
    }

    .btn-disable {
        background-color: black;
        color: white;
        border-radius: 5px;
        height: 35px;
        border: none;
        width: 80px
    }
    .btn-activate {
        background-color: green;
        color: white;
        border-radius: 5px;
        height: 35px;
        width: 80px;
        border: none;
    }

    .color_activation {
        color: green;
    }
    .card {
    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    width: 20%;
    margin-left: 10px;
    margin-top: 10px;
    border-radius: 10px; 
    }

    .container {
    padding:  16px;
    }

    .sensors-container {
    display: flex;
    flex-direction: row;
    align-items: center;
    }

    .button {
            display: inline-block;
            background-color: #4CAF50;
            border: none;
            border-radius: 4px;
            color: white;
            padding: 16px 40px;
            text-decoration: none;
            font-size: 30px;
            margin: 2px;
            cursor: pointer;
        }
        
    .button2 {
        background-color: #555555;
    }

    .circle {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: inline-block;
        margin-left: 10px;
    }

    </style>
    <script>
      function updateStatus() {
          var xhr = new XMLHttpRequest();
          xhr.onreadystatechange = function() {
              if (xhr.readyState == 4 && xhr.status == 200) {
                  var data = JSON.parse(xhr.responseText);
                  document.getElementById("RedLEDStatus").innerHTML = data.RedLEDStatus;
                  var buzzerColor = data.RedLEDStatus === "On" ? "red" : "gray";
                  document.getElementById("buzzerIndicator").style.backgroundColor = buzzerColor;
              }
          };
          xhr.open("GET", "/status", true);
          xhr.send();
      }
      setInterval(updateStatus, 1000); // Refresh every 1 second
  </script>

    </head>

    <body>
    <h1>SMART WINDOW BLINDS</h1>
        <!-- Card for Window Blind status -->

        <div class="card">
            <div class="container">
            <h4>Window Blinds Status</h4> 
            <p class="color_activation">Activated</p> 
            <button type="button" class="btn-activate">Activate</button>
            <button type="button" class="btn-disable">Disable</button>
            </div>
        </div>

        <p>RedLED Status: <strong id="RedLEDStatus">""" + redLED_status + """</strong><div class="circle" id="buzzerIndicator" style="background-color: """ + buzzer_color + """;"></div></p>

        <div class="sensors-container">
        <div class="card">
            <img src="light sensor.jpg" alt="Avatar" style="width:100%">
            <div class="container">
            <h4>Light sensor internal</h4> 
            <p id="light_sensor_internal">""" + str(get_inside_status()) + """</p> 
            </div>
        </div>

        <div class="card">
            <img src="heat sensor.jpg" alt="Avatar" style="width:100%">
            <div class="container">
            <h4>Temperature sensor</h4> 
            <p id="temperature_sensor">""" + str(get_temperature_status()) + """</p> 
            </div>
        </div>

        <div class="card">
            <img src="light sensor.jpg" alt="Avatar" style="width:100%">
            <div class="container">
            <h4>Light sensor external</h4> 
            <p id="light_sensor_external">""" + str(get_outside_status()) + """</p> 
            </div>
        </div>
        </div>


    </body>
    </html>"""
    return html

# Function to get the current status
def get_status():
    status = {
        "RedLEDStatus": redLED_status,
        "InsideBrightness": get_inside_status(),
        "OutsideBrightness": get_outside_status(),
        "Temperature": get_temperature_status(),
    }
    return json.dumps(status)

# Start the ADC monitoring function in a separate thread
_thread.start_new_thread(check_adc_and_control_redLED, ())

# Create a socket server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    if request:
        request = str(request)
        print('Content = %s' % request)
        buzzer_on = request.find('/?redLED_pin=on')  # redLED_pin is the Red LED
        buzzer_off = request.find('/?redLED_pin=off')

    if buzzer_on == 6:
        print('Red LED ON')
        redLED_pin.value(1)
    elif buzzer_off == 6:
        print('Red LED OFF')
        redLED_pin.value(0)

    if request.find("/status") == 6:
        response = get_status()
        conn.send("HTTP/1.1 200 OK\n")
        conn.send("Content-Type: application/json\n")
        conn.send("Connection: close\n\n")
        conn.sendall(response)
    else:
        response = web_page()
        conn.send("HTTP/1.1 200 OK\n")
        conn.send("Content-Type: text/html\n")
        conn.send("Connection: close\n\n")
        conn.sendall(response)
    conn.close()
