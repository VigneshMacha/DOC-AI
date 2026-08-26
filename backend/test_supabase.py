import os

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print("URL:", url)
print("KEY loaded:", bool(key))

supabase = create_client(url, key)

response = supabase.table("profiles").select("*").execute()

print(response.data)