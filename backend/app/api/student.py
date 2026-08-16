import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_academy, get_db
from app.models.academy import Academy
from app.schemas.student import (
    PaginatedStudentResponse,
    StudentCreate,
    StudentResponse,
    StudentStatsResponse,
    StudentUpdate,
)
from app.services.student import StudentService

router = APIRouter(
    prefix="/api/students",
    tags=["Students"],
    responses={401: {"description": "Invalid or missing authentication token"}},
)


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    responses={
        201: {"description": "Student created"},
        401: {"description": "Not authenticated"},
        409: {"description": "Duplicate email or identification number"},
    },
)
async def create_student(
    data: StudentCreate,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new student for the authenticated academy.

    - **first_name**: Student's first name
    - **last_name**: Student's last name
    - **email**: Student's email (unique per academy)
    - **identification_number**: ID document number (unique per academy)
    - **phone_number**: Contact phone
    - **address**: Full address
    - **date_of_birth**: Date of birth (ISO format)
    - **allergies**: Known allergies (default: "N/A")
    - **referral_source**: How they found the academy
    - **occupation**: Student's occupation
    """
    service = StudentService(db)
    return await service.create_student(academy.id, data)


@router.get(
    "",
    response_model=PaginatedStudentResponse,
    summary="List students",
    responses={
        200: {"description": "Paginated list of students"},
    },
)
async def list_students(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(20, ge=1, le=100, description="Items per page (1-100)"),
    search: str | None = Query(None, description="Search by name, email, phone, or ID number"),
    status: str | None = Query(None, description="Filter by status: active, inactive, pending, graduated"),
    include_deleted: bool = Query(False, description="Include soft-deleted students"),
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    """
    List all students belonging to the authenticated academy.

    - **search**: Search by first name, last name, email, phone number, or identification number
    - **status**: Filter by student status (active, inactive, pending, graduated)
    - **include_deleted**: Set to true to include soft-deleted students
    """
    service = StudentService(db)
    return await service.list_students(academy.id, page, size, search, status, include_deleted)


@router.get(
    "/stats",
    response_model=StudentStatsResponse,
    summary="Get student statistics",
    responses={
        200: {"description": "Student statistics"},
    },
)
async def get_student_stats(
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    """
    Get statistics about students in the academy.

    Returns total, active, inactive, pending, graduated counts, and new students this month.
    """
    service = StudentService(db)
    return await service.get_stats(academy.id)


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Get student by ID",
    responses={
        200: {"description": "Student details"},
        404: {"description": "Student not found"},
    },
)
async def get_student(
    student_id: uuid.UUID,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a specific student.
    """
    service = StudentService(db)
    return await service.get_student(student_id, academy.id)


@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Update student",
    responses={
        200: {"description": "Student updated"},
        404: {"description": "Student not found"},
        409: {"description": "Duplicate email or identification number"},
    },
)
async def update_student(
    student_id: uuid.UUID,
    data: StudentUpdate,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    """
    Update student information. All fields are optional — only provided fields will be updated.
    """
    service = StudentService(db)
    return await service.update_student(student_id, academy.id, data)


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete student",
    responses={
        204: {"description": "Student soft-deleted"},
        404: {"description": "Student not found"},
    },
)
async def delete_student(
    student_id: uuid.UUID,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft-delete a student by setting their status to 'deleted'.

    The student record is preserved but will not appear in normal listings.
    """
    service = StudentService(db)
    await service.delete_student(student_id, academy.id)
