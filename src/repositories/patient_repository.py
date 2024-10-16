from _decimal import Decimal
from typing import Any, Sequence, Tuple

from sqlalchemy import exists, func, select
from sqlalchemy.engine.row import Row
from sqlalchemy.orm import joinedload

from src.core.database.postgresql import PostgresRepository
from src.core.decorator.exception_decorator import catch_error_repository
from src.core.exception import BadRequest
from src.core.security.password import PasswordHandler
from src.enum import AppointmentModelStatus, ErrorCode
from src.models.appointment_model import AppointmentModel
from src.models.doctor_model import DoctorModel
from src.models.patient_model import PatientModel
from src.models.rating_model import RatingModel
from src.models.user_model import Role, UserModel
from src.schema.rating_schema import RequestCreateRatingSchema
from src.schema.register import RequestRegisterPatientSchema


class PatientRepository(PostgresRepository[PatientModel]):

    @catch_error_repository("Failed to get patient by id, please try again later")
    async def get_all_patient(
        self,
        skip: int = 0,
        limit: int = 10,
        where: dict[str, Any] = {},
        order_by: dict[str, str] | None = None,
    ):

        query_patient = select(PatientModel)

        amount_query = select(func.count(PatientModel.id)).select_from(query_patient)
        query_patient = (
            query_patient.options(joinedload(PatientModel.doctor_manage))
            .offset(skip)
            .limit(limit)
        )

        result_amount = await self.session.execute(amount_query)
        page_size: int = limit
        total_pages = (result_amount.scalar_one() + page_size - 1) // page_size
        current_page: int = skip // limit + 1

        result_patient = await self.session.execute(query_patient)
        result_patient = result_patient.unique().scalars().all()

        items = [
            {
                **{
                    key: value
                    for key, value in element.as_dict.items()
                    if key != "doctor_manage_id"
                },
                "doctor_manager": (
                    element.doctor_manage.as_dict if element.doctor_manage else None
                ),
            }
            for element in result_patient
        ]
        return {
            "items": items,
            "total_page": total_pages,
            "current_page": current_page,
            "page_size": page_size,
        }

    @catch_error_repository("Failed to get patient by id, please try again later")
    async def get_by_id(self, patient_id: int):
        return await self.get_by("id", patient_id)

    @catch_error_repository("Failed to create rating, please try again later")
    async def create_rating_repository(self, user_id, data: RequestCreateRatingSchema):
        # check if patient hava rating
        query_rating_statment = select(RatingModel).where(
            RatingModel.patient_id == user_id, RatingModel.doctor_id == data.doctor_id
        )
        result_rating = await self.session.execute(query_rating_statment)
        data_rating = result_rating.scalar_one_or_none()
        if data_rating:
            data_rating.rating = data.rating
            data_rating.comment = data.comment
            self.session.add(data_rating)
            await self.session.commit()
            return data_rating.as_dict
        # check patient have permission to rating
        query_exist_appointment = select(
            exists(AppointmentModel).where(
                AppointmentModel.patient_id == user_id,
                AppointmentModel.doctor_id == data.doctor_id,
                AppointmentModel.appointment_status
                == AppointmentModelStatus.COMPLETED.value,
            )
        )
        result_exists_appointment = await self.session.execute(query_exist_appointment)
        if not result_exists_appointment.scalar_one():
            raise BadRequest(
                error_code=ErrorCode.BAD_REQUEST.name,
                errors={"message": ErrorCode.msg_permission_rating.value},
            )

        rating_model = RatingModel(
            **data.model_dump(),
            patient_id=user_id,
        )
        self.session.add(rating_model)
        await self.session.commit()
        return rating_model.as_dict

    async def count_patient(self):
        query = select(func.count(PatientModel.id))
        result = await self.session.execute(query)
        return result.scalar_one()

    @catch_error_repository(message=None)
    async def age_distribution_patient_repository(self):
        query = (
            select(
                (func.extract('year', func.age(PatientModel.date_of_birth))).label("age"),
                func.count(PatientModel.id).label("total"),
            )
            .group_by(func.extract('year', func.age(PatientModel.date_of_birth)),"id")
            .order_by(func.extract('year', func.age(PatientModel.date_of_birth)))
        )
        result = await self.session.execute(query)
        data = result.all()

        group_age = {
            "0-2": {"total": 0, "percentage": 0},
            "3-12": {"total": 0, "percentage": 0},
            "13-19": {"total": 0, "percentage": 0},
            "20-29": {"total": 0, "percentage": 0},
            "30-39": {"total": 0, "percentage": 0},
            "40-49": {"total": 0, "percentage": 0},
            "50-59": {"total": 0, "percentage": 0},
            "60-69": {"total": 0, "percentage": 0},
            "70-79": {"total": 0, "percentage": 0},
            "80-89": {"total": 0, "percentage": 0},
            "90-99": {"total": 0, "percentage": 0},
            "100+": {"total": 0, "percentage": 0},
        }

        total_patients = sum(total for _, total in data)
        for age, total in data:
            if age < 3:
                group_age["0-2"]["total"] += total
            elif age < 13:
                group_age["3-12"]["total"] += total
            elif age < 20:
                group_age["13-19"]["total"] += total
            elif age < 30:
                group_age["20-29"]["total"] += total
            elif age < 40:
                group_age["30-39"]["total"] += total
            elif age < 50:
                group_age["40-49"]["total"] += total
            elif age < 60:
                group_age["50-59"]["total"] += total
            elif age < 70:
                group_age["60-69"]["total"] += total
            elif age < 80:
                group_age["70-79"]["total"] += total
            elif age < 90:
                group_age["80-89"]["total"] += total
            elif age < 100:
                group_age["90-99"]["total"] += total
            else:
                group_age["100+"]["total"] += total

        # Tính tỷ lệ phần trăm cho mỗi nhóm tuổi
        for age_group, values in group_age.items():
            if total_patients > 0:  # Đảm bảo tổng số bệnh nhân không bằng 0
                values["percentage"] = (values["total"] / total_patients) * 100
            else:
                values["percentage"] = 0  # Nếu không có bệnh nhân

        return group_age
