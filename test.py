from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint="pt-onlinellm.azurewebsites.net",
    api_version="2024-02-01",
    api_key="99d8e7d8c355486583e8ab633d7ff06b"
)

completion = client.chat.completions.create(
    model="dummy_model",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the top news about Gen AI today?"}
    ]
)

print(completion.choices[0].message)