import streamlit as st
import pyttsx3
import speech_recognition as sr
import threading
import time
from gtts import gTTS
from tempfile import NamedTemporaryFile
import os
from Main import model as dec
import pydub

code = dec.code
df = dec.df

if code in df['Code'].values:
    questions = df[df['Code'] == code]['Question'].values[:5]
    answers = df[df['Code'] == code]['Answer'].values[:5]
else:
    st.write("No matching code found in the DataFrame.")

# Set the speech recognition microphone source
# You may need to adjust this depending on your system's configuration
microphone_source = sr.Microphone(device_index=1)


# Initialize the speech recognition engine once
recognizer = sr.Recognizer()

recognizer_started = False


def start_recognizer():
    global recognizer_started
    with microphone_source as source:
        recognizer.adjust_for_ambient_noise(source)
        recognizer_started = True


def speak(text):
    """Speaks the provided text using pyttsx3."""
    with NamedTemporaryFile(suffix=".wav", delete=False) as tts_file:
        tts = gTTS(text=text, lang="en")
        tts.save(tts_file.name)
        audio = pydub.AudioSegment.from_file(tts_file.name)
        audio.export(tts_file.name, format="wav")
        st.audio(tts_file.name, format="audio/wav")
        # os.remove(tts_file.name)


def listen():
    """Listens to user speech and returns the recognized text."""
    if not recognizer_started:
        start_recognizer()

    try:
        with microphone_source as source:
            st.write("Listening...")
            audio = recognizer.listen(source)
            st.write("Processing speech...")
            text = recognizer.recognize_google(audio)
            st.write("Recognized speech:", text)
            return text
    except sr.UnknownValueError:
        st.write("Speech recognition could not understand audio.")
        return ""
    except sr.RequestError:
        st.write("Could not connect to speech recognition service.")
        return ""



def interview():
    """Conducts an interview by asking questions and recording responses."""
    st.write("Welcome to the interview! Please answer the following questions:")
    answers_given = []

    for i, question in enumerate(questions):
        st.write("Question:", question)
        speak(question)  # Call the speak function with the question
        time.sleep(2)  # Pause for 2 seconds to allow the user to answer
        response = listen()
        while response == "":
            response = listen()  # Wait until the answer is finished
        answers_given.append(response)

    speak("Thank you for your answers. The interview is complete.")

    # Print the user's responses
    for i, answer in enumerate(answers_given):
        st.write("Question:", questions[i])
        st.write("Answer:", answer)
        st.write()

    # Calculate accuracy
    correct_count = sum(answer == answer_given for answer, answer_given in zip(answers, answers_given))
    total_questions = len(questions)
    accuracy = (correct_count / total_questions) * 100
    st.write(f"Accuracy: {accuracy}%")


def main():
    st.title("Interview Application")
    interview()


if __name__ == "__main__":
    main()
