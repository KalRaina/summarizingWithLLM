# paste link
# fetch transcript
# break into chunks and feed to LLM
# generates summary
# concatenate summary parts
# prints summary

from scipy.io.wavfile import write
import numpy as np
import re

import os
from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq

LLMclient = Groq(api_key=os.getenv("GROQ_API_KEY")) # to run this on your computer you will have to save your API key as this environment variable
# do this by going into powershell and running:  setx GROQ_API_KEY "insert API key here"

def fetchDATTRANSCRIPT():
 
 yt = YouTubeTranscriptApi()

 while True:
  
  try:
   
   url = input("Paste the Youtube vid's URL: ")
   pattern = r"(?:v=|youtu\.be/|shorts/|embed/)([^&?/]{11})" # looks for any of these markers, then extracts next 11 characters till ^, &, ? or /
   
   match = re.search(pattern,url)
   id = match.group(1) # group 1 is capturing group, the ([^&?/]{11})
   
   break
  
  except Exception:
     
     print("Please type in a valid url.")

 
 transcript = yt.fetch(video_id=id) # gets transcript
 transcript = transcript.to_raw_data() # so we can edit on this boi like a dictionary

 readableTranscript = " ".join(entry["text"] for entry in transcript)

 return readableTranscript

def chunk_text(text, max_chars=3000):
    
    chunks = []
    current = ""

    for sentence in text.split(". "):
        sentence += ". "
        
        # if adding this sentence keeps us under the limit, append it
        if len(current) + len(sentence) <= max_chars:
            current += sentence
        else:
            # otherwise start a new chunk
            chunks.append(current.strip())
            current = sentence

    # Add the last chunk
    if current:
        chunks.append(current.strip())

    return chunks

def feedToLLM(chunk, client):

 response = client.chat.completions.create( # opens up chat, and give prompt to the LLM
  model="openai/gpt-oss-120b",
  messages=[
   {"role": "user", "content": f"Summarize: {chunk}"}
  ])
 return response.choices[0].message.content # returns the response by the LLM

def summarizeAll(chunks, client):
   
   partial_summaries = [feedToLLM(chunk=c, client=LLMclient) for c in chunks] # creates list with all the summaries in it
   combined = "\n".join(partial_summaries) # joins to make massive string

   final = client.chat.completions.create( # opens chat and gives below prompt
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "user", "content": f"Summarize these summaries into one final summary, do not mention anything about me asking you to summarize:\n\n{combined}"}
        ]
    )

   return final.choices[0].message.content # chat response, final summary to show to use

chunks = chunk_text(fetchDATTRANSCRIPT())
print(summarizeAll(chunks=chunks, client=LLMclient))