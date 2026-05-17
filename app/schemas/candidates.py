from typing import Optional
from datetime import date
from decimal import Decimal
from pydantic import field_validator
from app.utils.validation import BaseSchema


class BulkCandidateIdsSchema(BaseSchema):
    """Schema for bulk archive/unarchive operations."""
    candidateIds: list[str]

    @field_validator('candidateIds')
    @classmethod
    def validate_candidate_ids(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError('At least one candidate ID is required')
        if len(v) > 500:
            raise ValueError('Cannot process more than 500 candidates at once')
        return v


class CreateCandidateSchema(BaseSchema):
    firstName: str
    parentName: Optional[str] = None
    lastName: str
    personalNumber: str
    phone: Optional[str] = None
    email: Optional[str] = None
    birthCountryId: Optional[str] = None
    birthMunicipalityId: Optional[str] = None
    birthPlaceId: Optional[str] = None
    birthMunicipalityForeign: Optional[str] = None
    birthPlaceForeign: Optional[str] = None
    dateOfBirth: Optional[date] = None
    gender: Optional[str] = None
    residenceMunicipalityId: Optional[str] = None
    residencePlaceId: Optional[str] = None
    categoryId: str
    isAutomatic: bool = False
    price: Decimal
    practicalHours: int = 20
    theoryHours: int = 20
    registrationDate: date
    protocolNumber: Optional[str] = None
    medicalCertificate: bool = False
    medicalCertificateNumber: Optional[str] = None
    medicalCertificateDate: Optional[date] = None
    verificationFlag: bool = False
    redCrossCertificate: bool = False
    idCardCopy: bool = False
    lecturerId: Optional[str] = None
    instructorId: Optional[str] = None
    vehicleId: Optional[str] = None
    comments: Optional[str] = None


class UpdateCandidateSchema(BaseSchema):
    firstName: Optional[str] = None
    parentName: Optional[str] = None
    lastName: Optional[str] = None
    personalNumber: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    birthCountryId: Optional[str] = None
    birthMunicipalityId: Optional[str] = None
    birthPlaceId: Optional[str] = None
    birthMunicipalityForeign: Optional[str] = None
    birthPlaceForeign: Optional[str] = None
    dateOfBirth: Optional[date] = None
    gender: Optional[str] = None
    residenceMunicipalityId: Optional[str] = None
    residencePlaceId: Optional[str] = None
    categoryId: Optional[str] = None
    isAutomatic: Optional[bool] = None
    price: Optional[Decimal] = None
    practicalHours: Optional[int] = None
    theoryHours: Optional[int] = None
    protocolNumber: Optional[str] = None
    medicalCertificate: Optional[bool] = None
    medicalCertificateNumber: Optional[str] = None
    medicalCertificateDate: Optional[date] = None
    verificationFlag: Optional[bool] = None
    redCrossCertificate: Optional[bool] = None
    idCardCopy: Optional[bool] = None
    lecturerId: Optional[str] = None
    instructorId: Optional[str] = None
    vehicleId: Optional[str] = None
    comments: Optional[str] = None
