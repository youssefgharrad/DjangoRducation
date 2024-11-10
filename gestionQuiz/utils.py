import requests
from django.conf import settings
import settings as stgs
import google.generativeai as genai

genai.configure(api_key=stgs.GEMINI_API_KEY)
