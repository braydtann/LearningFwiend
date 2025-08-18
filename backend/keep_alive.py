#!/usr/bin/env python3
"""
Database Keep-Alive Service
Pings MongoDB Atlas every 30 minutes to prevent auto-pause on Free Tier.
Run this as a background service to keep your cluster active.
"""
import asyncio
import os
import time
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class DatabaseKeepAlive:
    def __init__(self):
        self.mongo_url = os.environ['MONGO_URL']
        self.db_name = os.environ['DB_NAME']
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client[self.db_name]
            
            # Test connection
            await self.db.admin.command('ping')
            logger.info("✅ Connected to MongoDB Atlas successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB Atlas: {e}")
            return False
    
    async def ping_database(self):
        """Perform a lightweight database operation to keep cluster active"""
        try:
            # Simple ping command
            result = await self.db.admin.command('ping')
            
            if result.get('ok') == 1:
                logger.info("✅ Database ping successful - cluster is active")
                return True
            else:
                logger.warning("⚠️ Database ping returned unexpected result")
                return False
                
        except Exception as e:
            logger.error(f"❌ Database ping failed: {e}")
            return False
    
    async def health_check(self):
        """Perform a more detailed health check"""
        try:
            # Check if we can read from users collection
            users_count = await self.db.users.count_documents({})
            logger.info(f"📊 Health check: {users_count} users in database")
            
            # Update a keep-alive timestamp
            keep_alive_doc = {
                "service": "keep_alive",
                "last_ping": datetime.utcnow(),
                "status": "active"
            }
            
            await self.db.system_health.replace_one(
                {"service": "keep_alive"},
                keep_alive_doc,
                upsert=True
            )
            
            logger.info("✅ Health check completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
    
    async def keep_alive_loop(self, interval_minutes=30):
        """Main keep-alive loop that runs indefinitely"""
        logger.info(f"🚀 Starting database keep-alive service (ping every {interval_minutes} minutes)")
        
        while True:
            try:
                # Reconnect if needed
                if not self.client:
                    await self.connect()
                
                # Perform ping
                ping_success = await self.ping_database()
                
                if ping_success:
                    # Every 10th ping, do a health check
                    current_time = datetime.utcnow()
                    if current_time.minute % 10 == 0:  # Rough check for every 10th iteration
                        await self.health_check()
                else:
                    logger.warning("⚠️ Ping failed, attempting to reconnect...")
                    await self.connect()
                
                # Wait for next interval
                sleep_seconds = interval_minutes * 60
                logger.info(f"😴 Sleeping for {interval_minutes} minutes until next ping...")
                await asyncio.sleep(sleep_seconds)
                
            except KeyboardInterrupt:
                logger.info("🛑 Keep-alive service stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error in keep-alive loop: {e}")
                logger.info("🔄 Retrying in 5 minutes...")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def close(self):
        """Clean shutdown"""
        if self.client:
            self.client.close()
            logger.info("🔌 MongoDB connection closed")

async def main():
    """Main function to run the keep-alive service"""
    keep_alive = DatabaseKeepAlive()
    
    try:
        # Initial connection
        connected = await keep_alive.connect()
        
        if connected:
            # Start the keep-alive loop
            await keep_alive.keep_alive_loop(interval_minutes=30)
        else:
            logger.error("❌ Could not establish initial connection. Exiting.")
            return 1
            
    except KeyboardInterrupt:
        logger.info("🛑 Service interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return 1
    finally:
        await keep_alive.close()
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)