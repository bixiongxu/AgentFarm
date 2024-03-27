from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from openai import OpenAI

def create_assistant(openai_client, name, desc):
    assistant = openai_client.beta.assistants.create(
        name=name,
        instructions=desc, 
        tools=[],
        model="gpt-4-turbo-preview",
    )
    return assistant

def create_thread(openai_client):
    thread = openai_client.beta.threads.create()
    return thread

def summarize_thread_name(openai_client, message):
    MODEL = "gpt-4-turbo-preview"
    prompt = f"""
        Please help create a short(<16 words) title based on the message: {message}
    """
    response = openai_client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    rewritten = response.choices[0].message.content
    return rewritten

