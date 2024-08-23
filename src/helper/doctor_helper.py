

import math
from typing import Any, Dict, List

from src.models.doctor_model import DoctorModel
from src.repositories.doctor_repository import DoctorRepository
from src.schema.doctor_schema import ReponseGetAllDoctorsSchame
from src.schema.register import RequestRegisterDoctorSchema


class DoctorHelper:
    def __init__(self, *, doctor_repository: DoctorRepository):
        self.doctor_repository = doctor_repository

    async def get_all_doctor(self, skip: int = 0, limit: int = 10, join_: set[str] | None = None, where: dict[str, Any] | None = None, order_by: dict[str, str] | None = None) -> ReponseGetAllDoctorsSchame:
        try:
            _doctors: list[DoctorModel] = await self.doctor_repository.get_all(skip, limit, join_, where, order_by)
            current_page = math.ceil(skip/limit) + 1
            total_page = 10
            page_size = limit
            data_respone: ReponseGetAllDoctorsSchame = ReponseGetAllDoctorsSchame(
                data=_doctors, current_page=current_page, total_page=total_page, page_size=page_size)  # type: ignore

            return data_respone
        except Exception as e:
            raise e

    async def get_doctor_by_id(self, doctor_id: int) -> DoctorModel | None:
        try:
            doctor: DoctorModel | None = await self.doctor_repository.get_by_id(doctor_id)
            return doctor
        except Exception as e:
            raise e

    async def create_doctor(self, data: RequestRegisterDoctorSchema):
        try:
            doctor = await self.doctor_repository.insert(data)
            return doctor
        except Exception as e:
            raise e
