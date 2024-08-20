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
from src.models.billing_model import BillingModel
from src.models.doctor_model import DoctorModel
from src.models.inventory_model import InventoryModel
from src.models.patient import PatientModel
from src.models.role import EnumRole, RoleModel
from src.models.user import UserModel
from src.models.user_roles import UserRolesModel


async def create_tables():
    engine = create_async_engine(config.POSTGRES_URL_MASTER, echo=True)
    async with engine.begin() as conn:
        try:
            def check_tables_and_data(connection):
                inspector = inspect(connection)
                appointment_table_exists = inspector.has_table(
                    'appointment', schema='public')
                bill_exists = inspector.has_table(
                    'bill', schema='public')
                doctor_table_exists = inspector.has_table(
                    'doctor', schema='public')
                inventory_table_exists = inspector.has_table(
                    'inventory', schema='public')
                patient_table_exist = inspector.has_table(
                    'patient', schema='public')
                role_table_exist = inspector.has_table(
                    'role', schema='public')
                user_table_exist = inspector.has_table(
                    'user', schema='public')
                user_roles_table_exists = inspector.has_table(
                    'user_roles', schema='public')
                tables = (appointment_table_exists, bill_exists, doctor_table_exists,
                          inventory_table_exists, patient_table_exist, role_table_exist, user_table_exist, user_roles_table_exists)

                # Check if any table does not exist
                if False in tables:
                    Base.metadata.create_all(connection)
                    print("Tables created")
                    # Create initial data if tables were created
                    current_dir = os.getcwd()
                    sql_file_path = os.path.join(current_dir, 'init.sql')
                    with open(sql_file_path, encoding='utf-8', mode='r') as f:
                        sql_script = f.read()
                        statements = sql_script.split(';')
                        for statement in statements:
                            if statement.strip():
                                connection.execute(text(statement))
                        connection.commit()
                    return True
                else:
                    return False

            result = await conn.run_sync(check_tables_and_data)
            if result is False:
                print("Tables already exist.")
        except Exception as e:
            print("==========================")
            print(f"An error occurred: {e}")
        finally:
            await engine.dispose()

asyncio.run(create_tables())
