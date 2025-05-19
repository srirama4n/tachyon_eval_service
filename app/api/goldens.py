from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.golden import Golden, GoldenCreate, GoldenUpdate, GoldenImport, GoldenGenerate
from app.services.golden_service import GoldenService
from app.core.exceptions import GoldenValidationError

router = APIRouter()

@router.get("/usecases/{usecase_id}/datasets/{dataset_id}/goldens", response_model=List[Golden])
async def get_goldens(usecase_id: str, dataset_id: str):
    return await GoldenService.get_goldens(usecase_id, dataset_id)

@router.post("/usecases/{usecase_id}/datasets/{dataset_id}/goldens", response_model=Golden)
async def create_golden(usecase_id: str, dataset_id: str, golden: GoldenCreate):
    if golden.usecase_id != usecase_id:
        raise GoldenValidationError(
            f"Golden usecase_id ({golden.usecase_id}) does not match URL parameter ({usecase_id})"
        )
    if golden.dataset_id != dataset_id:
        raise GoldenValidationError(
            f"Dataset ID in golden ({golden.dataset_id}) does not match URL parameter ({dataset_id})"
        )
    return await GoldenService.create_golden(golden)

@router.put("/usecases/{usecase_id}/datasets/{dataset_id}/goldens/{golden_id}", response_model=Golden)
async def update_golden(usecase_id: str, dataset_id: str, golden_id: str, golden_update: GoldenUpdate):
    
    return await GoldenService.update_golden(usecase_id, dataset_id, golden_id, golden_update)

@router.delete("/usecases/{usecase_id}/datasets/{dataset_id}/goldens/{golden_id}")
async def delete_golden(usecase_id: str, dataset_id: str, golden_id: str):
    await GoldenService.delete_golden(usecase_id, golden_id)
    return {"message": f"Golden '{golden_id}' deleted successfully"}

@router.post("/usecases/{usecase_id}/datasets/{dataset_id}/goldens/import", response_model=List[Golden])
async def import_goldens(usecase_id: str, dataset_id: str, goldens_to_import: List[GoldenImport]):
    
    return await GoldenService.import_goldens(usecase_id, dataset_id, goldens_to_import)

@router.post("/usecases/{usecase_id}/datasets/{dataset_id}/goldens/generate", response_model=List[Golden])
async def generate_goldens(
    usecase_id: str,
    dataset_id: str,
    golden: GoldenGenerate
):
    try:
        return await GoldenService.generate_goldens(usecase_id, dataset_id, golden)
    except GoldenValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate goldens: {str(e)}"
        ) 