from django.http import JsonResponse
import gradio as gr
import threading
import assemblyai as aai
from translate import Translator
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import uuid
from django.shortcuts import render
from pathlib import Path
from .models import InputTranslator, OutputTranslator
from django.views.decorators.http import require_http_methods

# In context_processors.py
def user_context(request):
    return {
        'current_user': request.user,
    }

# Function to transcribe, translate, and convert text to speech
def voice_to_voice(audio_file):
    print("Received audio file:", audio_file)  # Debugging statement

    # Transcribe speech using AssemblyAI 
    transcription_response = transcribe_audio(audio_file)

    if transcription_response.status == aai.TranscriptStatus.error:
        raise gr.Error(transcription_response.error)
    
    transcript = transcription_response.text
    print("Transcription successful:", transcript)  # Debugging statement

    # Translate to multiple languages 
    translations = translate_text(transcript)

    # Generate speech for translations
    audio_paths = []
    for translation in translations:
        audio_path = text_to_speech(translation)
        audio_paths.append(audio_path)  # Append string path instead of Path object

    return tuple(audio_paths)

# Function to transcribe audio using AssemblyAI
def transcribe_audio(audio_file):
    aai.settings.api_key = "30199d1616274b6cb8c61751220e4863"  # Replace with your API key
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    return transcript

# Function to translate text
def translate_text(text):
    languages = ["es", "tr", "ja", "sv", "ru", "de"]  # Spanish, Turkish, Japanese, Swedish, Russian, German
    translations = []
    for lang in languages:
        translator = Translator(from_lang="en", to_lang=lang)
        translation = translator.translate(text)
        translations.append(translation)
    return translations

# Function to convert text to speech using ElevenLabs API
def text_to_speech(text):
    client = ElevenLabs(api_key="sk_5fcd08716b3d0947c892123b49e82ab942fb3d9f0d316bd5")  # Replace with your API key
    response = client.text_to_speech.convert(
        voice_id="Xb7hH8MSUJpSbSDYk0k2",  # Use your voice ID
        text=text,
        output_format="mp3_22050_32",
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.8)
    )
    
    # Generate a unique file name for the output MP3 file
    file_path = f"{uuid.uuid4()}.mp3"
    
    # Write the audio to a file
    with open(file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"Audio saved at: {file_path}")  # Debugging statement
    return file_path  # Return as string, not Path object

# Gradio Interface creation
def create_gradio_interface():
    with gr.Blocks() as demo:
        gr.Markdown("## Record yourself in English and immediately receive voice translations.")
        
        with gr.Row():
            with gr.Column():
                audio_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    show_download_button=True,
                    waveform_options=gr.WaveformOptions(
                        waveform_color="#01C6FF",
                        waveform_progress_color="#0066B4",
                        skip_length=2,
                        show_controls=False,
                    ),
                )
                with gr.Row():
                    submit = gr.Button("Submit", variant="primary")
                    clear_btn = gr.ClearButton(audio_input, "Clear")

        # Output groups for translations
        output_components = {}
        for lang in ["Turkish", "Swedish", "Russian", "German", "Spanish", "Japanese"]:
            with gr.Group() as group:
                output_audio = gr.Audio(label=lang, interactive=False)
                output_text = gr.Markdown()
                output_components[lang] = (output_audio, output_text)

        submit.click(fn=voice_to_voice, inputs=audio_input, outputs=[item[0] for item in output_components.values()], show_progress=True)

    demo.launch(share=True)

# Thread for Gradio interface
def launch_gradio_thread():
    thread = threading.Thread(target=create_gradio_interface)
    thread.daemon = True  # Daemonize the thread to close with Django server
    thread.start()

# Django view to display the Gradio app
def gradio_view(request):
    # Launch Gradio in a separate thread
    launch_gradio_thread()

    # Render the template for the Gradio app
    return render(request, 'gradio_page.html')

def translator_history(request):
    # Get all input translations for the logged-in user
    input_translations = InputTranslator.objects.filter(user=request.user).prefetch_related('outputtranslator_set')
    
    context = {
        'input_translations': input_translations,
    }
    
    return render(request, 'translator_history.html', context)

@require_http_methods(["DELETE"])
def delete_translation(request, translation_id):
    try:
        translation = InputTranslator.objects.get(id=translation_id)
        translation.delete()
        return JsonResponse({'message': 'Translation deleted successfully.'}, status=204)
    except InputTranslator.DoesNotExist:
        return JsonResponse({'error': 'Translation not found.'}, status=404)