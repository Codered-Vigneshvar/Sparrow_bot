import tkinter as tk
import speech_recognition as sr
import os
import pygame
import openai
import time




# Set up OpenAI API key
openai.api_key = "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"


# Function to listen to user's speech for a maximum of 20 seconds
def listen_to_user():
    recognizer = sr.Recognizer()
    with sr.Microphone() as mic:
        update_conversation("Listening...")
        root.update()
        print("Listening...")
        recognizer.adjust_for_ambient_noise(mic, duration=0.3)
        audio = recognizer.listen(mic, timeout=20)
        update_conversation("Finished listening.")
        root.update()
        print("Finished listening.")
        try:
            return recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            return ""  # Return empty string if no speech is detected or not recognized
        except sr.RequestError:
            return ""  # Return empty string if there is an error with the speech recognition service


# Function to generate a reply using OpenAI's Chat API
def reply(prompt):
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                              messages=[{"role": "system", "content": "You are a helpful assistant."},
                                                        {"role": "user", "content": prompt}])
    return completion.choices[0].message.content


# Function to speak the given text
def speak(data):
    voice = 'en-US-SteffanNeural'
    command = f'edge-tts --voice "{voice}" --text "{data}" --write-media "data.mp3"'
    os.system(command)

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("data.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


# Function to display the conversation in the GUI and center it on the page
def update_conversation(text):
    conversation_label.config(text=text)
    conversation_label.place(relx=0.5, rely=0.5, anchor="center")

    # Adjust the conversation label's size to fit the text
    conversation_label.update_idletasks()
    label_width = conversation_label.winfo_width()
    label_height = conversation_label.winfo_height()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    max_label_width = window_width - 20  # Leave some margin
    max_label_height = window_height - 20
    if label_width > max_label_width or label_height > max_label_height:
        scale_factor = min(max_label_width / label_width, max_label_height / label_height)
        new_font_size = int(conversation_label['font'].actual()['size'] * scale_factor)
        conversation_label.config(font=("Helvetica", new_font_size))


# Function to display the assistant's reply line by line with a dynamic delay
def display_reply_line_by_line(speak_text):
    lines = speak_text.split('\n')
    for line in lines:
        update_conversation("Sparrow Bot: " + line)
        try:
            speak(line)
        except Exception as e:
            print(e)
            continue
        time.sleep(len(line) * 0.04)  # Adjust the speed of reading


# Function to handle asking if there are further questions
def ask_further_questions():
    update_conversation("Sparrow Bot: Do you have any further questions?")
    speak("Do you have any further questions?")
    while True:
        user_speech = listen_to_user()
        if user_speech:
            speak_text = reply(user_speech)
            display_reply_line_by_line(speak_text)
            break


# Function to handle the "Start Listening" button click event
def start_listening():
    # Disable the "Start Listening" button while listening
    start_button.config(state=tk.DISABLED)

    # Initial greeting
    speak_t = "Hello, I am Sparrow Bot. How can I help you today?"
    display_reply_line_by_line(speak_t)

    while True:
        # Listen to user's speech
        user_speech = listen_to_user()

        # If no speech is detected or there is an error, ask again
        if not user_speech:
            ask_further_questions()
            continue

        # Use the user's speech as a prompt to reply back using OpenAI
        speak_text = reply(user_speech)
        display_reply_line_by_line(speak_text)

        # Enable the "Start Listening" button after processing the request
        start_button.config(state=tk.NORMAL)


# Create the GUI window
root = tk.Tk()
root.title("Sparrow Bot")

# Add minimize and exit buttons to the window
root.attributes("-fullscreen", True)
root.protocol("WM_DELETE_WINDOW", root.destroy)

# Create a label to display the conversation
conversation_label = tk.Label(root, text="", font=("Helvetica", 20), wraplength=800, justify="center")
conversation_label.pack(pady=100)

# Create the "Start Listening" button
start_button = tk.Button(root, text="Start Listening", font=("Helvetica", 20), command=start_listening)
start_button.pack()

# Start the GUI event loop
root.mainloop()

