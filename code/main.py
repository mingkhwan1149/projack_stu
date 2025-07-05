# code/main.py
from fastapi import FastAPI, HTTPException
from supabase import create_client
import os

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.get("/show-keys")
async def show_keys():
    return {
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_KEY": SUPABASE_KEY
    }
    
@app.get("/test")
async def root():
    return {"message":"ch" }

@app.get("/user")
async def get_users():
    response = supabase.table("student").select("*").execute()
    return {"users": response.data}


@app.get("/user_by_card/{card_id}")
async def get_user_by_card(card_id: str):
    response = supabase.table("student").select("*").eq("card_id", card_id).execute()

    # Debug: ดูโครงสร้าง response ทั้งหมดก่อน
    # print("response:", response)
    # print("response.data:", getattr(response, "data", None))
    # print("response.error:", getattr(response, "error", None))
    # print("response.__dict__:", response.__dict__)

    # หากข้อมูลใน response ไม่มี 'data' หรือ 'error' ให้เช็คตาม attribute ที่มี
    data = getattr(response, "data", None)
    error = getattr(response, "error", None)

    if error:
        raise HTTPException(status_code=500, detail=str(error))

    if not data:
        raise HTTPException(status_code=404, detail="User not found")

    return {"user": data[0]}