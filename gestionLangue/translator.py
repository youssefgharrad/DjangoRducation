import os
import django

# Set the Django settings module before any Django imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'firstProject.settings')
django.setup()

from django.core.files.base import ContentFile

import gradio as gr
import assemblyai as aai
from translate import Translator
import uuid
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from pathlib import Path
import shutil
from gestionLangue.models import InputTranslator, OutputTranslator  
from django.core.files import File
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import get_user_model


# from accounts.models import CustomUser

# AUTH_USER_MODEL = 'accounts.CustomUser'  


User = get_user_model()


# Define directories for saving files
INPUT_TEXT_DIR = Path("gestionLangue/input_text")
INPUT_VOICE_DIR = Path("gestionLangue/input_voice")
OUTPUT_TEXT_DIR = Path("gestionLangue/output_text")
OUTPUT_VOICE_DIR = Path("gestionLangue/output_voice")

# Create directories if they don't exist
for directory in [INPUT_TEXT_DIR, INPUT_VOICE_DIR, OUTPUT_TEXT_DIR, OUTPUT_VOICE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Available languages for translation
LANGUAGES = {
    "Russian": "ru",
    "Turkish": "tr",
    "Swedish": "sv",
    "German": "de",
    "Spanish": "es",
    "Japanese": "ja",
}

def voice_to_voice(audio_file, selected_language, user):
    # Ensure the input and output directories exist
    os.makedirs(INPUT_VOICE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_TEXT_DIR, exist_ok=True)
    
    # Save the uploaded audio file
    saved_audio_path = INPUT_VOICE_DIR / f"{uuid.uuid4()}.wav"
    
    # Handle audio file saving
    if isinstance(audio_file, str) and os.path.isfile(audio_file):
        shutil.copy(audio_file, saved_audio_path)
        print(f"Saved uploaded audio file to {saved_audio_path}")
    else:
        raise ValueError("Invalid audio file provided.")

    # Transcribe audio
    transcript = transcribe_audio(str(saved_audio_path))

    if transcript.status == aai.TranscriptStatus.error:
        raise gr.Error(transcript.error)
    else:
        transcript_text = transcript.text

    # Translate text to the selected language
    translation = translate_text(transcript_text, selected_language)
    
    # Save the translated text as a file
    translated_text_file_path = save_text(translation, OUTPUT_TEXT_DIR)
    
    # Generate speech from the translated text
    translated_audio_file_name = text_to_speech(translation)

    # Save to database with proper file handling
    try:
        with open(saved_audio_path, 'rb') as audio_file_obj:
            input_translator = InputTranslator.objects.create(
                user=user,
                input_voice=File(audio_file_obj)
            )
        
        with open(translated_audio_file_name, 'rb') as translated_audio_file_obj:
            output_translator = OutputTranslator.objects.create(
                input_translator=input_translator,
                output_text=translation,
                output_voice=File(translated_audio_file_obj)
            )
    except Exception as e:
        raise Exception(f"Failed to save to database: {e}")

    return translated_audio_file_name, translation




def text_to_text(text, selected_language, user):
    # Save the input text as a file
    save_text(text, INPUT_TEXT_DIR)

    # Translate text to the selected language
    translation = translate_text(text, selected_language)

    # Save the translated text as a file
    save_text(translation, OUTPUT_TEXT_DIR)

    # Save to database
    input_translator = InputTranslator.objects.create(
        user=user,
        input_text=text
    )
    
    output_translator = OutputTranslator.objects.create(
        input_translator=input_translator,
        output_text=translation
    )

    return None, translation




# Function to transcribe audio using AssemblyAI
def transcribe_audio(audio_file):
    aai.settings.api_key = "30199d1616274b6cb8c61751220e4863"
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    return transcript

# Function to translate text to the selected language
def translate_text(text: str, lang_code: str):
    translator = Translator(from_lang="en", to_lang=lang_code)
    return translator.translate(text)

# Function to generate speech
def text_to_speech(text: str):
    client = ElevenLabs(api_key="sk_5fcd08716b3d0947c892123b49e82ab942fb3d9f0d316bd5")
    
    response = client.text_to_speech.convert(
        voice_id="Xb7hH8MSUJpSbSDYk0k2",
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=0.8,
            style=0.5,
            use_speaker_boost=True,
        ),
    )

    save_file_path = OUTPUT_VOICE_DIR / f"{uuid.uuid4()}.mp3"

    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"{save_file_path}: A new audio file was saved successfully!")
    return save_file_path

