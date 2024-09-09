import asyncio
import os

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.schema import MetaData
from sqlalchemy.sql import text

from src.config import config
from src.core.database.postgresql import Model, get_session
from src.core.database.postgresql.repository import Base
from src.models.appointment_model import AppointmentModel
from src.models.doctor_model import DoctorModel
from src.models.medical_records_model import MedicalRecordModel
from src.models.notification_model import NotificationModel
from src.models.patient_model import PatientModel
from src.models.payment_model import PaymentModel
from src.models.prescription_model import PrescriptionModel
from src.models.rating_model import RatingModel
from src.models.user_model import UserModel
from src.models.work_schedule_model import WorkScheduleModel


async def manage_database():
    engine = create_async_engine(config.POSTGRES_URL_MASTER, echo=True)
    async with engine.begin() as conn:
        _ = conn.execute(text("DROP DATABASE IF EXISTS health_care"))
        _ = conn.execute(text("CREATE DATABASE health_care"))
        _ = conn.commit()


async def create_tables():
    engine = create_async_engine(config.POSTGRES_URL_MASTER, echo=True)
    async with engine.begin() as conn:
        try:
            def check_tables_and_data(connection):
                Base.metadata.create_all(connection)
                return True
            result = await conn.run_sync(check_tables_and_data)
            if result is False:
                print("Tables already exist.")
        except Exception as e:
            print("==========================")
            print(f"An error occurred: {e}")
        finally:
            await engine.dispose()

if config.ENV == 'DEV':
    asyncio.run(manage_database())
    asyncio.run(create_tables())
