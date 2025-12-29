from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.auth import verify_api_key
from app.services.school_service import SchoolService
from app.schemas.school import SchoolCreate, SchoolUpdate, SchoolResponse


router = APIRouter(prefix="/schools", tags=["schools"])


def get_school_service(db: Session = Depends(get_db)) -> SchoolService:
    return SchoolService(db)


@router.post("", response_model=SchoolResponse, status_code=status.HTTP_201_CREATED)
def create_school(
    school: SchoolCreate,
    service: SchoolService = Depends(get_school_service),
    _: str = Depends(verify_api_key)
) -> SchoolResponse:
    return service.create(school)


@router.get("", response_model=List[SchoolResponse])
def list_schools(
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    service: SchoolService = Depends(get_school_service)
) -> List[SchoolResponse]:
    return service.get_all(limit=limit, offset=offset, is_active=is_active)


@router.get("/{school_id}", response_model=SchoolResponse)
def get_school(
    school_id: int,
    service: SchoolService = Depends(get_school_service)
) -> SchoolResponse:
    return service.get_by_id(school_id)


@router.patch("/{school_id}", response_model=SchoolResponse)
def update_school(
    school_id: int,
    school: SchoolUpdate,
    service: SchoolService = Depends(get_school_service),
    _: str = Depends(verify_api_key)
) -> SchoolResponse:
    return service.update(school_id, school)


@router.delete("/{school_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_school(
    school_id: int,
    service: SchoolService = Depends(get_school_service),
    _: str = Depends(verify_api_key)
) -> None:
    service.delete(school_id)


@router.patch("/{school_id}/activate", response_model=SchoolResponse)
def activate_school(
    school_id: int,
    service: SchoolService = Depends(get_school_service),
    _: str = Depends(verify_api_key)
) -> SchoolResponse:
    return service.activate(school_id)

