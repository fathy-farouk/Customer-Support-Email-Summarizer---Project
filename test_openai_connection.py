from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="EqmbaaqQJRmAG1eWO8VtJwxMeQ3OnzuITxKR0RJhRhikplzZ9yAfJQQJ99BEACHYHv6XJ3w3AAAAACOGNUT4",  # Replace with your real key
    api_version="2024-02-15-preview",     # This is the correct version for gpt-4o
    azure_endpoint="https://email-summarizer-ai-resource.cognitiveservices.azure.com/",
)

response = client.chat.completions.create(
    model="gpt-4o",  # Your actual deployment name shown in the portal
    messages=[
        {"role": "system", "content": "You are an assistant that summarizes emails."},
        {"role": "user", "content": "This is a long customer support email. Please summarize it."}
    ]
)

print(response.choices[0].message.content)
