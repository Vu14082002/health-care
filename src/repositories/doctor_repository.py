import logging as log
from typing import Any, Dict, List, Optional, Sequence, Union

from sqlalchemy import select

from src.core.database.postgresql import PostgresRepository, Transactional
from src.models.doctor_model import DoctorModel
from src.repositories.global_func import destruct_where, process_orderby


class DoctorRepository(PostgresRepository[DoctorModel]):

    async def get_all(self, skip: int = 0, limit: int = 10, join_: set[str] | None = None, where: Optional[Dict[str, Any]] = None, order_by: Optional[Dict[str, str]] = None) -> list[DoctorModel]:
        if where is None:
            where = {}
        if order_by is None:
            order_by = {"created_at": "desc"}
        try:
            # condition: Any | None = destruct_where(
            #     self.model_class, where)
            # order_expressions: List[Any] = process_orderby(
            #     self.model_class, order_by)
            # query = select(self.model_class)

            # if condition is not None:
            #     query = query.where(condition)
            # query = query.order_by(
            #     *order_expressions).offset(skip).limit(limit)
            # result = await self.session.execute(query)

            # data: List[DoctorModel] = list(result.scalars().all())
            # return data
            doctors: list[DoctorModel] = await super().orm_get_all(skip, limit, join_, where, order_by)
            return doctors
        except Exception as e:
            log.error(e)
            raise e