# Function to save text to a file
def save_text(content, directory):
    text_file_path = directory / f"{uuid.uuid4()}.txt"
    with open(text_file_path, "w") as file:
        file.write(content)
    print(f"Text saved to {text_file_path}")
    return text_file_path



def get_authenticated_user(session_id):
    """Retrieve the authenticated user from the given session ID."""
    session = SessionStore(session_key=session_id)
    
    if session.exists(session_id):
        print(f"Session exists for ID: {session_id}")  # Debug statement
        user_id = session.get('_auth_user_id')
        print(f"Retrieved user ID from session: {user_id}")  # Debug statement
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                print(f"User found: {user}")  # Debug statement
                return user
            except User.DoesNotExist:
                print("User does not exist.")
                return None
        else:
            print("No user ID found in session.")
            return None
    else:
        print("Session does not exist.")
        return None

def extract_session_id(cookies):
    """Extract the session ID from cookies."""
    # Assuming cookies is a dictionary-like object
    return cookies.get('sessionid')

def launch_gradio_interface(cookies):
    session_id = extract_session_id(cookies)  # Automatically extract session ID from cookies
    print(f"Extracted session ID: {session_id}")  # Debug statement
    user = get_authenticated_user(session_id)  # Get the user from session ID
    
    if user is None:
        print("User not authenticated.")  # Debug statement
    else:
        print(f"Authenticated user: {user}")  # Debug statement

    with gr.Blocks() as demo:
        gr.Markdown("## Record or Enter Text in English to Receive Voice or Text Translations.")

        translation_mode = gr.Radio(
            choices=["Voice Translation", "Text Translation"],
            value="Voice Translation",
            label="Choose Translation Mode"
        )

        language_selector = gr.Dropdown(
            label="Select Language",
            choices=list(LANGUAGES.keys()),
            value="Spanish"
        )

        # Define audio and text input areas with buttons below each
        with gr.Column():
            # Audio Input Area
            with gr.Column(visible=True) as voice_input_area:
                audio_input = gr.Audio(sources=["microphone"], type="filepath", show_download_button=True, label="Record Voice")
                with gr.Row():
                    submit_button_audio = gr.Button("Submit", variant="primary")
                    clear_button_audio = gr.Button("Clear", variant="secondary")
            
            # Text Input Area
            with gr.Column(visible=False) as text_input_area:
                text_input = gr.Textbox(label="Enter Text")
                with gr.Row():
                    submit_button_text = gr.Button("Submit", variant="primary")
                    clear_button_text = gr.Button("Clear", variant="secondary")

        output_audio = gr.Audio(label="Translated Audio", interactive=False)
        output_text = gr.Markdown(label="Translated Text")

        # Toggle input fields based on translation mode
        def update_inputs(mode):
            return (gr.update(visible=(mode == "Voice Translation")), 
                    gr.update(visible=(mode == "Text Translation")))

        translation_mode.change(
            update_inputs,
            inputs=translation_mode,
            outputs=[voice_input_area, text_input_area]
        )

        def process_translation(mode, audio, text, lang):
            if user is not None:
                if mode == "Voice Translation":
                    return voice_to_voice(audio, lang, user)
                else:
                    return text_to_text(text, lang, user)
            else:
                print("User not authenticated.")
                return None, "User not authenticated."

        # Link Submit buttons to process translation
        submit_button_audio.click(
            fn=process_translation,
            inputs=[translation_mode, audio_input, text_input, language_selector],
            outputs=[output_audio, output_text],
            show_progress=True
        )

        submit_button_text.click(
            fn=process_translation,
            inputs=[translation_mode, audio_input, text_input, language_selector],
            outputs=[output_audio, output_text],
            show_progress=True
        )

        # Clear output when Clear buttons are clicked
        clear_button_audio.click(
            fn=lambda: (None, ""),
            inputs=None,
            outputs=[output_audio, output_text]
        )

        clear_button_text.click(
            fn=lambda: (None, ""),
            inputs=None,
            outputs=[output_audio, output_text]
        )

    demo.launch()

# Example usage: Launch the Gradio interface and simulate passing cookies
if __name__ == "__main__":
    # Simulated cookies - replace with actual cookies fetching logic if needed
    simulated_cookies = {
        'sessionid': '4i2uyk9ec43cnopngz7jxw0bt2t04y1r'  # Replace with actual session ID extraction
    }
    launch_gradio_interface(simulated_cookies)