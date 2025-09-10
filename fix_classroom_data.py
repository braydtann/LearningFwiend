#!/usr/bin/env python3
"""
Script to fix classroom data structure to match the expected model
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def fix_classroom_data():
    """Fix classroom data structure."""
    
    # Get the classroom we created
    classroom = await db.classrooms.find_one({"title": "Test Classroom for Program 2"})
    
    if not classroom:
        print("❌ Test classroom not found!")
        return
    
    print(f"✅ Found classroom: {classroom.get('title', 'No title')}")
    
    # Update the classroom to match the expected structure
    update_data = {
        "name": classroom.get("title", "Test Classroom for Program 2"),
        "trainerId": classroom.get("instructorId"),
        "trainerName": classroom.get("instructor"),
        "createdBy": classroom.get("instructorId"),
        "programCount": len(classroom.get("programIds", [])),
        "updated_at": datetime.utcnow()
    }
    
    # Remove the old fields and add new ones
    await db.classrooms.update_one(
        {"_id": classroom["_id"]},
        {
            "$set": update_data,
            "$unset": {"title": "", "instructorId": "", "instructor": ""}
        }
    )
    
    print("✅ Fixed classroom data structure")
    
    # Verify the fix
    updated_classroom = await db.classrooms.find_one({"_id": classroom["_id"]})
    print(f"✅ Updated classroom: {updated_classroom.get('name')}")
    print(f"   Trainer: {updated_classroom.get('trainerName')}")
    print(f"   Students: {len(updated_classroom.get('studentIds', []))}")
    print(f"   Programs: {len(updated_classroom.get('programIds', []))}")

async def main():
    try:
        await fix_classroom_data()
    except Exception as e:
        print(f"❌ Error fixing classroom data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())