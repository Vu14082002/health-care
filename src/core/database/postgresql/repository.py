# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from functools import reduce
from operator import and_
from typing import Any, Dict, Generic, List, Type, TypeVar, Union

from sqlalchemy import (Boolean, Integer, Select, String, and_, asc, between,
                        desc, event, or_, select)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy.sql import func

Base = declarative_base()
ModelType = TypeVar("ModelType", bound=Base)


class PostgresRepository(Generic[ModelType]):
    """Base class for data repositories."""

    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self.session = db_session
        self.model_class: Type[ModelType] = model

    async def create(self, attributes: dict[str, Any] = None) -> ModelType:
        """
        Creates the model instance.

        :param attributes: The attributes to create the model with.
        :return: The created model instance.
        """
        if attributes is None:
            attributes = {}
        model = self.model_class(**attributes)
        self.session.add(model)
        return model

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        join_: set[str] | None = None,
        where: dict = None,
        order_by: tuple[str, str] | None = None,
    ) -> list[ModelType]:
        """
        Returns a list of model instances.

        :param skip: The number of records to skip.
        :param limit: The number of record to return.
        :param join_: The joins to make.
        :param where: The conditions for the WHERE clause.
        :return: A list of model instances.
        """
        query = self._query(join_)
        query = query.offset(skip).limit(limit)

        # if where is not None:
        #     conditions = []
        #     for k, v in where.items():
        #         if k != "$or":
        #             column = getattr(self.model_class, k)
        #             if isinstance(v, dict):
        #                 gt = v.get("$gt")
        #                 lt = v.get("$lt")
        #                 _or = v.get("$or")
        #                 nen = v.get("$ne")
        #                 if gt is not None and lt is not None:
        #                     conditions.append(between(column, gt, lt))
        #                 elif gt is not None:
        #                     conditions.append(column > gt)
        #                 elif lt is not None:
        #                     conditions.append(column < lt)
        #                 if _or is not None:
        #                     conditions.append(or_(*[column == i for i in _or]))
        #                 if nen is not None:
        #                     conditions.append(column != nen)
        #             else:
        #                 conditions.append(column == v)
        #         else:
        #             _or = v
        #             or_conditions = []
        #             for or_condition in _or:
        #                 for k, v in or_condition.items():
        #                     column = getattr(self.model_class, k)
        #                     or_conditions.append(column == v)
        #             conditions.append(or_(*or_conditions))

        #     # Kết hợp các điều kiện bằng `and_`
        query = query.where(destruct_where(self.model_class, where))

        if order_by is not None:
            column, direction = order_by
            if direction.lower() == "desc":
                query = query.order_by(desc(getattr(self.model_class, column)))
            else:
                query = query.order_by(asc(getattr(self.model_class, column)))

        if join_ is not None:
            return await self.all_unique(query)
        return await self._all(query)

    async def get_by(
        self,
        field: str,
        value: Any,
        join_: set[str] | None = None,
        unique: bool = False,
    ) -> ModelType:
        """
        Returns the model instance matching the field and value.

        :param field: The field to match.
        :param value: The value to match.
        :param join_: The joins to make.
        :return: The model instance.
        """
        query = self._query(join_)
        query = await self._get_by(query, field, value)

        if join_ is not None:
            return await self.all_unique(query)
        if unique:
            return await self._one(query)

        return await self._all(query)

    async def delete(self, model: ModelType) -> None:
        """
        Deletes the model.

        :param model: The model to delete.
        :return: None
        """
        await self.session.delete(model)

    async def update(self, model: ModelType, attributes: dict[str, Any]) -> ModelType:
        """
        Updates the model.

        :param model: The model to update.
        :param attributes: The attributes to update the model with.
        :return: The updated model instance.
        """
        for key, value in attributes.items():
            if hasattr(model, key):
                setattr(model, key, value)

        self.session.add(model)
        await self.session.commit()

        return model

    def _query(
        self,
        join_: set[str] | None = None,
        order_: dict | None = None,
    ) -> Select:
        """
        Returns a callable that can be used to query the model.

        :param join_: The joins to make.
        :param order_: The order of the results. (e.g desc, asc)
        :return: A callable that can be used to query the model.
        """
        query = select(self.model_class)
        query = self._maybe_join(query, join_)
        query = self._maybe_ordered(query, order_)

        return query

    async def _all(self, query: Select) -> list[ModelType]:
        """
        Returns all results from the query.

        :param query: The query to execute.
        :return: A list of model instances.
        """
        query = await self.session.scalars(query)
        return query.all()

    async def all_unique(self, query: Select) -> list[ModelType]:
        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def _first(self, query: Select) -> ModelType | None:
        """
        Returns the first result from the query.

        :param query: The query to execute.
        :return: The first model instance.
        """
        query = await self.session.scalars(query)
        return query.first()

    async def _one_or_none(self, query: Select) -> ModelType | None:
        """Returns the first result from the query or None."""
        query = await self.session.scalars(query)
        return query.one_or_none()

    async def _one(self, query: Select) -> ModelType:
        """
        Returns the first result from the query or raises NoResultFound.

        :param query: The query to execute.
        :return: The first model instance.
        """
        query = await self.session.scalars(query)
        return query.one()

    async def _count(self, query: Select) -> int:
        """
        Returns the count of the records.

        :param query: The query to execute.
        """
        query = query.subquery()
        query = await self.session.scalars(select(func.count()).select_from(query))
        return query.one()

    async def _sort_by(
        self,
        query: Select,
        sort_by: str,
        order: str | None = "asc",
        model: Type[ModelType] | None = None,
        case_insensitive: bool = False,
    ) -> Select:
        """
        Returns the query sorted by the given column.

        :param query: The query to sort.
        :param sort_by: The column to sort by.
        :param order: The order to sort by.
        :param model: The model to sort.
        :param case_insensitive: Whether to sort case insensitively.
        :return: The sorted query.
        """
        model = model or self.model_class

        order_column = None

        if case_insensitive:
            order_column = func.lower(getattr(model, sort_by))
        else:
            order_column = getattr(model, sort_by)

        if order == "desc":
            return query.order_by(order_column.desc())

        return query.order_by(order_column.asc())

    async def _get_by(self, query: Select, field: str, value: Any) -> Select:
        """
        Returns the query filtered by the given column.

        :param query: The query to filter.
        :param field: The column to filter by.
        :param value: The value to filter by.
        :return: The filtered query.
        """

        return query.where(getattr(self.model_class, field) == value)

    def _maybe_join(self, query: Select, join_: set[str] | None = None) -> Select:
        """
        Returns the query with the given joins.

        :param query: The query to join.
        :param join_: The joins to make.
        :return: The query with the given joins.
        """
        if not join_:
            return query

        if not isinstance(join_, set):
            raise TypeError("join_ must be a set")

        return reduce(self._add_join_to_query, join_, query)

    def _maybe_ordered(self, query: Select, order_: dict | None = None) -> Select:
        """
        Returns the query ordered by the given column.

        :param query: The query to order.
        :param order_: The order to make.
        :return: The query ordered by the given column.
        """
        if order_:
            if order_["asc"]:
                for order in order_["asc"]:
                    query = query.order_by(
                        getattr(self.model_class, order).asc())
            else:
                for order in order_["desc"]:
                    query = query.order_by(
                        getattr(self.model_class, order).desc())

        return query

    def _add_join_to_query(self, query: Select, join_: set[str]) -> Select:
        """
        Returns the query with the given join.

        :param query: The query to join.
        :param join_: The join to make.
        :return: The query with the given join.
        """
        return getattr(self, "_join_" + join_)(query)


