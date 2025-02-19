import cohere
from key import API_KEY

COHERE_API_KEY = API_KEY
co = cohere.ClientV2(COHERE_API_KEY)

system_message="""## Task and Context: 
You are a chatot designed to help a student find the est colleges suited for them. 
Provide a list of ten colleges suited to the student and list why the colleges would be good 
as well as supporting information about the school such as the acceptance rate, the tuition and averge GPA.
"""
message = input("\n Write About yourself:")

# Add the messages

messages = [{'role': 'system', 'content': system_message},
        {'role': 'user', 'content': message}]

response = co.chat_stream(model="command-r-plus-08-2024",
                messages=messages, temperature=1)
for event in response:
    if event.type == "content-delta":
        print(event.delta.message.content.text, end="")
print("\n")