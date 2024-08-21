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
from src.models.dermatology_medical import DermatologyMedicalRecords
from src.models.doctor_model import DoctorModel
from src.models.inventory_model import InventoryModel
from src.models.medical_model import MedicalModel
from src.models.patient_model import PatientModel
from src.models.payment_model import PaymentModel
from src.models.rating_model import RatingModel
from src.models.user import UserModel
from src.models.working_schedule_model import WorkingScheduleModel


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
                # current_dir = os.getcwd()
                # sql_file_path = os.path.join(current_dir, 'init.sql')
                # with open(sql_file_path, encoding='utf-8', mode='r') as f:
                #     sql_script = f.read()
                #     statements = sql_script.split(';')
                #     for statement in statements:
                #         if statement.strip():
                #             connection.execute(text(statement))
                # connection.commit()
                return True
            result = await conn.run_sync(check_tables_and_data)
            if result is False:
                print("Tables already exist.")
        except Exception as e:
            print("==========================")
            print(f"An error occurred: {e}")
        finally:
            await engine.dispose()

if config.ENV == 'DB':
    asyncio.run(manage_database())
    asyncio.run(create_tables())
