import google.generativeai as genai
#import PIL.Image
import os
import json
#genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
#img = PIL.Image.open('path/to/image.png')

PROJECT_DIR = os.path.dirname(__file__)+'/'

with open(PROJECT_DIR+'tokens.gitignore', 'r') as rfile:
    TOKEN = json.load(rfile)['gemini']


genai.configure(api_key=TOKEN)

model = genai.GenerativeModel('gemini-pro')
multi_model = genai.GenerativeModel("gemini-1.5-flash")


