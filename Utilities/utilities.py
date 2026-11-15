import os
from dotenv import load_dotenv

load_dotenv()

START_SEQUENCE = "\033[90m" # Ansi escape code for grey text.
END_SEQUENCE = "\033[0m"
# Function to log.
def log(text):
    if(int(os.getenv("DEBUG","0"))):
        print(f" {START_SEQUENCE}{text}{END_SEQUENCE}")