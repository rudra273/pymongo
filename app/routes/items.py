from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
import logging
from app.database import get_db
from app.schemas import Item, ItemCreate, ItemUpdate

router = APIRouter()
logger = logging.getLogger(__name__)

db = get_db()
items_collection = db.items

def item_helper(item) -> Item:
    return Item(
        _id=str(item["_id"]),
        name=item["name"],
        email=item["email"],
        item_name=item["item_name"],
        quantity=item["quantity"],
        expiry_date=item["expiry_date"],
        insert_date=item["insert_date"]
    )

@router.post("/", response_model=Item)
async def create_item(item: ItemCreate):
    try:
        item_dict = item.dict()
        item_dict["insert_date"] = datetime.utcnow()
        result = items_collection.insert_one(item_dict)
        new_item = items_collection.find_one({"_id": result.inserted_id})
        logger.info(f"Created item with ID: {result.inserted_id}")
        return item_helper(new_item)
    except Exception as e:
        logger.error(f"Error creating item: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{id}", response_model=Item)
async def get_item(id: str):
    try:
        item = items_collection.find_one({"_id": ObjectId(id)})
        if item:
            logger.info(f"Retrieved item with ID: {id}")
            return item_helper(item)
        logger.warning(f"Item with ID {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        logger.error(f"Error retrieving item: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/filter", response_model=List[Item])
async def filter_items(
    email: Optional[str] = None,
    expiry_date: Optional[str] = None,
    insert_date: Optional[str] = None,
    quantity: Optional[int] = None
):
    try:
        query = {}
        if email:
            query["email"] = email
        if expiry_date:
            query["expiry_date"] = {"$gte": expiry_date}
        if insert_date:
            query["insert_date"] = {"$gte": datetime.fromisoformat(insert_date)}
        if quantity:
            query["quantity"] = {"$gte": quantity}

        items = items_collection.find(query)
        result = [item_helper(item) for item in items]
        logger.info(f"Filtered items: {len(result)} results")
        return result
    except Exception as e:
        logger.error(f"Error filtering items: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/aggregate")
async def aggregate_items():
    try:
        pipeline = [
            {"$group": {"_id": "$email", "count": {"$sum": 1}}}
        ]
        result = list(items_collection.aggregate(pipeline))
        logger.info("Aggregated items by email")
        return result
    except Exception as e:
        logger.error(f"Error aggregating items: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.delete("/{id}")
async def delete_item(id: str):
    try:
        result = items_collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count:
            logger.info(f"Deleted item with ID: {id}")
            return {"message": "Item deleted successfully"}
        logger.warning(f"Item with ID {id} not found for deletion")
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        logger.error(f"Error deleting item: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put("/{id}", response_model=Item)
async def update_item(id: str, item: ItemUpdate):
    try:
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        result = items_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if result.modified_count:
            updated_item = items_collection.find_one({"_id": ObjectId(id)})
            logger.info(f"Updated item with ID: {id}")
            return item_helper(updated_item)
        logger.warning(f"Item with ID {id} not found for update")
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        logger.error(f"Error updating item: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")