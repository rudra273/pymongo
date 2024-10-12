from fastapi import APIRouter, HTTPException
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
import logging
from app.database import get_db
from app.schemas import ClockIn, ClockInCreate, ClockInUpdate

router = APIRouter()
logger = logging.getLogger(__name__)

db = get_db()
clock_in_collection = db.clock_in

def clock_in_helper(record) -> ClockIn:
    return ClockIn(
        _id=str(record["_id"]),
        email=record["email"],
        location=record["location"],
        insert_datetime=record["insert_datetime"]
    )

@router.post("/", response_model=ClockIn)
async def create_clock_in(clock_in: ClockInCreate):
    try:
        clock_in_dict = clock_in.dict()
        clock_in_dict["insert_datetime"] = datetime.utcnow()
        result = clock_in_collection.insert_one(clock_in_dict)
        new_clock_in = clock_in_collection.find_one({"_id": result.inserted_id})
        logger.info(f"Created clock-in record with ID: {result.inserted_id}")
        return clock_in_helper(new_clock_in)
    except Exception as e:
        logger.error(f"Error creating clock-in record: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{id}", response_model=ClockIn)
async def get_clock_in(id: str):
    try:
        clock_in = clock_in_collection.find_one({"_id": ObjectId(id)})
        if clock_in:
            logger.info(f"Retrieved clock-in record with ID: {id}")
            return clock_in_helper(clock_in)
        logger.warning(f"Clock-in record with ID {id} not found")
        raise HTTPException(status_code=404, detail="Clock-in record not found")
    except Exception as e:
        logger.error(f"Error retrieving clock-in record: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/filter", response_model=List[ClockIn])
async def filter_clock_in(
    email: Optional[str] = None,
    location: Optional[str] = None,
    insert_datetime: Optional[str] = None
):
    try:
        query = {}
        if email:
            query["email"] = email
        if location:
            query["location"] = location
        if insert_datetime:
            query["insert_datetime"] = {"$gte": datetime.fromisoformat(insert_datetime)}

        clock_ins = clock_in_collection.find(query)
        result = [clock_in_helper(record) for record in clock_ins]
        logger.info(f"Filtered clock-in records: {len(result)} results")
        return result
    except Exception as e:
        logger.error(f"Error filtering clock-in records: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.delete("/{id}")
async def delete_clock_in(id: str):
    try:
        result = clock_in_collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count:
            logger.info(f"Deleted clock-in record with ID: {id}")
            return {"message": "Clock-in record deleted successfully"}
        logger.warning(f"Clock-in record with ID {id} not found for deletion")
        raise HTTPException(status_code=404, detail="Clock-in record not found")
    except Exception as e:
        logger.error(f"Error deleting clock-in record: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put("/{id}", response_model=ClockIn)
async def update_clock_in(id: str, clock_in: ClockInUpdate):
    try:
        update_data = {k: v for k, v in clock_in.dict().items() if v is not None}
        result = clock_in_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if result.modified_count:
            updated_clock_in = clock_in_collection.find_one({"_id": ObjectId(id)})
            logger.info(f"Updated clock-in record with ID: {id}")
            return clock_in_helper(updated_clock_in)
        logger.warning(f"Clock-in record with ID {id} not found for update")
        raise HTTPException(status_code=404, detail="Clock-in record not found")
    except Exception as e:
        logger.error(f"Error updating clock-in record: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")