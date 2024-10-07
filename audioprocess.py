#Declaring all the libraries
import wave
import pyaudio
import subprocess
import speech_recognition as sr
import gpiod
import time
import RPi.GPIO
# To handle both incoming and outgoing signals
chip = gpiod.Chip('gpiochip4')

# activating the line for red, green, and blue led.
red_led = chip.get_line(17)
green_led = chip.get_line(27)
blue_led = chip.get_line(22)

red_led.request(consumer = "LED", type = gpiod.LINE_REQ_DIR_OUT)
green_led.request(consumer = "LED", type = gpiod.LINE_REQ_DIR_OUT)
blue_led.request(consumer = "LED", type = gpiod.LINE_REQ_DIR_OUT)

# This method checks if the wanted device is connected to the raspberry pi via bluetooth
def check_bluetooth(device_name):
	try:
		result = subprocess.check_output(['pactl list short sinks'], shell = True, text = True)
		devices = result
		
		if device_name in devices:
			print(f"Device: {device_name} found.")
			return True
		return False
	except Exception as e:
		print(f"Error checking bluetooth devices: {e}")
		return False

# Records audio to the passed filename for the duration of 5 seconds
def record_audio(filename, duration = 5):
	audio = pyaudio.PyAudio()
	stream = audio.open(format = pyaudio.paInt16, channels= 1, rate = 44100, input=True, frames_per_buffer=1024)
	
	print("Recording")
	frames=[]
	
	for _ in range(int(44100/1024*duration)):
		data = stream.read(1024)
		frames.append(data)
		
	print("Finished Recording")
	
	
	stream.stop_stream()
	stream.close()
	audio.terminate()
	
	with wave.open(filename, 'wb') as wf:
		wf.setnchannels(1)
		wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
		wf.setframerate(44100)
		wf.writeframes(b''.join(frames))

# This method converts the wav file into text file. The wav file is passed after record_audio method.
def convert_wav_to_text(wav_file):
	recognizer = sr.Recognizer()
	
	with sr.AudioFile(wav_file) as source:
		audio_data = recognizer.record(source)
	
	try:
		text = recognizer.recognize_google(audio_data)
		return text
	except sr.UnknownValueError:
		return "Google Speech Recognition could not understand the audio."
	except sr.RequestError as e:
		return f"Could not request results from Google Speech Recognition Service, {e}"

# Toggle LED function which called in a while loop. This function take input_text as a parameter and finds certain phrases from the input text. If those are phrase are found respective led is glown.
def Toggle_LED(input_text):
	if "red led on" in input_text.lower():
		red_led.set_value(1)
		green_led.set_value(0)
		blue_led.set_value(0)
		time.sleep(1)
	if "green led on" in input_text.lower():
		red_led.set_value(0)
		green_led.set_value(1)
		blue_led.set_value(0)
		time.sleep(1)	
	if "blue led on" in input_text.lower():
		red_led.set_value(0)
		green_led.set_value(0)
		blue_led.set_value(1)
		time.sleep(1)	
	if "shazam" in input_text.lower():
		red_led.set_value(1)
		green_led.set_value(1)
		blue_led.set_value(1)
		time.sleep(1)
	input_text = ""
# The given input_text file is emptied after any one of the phrase is successfully captured and recognized. This is to ensure that only recent voice inputs are updated into the text. Thus, it does not consider past inputs and refreshes the string after every recording.

try:
	while True:
		audio_filename = "recorded_audio.wav"
		if check_bluetooth("08_E4_DF_B8_5F_4A.1") == True:
			record_audio(audio_filename, duration=5)
			text_out = convert_wav_to_text(audio_filename)
			Toggle_LED(text_out)
			print(text_out)
		else:
			print("Not Connected")
			break;
except KeyboardInterrupt:
	print("Process Ended")
	RPi.GPIO.cleanup()
	
		
