from typing import Optional
from datetime import datetime
from database import Database
from models import Usecase
from app.core.exceptions import UsecaseNotFoundError, DatabaseError

class UsecaseRepository:
    def __init__(self):
        self.db = Database.db

    async def find_by_id(self, usecase_id: str) -> Usecase:
        try:
            document = await self.db.usecases.find_one({"id": usecase_id})
            if not document:
                raise UsecaseNotFoundError(usecase_id)
            
            document["created_at"] = document["created_at"].isoformat()
            document["updated_at"] = document["updated_at"].isoformat()
            return Usecase(**document)
        except UsecaseNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(detail=f"Failed to fetch usecase: {str(e)}")

    async def create(self, usecase: Usecase) -> Usecase:
        try:
            # Check if usecase already exists
            existing = await self.db.usecases.find_one({"id": usecase.id})
            if existing:
                raise DatabaseError(detail=f"Usecase with id {usecase.id} already exists")
            
            usecase_dict = usecase.model_dump()
            await self.db.usecases.insert_one(usecase_dict)
            return usecase
        except Exception as e:
            raise DatabaseError(detail=f"Failed to create usecase: {str(e)}")

    async def update(self, usecase_id: str, usecase: Usecase) -> Usecase:
        try:
            # Check if usecase exists
            existing = await self.db.usecases.find_one({"id": usecase_id})
            if not existing:
                raise UsecaseNotFoundError(usecase_id)
            
            usecase_dict = usecase.model_dump()
            usecase_dict["updated_at"] = datetime.now()
            await self.db.usecases.update_one(
                {"id": usecase_id},
                {"$set": usecase_dict}
            )
            return usecase
        except UsecaseNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(detail=f"Failed to update usecase: {str(e)}")

    async def delete(self, usecase_id: str) -> None:
        try:
            # Check if usecase exists
            existing = await self.db.usecases.find_one({"id": usecase_id})
            if not existing:
                raise UsecaseNotFoundError(usecase_id)
            
            await self.db.usecases.delete_one({"id": usecase_id})
        except UsecaseNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(detail=f"Failed to delete usecase: {str(e)}") 