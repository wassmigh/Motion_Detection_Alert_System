import machine
import time
import network
import urequests

pir_pin = machine.Pin(36, machine.Pin.IN) 
led_pin = machine.Pin(22, machine.Pin.OUT) 

# Wi-Fi network credentials
SSID = "your router SSID"  # Replace with your Wi-Fi network name
PASSWORD = "your router password"  # Replace with your Wi-Fi password

# Twilio credentials for sending SMS notifications
TWILIO_SID = "your twilio sid"  # Replace with your Twilio SID
TWILIO_AUTH_TOKEN = "your twilio auth token"  # Replace with your Twilio Auth Token
FROM_NUMBER = "twilio number"  # Replace with your Twilio phone number
TO_NUMBER = "your number"  # Replace with the phone number to receive alerts

# Function to connect the ESP32/ESP8266 device to the Wi-Fi network
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)  
    wlan.active(True)  
    wlan.connect(SSID, PASSWORD)  
    while not wlan.isconnected(): 
        time.sleep(1)  
        print("Connexion en cours...")  
    print("Connecté au réseau Wi-Fi")  
    print("Adresse IP:", wlan.ifconfig()[0])  

# Function to trigger an alert when motion is detected
def alert():
    print("Intrusion détectée !") 
    start_time = time.time()  
    while time.time() - start_time < 6:  
        led_pin.value(1) 
        time.sleep(1)  
        led_pin.value(0) 
        time.sleep(1)  

# Function to send an SMS alert using Twilio API
def send_sms():
    url = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json".format(TWILIO_SID)  
    payload = "To={}&From={}&Body={}".format(TO_NUMBER, FROM_NUMBER, "Intrusion Alert: Motion detected!")
    response = urequests.post(url, data=payload, auth=(TWILIO_SID, TWILIO_AUTH_TOKEN))
    print(response.text)  
    response.close() 

connect_wifi()

# Variable to store the last alert time, preventing too frequent alerts
last_alert_time = 0  

# Callback function triggered when motion is detected by the PIR sensor
def pir_callback(pin):
    global last_alert_time 
    current_time = time.time() 
    # Ensure alerts are sent no more than once every 10 seconds
    if current_time - last_alert_time > 10:  
        alert()  
        send_sms() 
        last_alert_time = current_time  

# Set up the PIR sensor to trigger the callback function when motion is detected
pir_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=pir_callback)

