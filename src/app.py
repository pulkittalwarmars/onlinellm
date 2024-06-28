## Lets use this space as the file output which is going to be tested
## Fow now import os and dotenv and load the parameters through there
## Will delete this for the final version

import os
from dotenv import load_dotenv
from openai import OpenAI



client = OpenAI(base_url=<DEPLOYMENT_ENDPOINT>,
   api_key=<API_KEY_FOR_DEPLOYMENT>)

   completion = client.chat.completions.create(
     model="<ONLINE_MODEL_ID>",
     messages=[
       {"role": "system", "content": "You are a helpful assistant."},
       {"role": "user", "content": "What is the top news about Gen AI today? "}
     ]
)

print(completion.choices[0].message)