## Lets use this space as the file output which is going to be tested
## Fow now import os and dotenv and load the parameters through there
## Will delete this for the final version

import os
import sys
from dotenv import load_dotenv
from openai import AzureOpenAI
from src.exception import CustomException



client = AzureOpenAI(azure_endpoint=os.getenv("AZURE_ENDPOINT"),
                     api_version="2024-02-01",
                     api_key=os.getenv("OPENAI_API_KEY"))

try:
  completion = client.chat.completions.create(
      model="pt_rekoncile",
      messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the top news about Gen AI today? "}
      ]
  )

  print(completion.choices[0].message)
except Exception as e:
  raise CustomException(e,sys)