class Model(Base):
    __abstract__ = True
    __table_args__ = {"extend_existing": True}

    created_at = mapped_column(
        name="created_at",
        type_=Integer,
        default=int(datetime.now(timezone.utc).timestamp())
    )

    updated_at = mapped_column(
        name="updated_at",
        type_=Integer,
        default=int(datetime.now(timezone.utc).timestamp()),
        onupdate=int(datetime.now(timezone.utc).timestamp())
    )
    is_deleted = mapped_column(name="is_deleted", type_=Boolean, default=False)

    @property
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @staticmethod
    def set_before_insert(mapper, connection, target):
        """Set timestamps before inserting a new record."""
        target.created_at = int(datetime.now(timezone.utc).timestamp())
        target.updated_at = int(datetime.now(timezone.utc).timestamp())

    @staticmethod
    def update_timestamps(mapper, connection, target):
        """Update timestamps before updating an existing record."""
        target.updated_at = int(datetime.now(timezone.utc).timestamp())


# Attach event listeners
event.listen(Model, "before_insert", Model.set_before_insert)
event.listen(Model, "before_update", Model.update_timestamps)


def destruct_where(model_class: Model, where: Dict[str, Any]) -> Union[Any, None]:
    """_summary_

    Args:
        model_class (_type_): is has type of ModelType
        where (dict): this is a dict: code like mongodb query

    Returns:
        _type_: _description_
    """
    if where is not {}:
        return process_condition(model_class, where)
    return None


