import os
import shelve
# import asyncio
import logging
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

client = OpenAI(api_key=OPENAI_API_KEY)

# def upload_file(path):
#     """Upload a file with an 'assistants' purpose"""
#     file = await client.files.create(file=open(path, "rb"), purpose="assistants") # type: ignore
#     return file

# def create_assistant(file):
#     """Create an assistant"""
#     assistant = await client.beta.assistants.create(
#         name="Fedusley",
#         instructions="You're a helpful WhatsApp assistant...",
#         tools=[{"type": "assistant"}],
#         model="gpt-4-1106-preview",
#         file_ids=[file.id] # type: ignore
#     )
#     return assistant

def generate_response(message_body, wa_id, name):
    """Generate a response"""
    thread_id = check_if_thread_exists(wa_id)
    if thread_id is None:
        logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.create() # type: ignore
        store_thread(wa_id, thread.id)
        thread_id = thread.id
    else:
        logging.info(f"Retrieving existing thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.retrieve(thread_id) # type: ignore

    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body
    ) # type: ignore
    new_message = run_assistant(thread, name) # type: ignore
    logging.info(f"To {name}: {new_message}")
    return new_message

def run_assistant(thread):
    """Run the assistant"""
    assistant = client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID) # type: ignore
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    ) # type: ignore

    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id) # type: ignore

    messages = client.beta.threads.messages.list(thread_id=thread.id) # type: ignore
    new_message = messages.data[0].content[0].text.value # type: ignore
    logging.info(f"Generated message: {new_message}")
    return new_message

def check_if_thread_exists(wa_id):
    """Check if a thread exists"""
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)

def store_thread(wa_id, thread_id):
    """Store a thread"""
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id