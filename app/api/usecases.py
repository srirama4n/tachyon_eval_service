from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.usecase import UsecaseCreate, UsecaseUpdate, Usecase
from app.services.usecase_service import UsecaseService
from app.core.exceptions import UsecaseNotFoundError, DatabaseError, UsecaseValidationError

router = APIRouter()

async def get_usecase_service() -> UsecaseService:
    return UsecaseService()

@router.get("/usecases/{usecase_id}", response_model=Usecase)
async def get_usecase(
    usecase_id: str,
    service: UsecaseService = Depends(get_usecase_service)
):
    try:
        usecase = await service.get_usecase(usecase_id)
        return usecase
    except UsecaseNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/usecases", response_model=Usecase)
async def create_usecase(
    usecase: UsecaseCreate,
    service: UsecaseService = Depends(get_usecase_service)
):
    try:
        created_usecase = await service.create_usecase(usecase.model_dump())
        return created_usecase
    except UsecaseValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/usecases/{usecase_id}", response_model=Usecase)
async def update_usecase(
    usecase_id: str,
    usecase: UsecaseUpdate,
    service: UsecaseService = Depends(get_usecase_service)
):
    try:
        updated_usecase = await service.update_usecase(usecase_id, usecase.model_dump())
        return updated_usecase
    except UsecaseNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UsecaseValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/usecases/{usecase_id}")
async def delete_usecase(
    usecase_id: str,
    service: UsecaseService = Depends(get_usecase_service)
):
    try:
        await service.delete_usecase(usecase_id)
        return {"message": f"Usecase {usecase_id} deleted successfully"}
    except UsecaseNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 