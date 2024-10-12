from typing import Any

from sqlalchemy import exists, func, select
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

    @catch_error_repository("Failed to create patient, please try again later")
    async def insert_patient(self, data: RequestRegisterPatientSchema) -> PatientModel:
        user_exists = await self.session.scalar(
            select(exists().where(UserModel.phone_number == data.phone_number))
        )
        if user_exists:
            raise BadRequest(
                error_code=ErrorCode.USER_HAVE_BEEN_REGISTERED.name,
                errors={"message": "Phone number has been used by another user"},
            )

        # Check if patient exists by email
        patient_exists = await self.session.scalar(
            select(exists().where(PatientModel.email == data.email))
        )
        doctor_email_exists = await self.session.scalar(
            select(exists().where(DoctorModel.email == data.email))
        )
        if patient_exists or doctor_email_exists:
            raise BadRequest(
                error_code=ErrorCode.EMAIL_HAVE_BEEN_REGISTERED.name,
                errors={"message": "Email has been used by another user"},
            )

        # Create user and patient models
        password_hash = PasswordHandler.hash(data.password_hash)
        user_model = UserModel(
            phone_number=data.phone_number,
            password_hash=password_hash,
            role=Role.PATIENT.value,
        )
        self.session.add(user_model)
        await self.session.flush()
        patient_data = data.model_dump(exclude={"password_hash"})
        patient_model = PatientModel(id=user_model.id, **patient_data)

        self.session.add(patient_model)
        await self.session.commit()
        return patient_model

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