def process_condition(model_class: Model, condition):
    """_summary_

    Args:
        model_class (_type_): _description_
        condition (_type_): _description_

    Returns:
        _type_: _description_
    """
    if not isinstance(condition, dict):
        return condition

    conditions = []
    for key, value in condition.items():
        if key == "$or":
            or_conditions: Any = [process_condition(
                model_class, cond) for cond in value]
            conditions.append(or_(*or_conditions))
        elif key == "$and":
            and_conditions: Any = [process_condition(
                model_class, cond) for cond in value]
            conditions.append(and_(*and_conditions))
        elif key.startswith("$"):
            conditions.append(process_operator(model_class, key, value))
        else:
            column = getattr(model_class, key)
            if isinstance(value, dict):
                conditions.append(process_column_operators(column, value))
            else:
                conditions.append(column == value)

    return and_(*conditions) if len(conditions) > 1 else conditions[0] if conditions else True


def process_column_operators(column, operators):
    """_summary_

    Args:
        column (_type_): _description_
        operators (_type_): _description_

    Returns:
        _type_: _description_
    """
    conditions = []
    for op, value in operators.items():
        if op == "$eq":
            conditions.append(column == value)
        elif op == "$ne":
            conditions.append(column != value)
        elif op == "$gt":
            conditions.append(column > value)
        elif op == "$gte":
            conditions.append(column >= value)
        elif op == "$lt":
            conditions.append(column < value)
        elif op == "$lte":
            conditions.append(column <= value)
        elif op == "$in":
            conditions.append(column.in_(value))
        elif op == "$nin":
            conditions.append(~column.in_(value))
        elif op == "$between":
            conditions.append(between(column, *value))
        elif op == "$like":
            conditions.append(column.like(value))
        elif op == "$ilike":
            conditions.append(column.ilike(value))
        elif op == "$regex":
            conditions.append(column.op("~")(value))
        elif op == "$iregex":
            conditions.append(column.op("~*")(value))
        elif op == "$exists":
            conditions.append(column is not None if value else column is None)
        elif op == "$type":
            conditions.append(column.type == value)
        elif op == "$not":
            conditions.append(not_(process_column_operators(column, value)))
        elif op == "$all":
            for item in value:
                conditions.append(column.contains(item))
        elif op == "$size":
            conditions.append(func.array_length(column, 1) == value)
        elif op == "$elemMatch":
            # This is a simplified version and may not work for all cases
            elem_conditions = process_column_operators(column.any(), value)
            conditions.append(column.any(elem_conditions))
    return and_(*conditions)


def process_operator(model_class, operator, value):
    """_summary_

    Args:
        model_class (_type_): _description_
        operator (_type_): _description_
        value (_type_): _description_

    Raises:
        NotImplementedError: _description_
        NotImplementedError: _description_
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    if operator == "$expr":
        # Simplified expression handling
        return text(value)
    elif operator == "$jsonSchema":
        # This would require more complex handling
        raise NotImplementedError("$jsonSchema is not implemented")
    elif operator == "$mod":
        column, divisor, remainder = value
        return func.mod(getattr(model_class, column), divisor) == remainder
    elif operator == "$text":
        # Simplified text search
        return func.to_tsvector('english', getattr(model_class, value['$search'])).match(value['$search'])
    elif operator == "$where":
        # This would require more complex handling and might be a security risk
        raise NotImplementedError(
            "$where is not implemented for security reasons")
    else:
        raise ValueError(f"Unsupported operator: {operator}")


def process_orderby(model_class: Model, orderby: Dict[str, str]):
    if not orderby:
        return []
    expressions = []
    for key, value in orderby.items():
        column = getattr(model_class, key, None)  # type: ignore
        if column is None:
            raise ValueError(f"Invalid column name: {key}")
        if value.lower() == "asc":
            expressions.append(asc(column))
        elif value.lower() == "desc":
            expressions.append(desc(column))
        else:
            raise ValueError(f"Invalid order direction: {value}")
    return expressions
