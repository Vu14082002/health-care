import logging
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Literal

from sqlalchemy.exc import NoResultFound

from src.core.decorator.exception_decorator import catch_error_helper
from src.core.exception import BadRequest
from src.enum import ErrorCode
from src.models.doctor_model import DoctorExaminationPriceModel, DoctorModel
from src.repositories.doctor_repository import DoctorRepository
from src.schema.doctor_schema import RequestDoctorWorkScheduleNextWeek


class DoctorHelper:
    def __init__(self, *, doctor_repository: DoctorRepository):
        self.doctor_repository = doctor_repository

    @catch_error_helper(message=None)
    async def get_doctor_statistics(self) :
        # total_doctors = await self.doctor_repository.count_record(
        #     {"verify_status": {"$eq": 2}}
        # )
        # total_doctors_local = await self.doctor_repository.count_record(
        #     {"verify_status": {"$eq": 2}, "is_local_person": True}
        # )
        # total_doctors_foreign = await self.doctor_repository.count_record(
        #     {"verify_status": {"$eq": 2}, "is_local_person": False}
        # )
        # total_doctor_online = await self.doctor_repository.count_record(
        #     {
        #         "$or": [
        #             {"type_of_disease": TypeOfDisease.ONLINE.value},
        #             {"type_of_disease": TypeOfDisease.BOTH.value},
        #         ],
        #         "verify_status": {"$eq": 2},
        #         # "is_local_person": True,
        #     }
        # )
        # total_doctor_offline = await self.doctor_repository.count_record(
        #     {
        #         "$or": [
        #             {"type_of_disease": TypeOfDisease.ONLINE.value},
        #             {"type_of_disease": TypeOfDisease.BOTH.value},
        #         ],
        #         "verify_status": {"$eq": 2},
        #         # "is_local_person": True,
        #     }
        # )
        # total_doctor_both = await self.doctor_repository.count_record(
        #     {
        #         "type_of_disease": TypeOfDisease.BOTH.value,
        #         "verify_status": {"$eq": 2},
        #         "is_local_person": True,
        #     }
        # )
        # return {
        #     "total_doctors": total_doctors,
        #     "total_doctors_local": total_doctors_local,
        #     "total_doctors_foreign": total_doctors_foreign,
        #     "total_doctor_online": total_doctor_online,
        #     "total_doctor_ofline": total_doctor_offline,
        #     "total_doctor_both": total_doctor_both,
        # }
        return await self.doctor_repository.count_record_v2()

    @catch_error_helper(message=None)
    async def get_all_doctor(
        self,
        current_page: int = 1,
        page_size: int = 10,
        text_search: str | None = None,
        join_: set[str] | None = None,
        where: dict[str, Any] | None = None,
        order_by: dict[str, str] | None = None,
    ):
        skip = (current_page - 1) * page_size
        limit = page_size

        result = await self.doctor_repository.get_all(
            skip=skip,
            limit=limit,
            join_=join_,
            where=where,
            order_by=order_by,
            text_search=text_search,
        )
        return result
    @catch_error_helper(message=None)
    async def get_all_doctor_helper(
        self,
        current_page: int = 1,
        page_size: int = 10,
        text_search: str | None = None,
        filter_data: dict[str, Any]={},
        order_by:str | None = None,
        is_desc:bool = False,
    ):
        result = await self.doctor_repository.get_all_doctor_repository(
            current_page=current_page,page_size=page_size,text_search=text_search,filter_data=filter_data,order_by=order_by,is_desc=is_desc
        )
        return result

    @catch_error_helper(message=None)
    async def get_all_doctor_by_text_search(
        self,
        current_page: int = 1,
        page_size: int = 10,
        text_search: str | None = None,
        where: dict[str, Any] | None = None,
        order_by: dict[str, str] | None = None,
    ):
        try:
            skip = (current_page - 1) * page_size
            limit = page_size
            result = await self.doctor_repository.get_all(
                skip=skip,
                limit=limit,
                where=where,
                order_by=order_by,
                text_search=text_search,
            )
            return result
        except BadRequest as e:
            logging.error(f"Error in get_all_doctor: {e}")
            raise e
        except Exception as e:
            raise e

    @catch_error_helper(message=None)
    async def get_doctor_by_id(self, doctor_id: int):
        doctor = await self.doctor_repository.get_doctor_with_ratings(
            doctor_id=doctor_id
        )
        return doctor

    @catch_error_helper(message=None)
    async def create_doctor(self, data: dict[str, Any], *args: Any, **kwargs: Any):
        try:
            doctor = await self.doctor_repository.insert(data)
            return doctor
        except Exception as e:
            raise e

    @catch_error_helper(message=None)
    async def update_doctor(self, doctor_id: int, data: dict[str, Any]):
        doctor_model = await self.doctor_repository.get_by("id", doctor_id, unique=True)
        data = {k: v for k, v in data.items() if v is not None}
        doctor = await self.doctor_repository.update(doctor_model, data)
        return doctor

    @catch_error_helper("Server error when create doctor working schedule")
    async def create_doctor_work_schedule(
        self, doctor_id: int, data: RequestDoctorWorkScheduleNextWeek
    ):
        response = await self.doctor_repository.add_workingschedule(doctor_id, data)
        return response

    @catch_error_helper(message=None)
    async def reject_doctor(self, doctor_id: int):
        return await self.doctor_repository.reject_doctor(doctor_id)

    @catch_error_helper(message=None)
    async def verify_doctor(
        self, doctor_id: int, verify_status: int, online_price: float | None
    ) -> bool|str:
        doctor = None
        try:
            doctor = await self.doctor_repository.get_by("id", doctor_id, unique=True)
        except Exception as e:
            if isinstance(e, NoResultFound):
                raise BadRequest(
                    error_code=ErrorCode.BAD_REQUEST.name,
                    errors={"message": ErrorCode.msg_doctor_not_found.value},
                )
            raise e
        if doctor and doctor.verify_status in [0, 1, -1]:
            if verify_status == 2 and doctor.verify_status != 1:
                raise BadRequest(
                    error_code=ErrorCode.BAD_REQUEST.name,
                    errors={
                        "message": ErrorCode.msg_verify_step_one_before_verify_two.value
                    },
                )
            doctor_examination_price = DoctorExaminationPriceModel(
                doctor_id=doctor_id,
                online_price=online_price,
                offline_price=0,
            )
            doctor.verify_status = verify_status
            updated_doctor: DoctorModel = (
                await self.doctor_repository.update_doctor_model(
                    doctor, doctor_examination_price
                )
            )
            if isinstance(updated_doctor, DoctorModel):
                if updated_doctor.verify_status == 2:
                    return updated_doctor.email
                return True
        return False

    @catch_error_helper(message=None)
    async def get_working_schedules(
        self,
        doctor_id: int | None,
        start_date: date | None,
        end_date: date | None,
        examination_type: Literal["online", "offline"] | None,
        ordered: bool | None = None,
    ) -> List[Dict[str, Any]]:
        return await self.doctor_repository.get_working_schedules(
            doctor_id, start_date, end_date, examination_type, ordered=ordered
        )

    @catch_error_helper(message=None)
    async def get_working_schedules_by_id(self, *, id: int):
        return await self.doctor_repository.get_working_schedules_by_id(id=id)

    @catch_error_helper(message=None)
    async def get_empty_working_time(
        self, doctor_id: int, start_date: date, end_date: date
    ) -> Dict[str, List[Dict[str, str]]]:
        occupied_slots = await self.doctor_repository.get_working_schedules_v2(
            doctor_id, start_date, end_date
        )
        empty_slots = self._generate_empty_slots(start_date, end_date, occupied_slots)
        return empty_slots

    def _generate_empty_slots(
        self, start_date: date, end_date: date, occupied_slots: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, str]]]:
        empty_slots = {}
        current_date = start_date
        while current_date <= end_date:
            day_slots = []
            start_time = datetime.combine(current_date, time(0, 0))
            end_time = datetime.combine(current_date, time(23, 59))

            while start_time < end_time:
                slot_end = start_time + timedelta(minutes=30)
                if not self._is_slot_occupied(start_time, slot_end, occupied_slots):
                    day_slots.append(
                        {
                            "start_time": start_time.strftime("%H:%M"),
                            "end_time": slot_end.strftime("%H:%M"),
                        }
                    )
                start_time = slot_end

            if day_slots:
                empty_slots[current_date.isoformat()] = day_slots
            current_date += timedelta(days=1)

        return empty_slots

    def _is_slot_occupied(
        self,
        start_time: datetime,
        end_time: datetime,
        occupied_slots: List[Dict[str, Any]],
    ) -> bool:
        for slot in occupied_slots:
            if slot["work_date"] == start_time.date():
                occupied_start = datetime.combine(slot["work_date"], slot["start_time"])
                occupied_end = datetime.combine(slot["work_date"], slot["end_time"])
                if (occupied_start <= start_time < occupied_end) or (
                    occupied_start < end_time <= occupied_end
                ):
                    return True
        return False

    @catch_error_helper(message=None)
    async def get_patient_by_doctor_id(
        self,
        doctor_id: int | None,
        current_page: int = 1,
        page_size: int = 10,
        appointment_status: str | None = None,
        status_order: tuple[str, ...] = ("approved", "processing", "completed"),
        examination_type: Literal["online", "offline"] | None = None,
        text_search: str | None = None,
    ):
        return await self.doctor_repository.get_patient_by_doctor_id(
            doctor_id=doctor_id,
            current_page=current_page,
            page_size=page_size,
            appointment_status=appointment_status,
            status_order=status_order,
            examination_type=examination_type,
            text_search=text_search,
        )

    @catch_error_helper(message=None)
    async def get_one_patient_by_doctor(
        self,
        doctor_id: int | None,
        patient_id: int,
    ):
        return await self.doctor_repository.get_one_patient_by_doctor(
            doctot_id=doctor_id, patient_id=patient_id
        )


    @catch_error_helper(message=None)
    async def get_doctor_conversation_statistics(self,from_date:date|None=None,to_date:date|None=None,doctor_id:int|None=None,examination_type:Literal["online","offline",None]=None):
        return await self.doctor_repository.get_doctor_conversation_statistics(from_date=from_date,to_date=to_date,doctor_id=doctor_id,examination_type=examination_type)
