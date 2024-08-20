
# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Optional, Sequence, Union

from sqlalchemy import (Float, Integer, and_, asc, cast, desc, func, not_, or_,
                        select, text)
from sqlalchemy.sql.elements import UnaryExpression
from sqlalchemy.sql.expression import between

from src.core.database.postgresql import Model


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


def process_orderby(model_class: Model, orderby: Dict[str, str]) -> List[UnaryExpression]:
    if not orderby:
        return []
    expressions: List[UnaryExpression] = []
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

    # how to use
    # case 1
    # Tìm người dùng có tên là "John"
    # where = {"name": "John"}
    # condition = destruct_where(User, where)
    # query = select(User).where(condition)

    # # Tìm người dùng có tuổi lớn hơn 18
    # where = {"age": {"$gt": 18}}
    # condition = destruct_where(User, where)
    # query = select(User).where(condition)

    # case 2
    # Tìm người dùng có tên là "John" và tuổi từ 25 đến 35
    # where = {
    #     "name": "John",
    #     "age": {"$gte": 25, "$lte": 35}
    # }
    # condition = destruct_where(User, where)
    # query = select(User).where(condition)

    # case3
    # Tìm người dùng có tên là "John" hoặc tuổi lớn hơn 30
    # where = {
    #     "$or": [
    #         {"name": "John"},
    #         {"age": {"$gt": 30}}
    #     ]
    # }
    # condition = destruct_where(User, where)
    # query = select(User).where(condition)

    # case4
    # Tìm người dùng có tên là "John" hoặc tuổi lớn hơn 30
    # where = {
    #     "$or": [
    #         {"name": "John"},
    #         {"age": {"$gt": 30}}
    #     ]
    # }
    # condition = destruct_where(User, where)
    # query = select(User).where(condition)

    # case 5
    # Tìm người dùng có (tên là "John" và tuổi > 25) hoặc (tên là "Jane" và tuổi < 30)
    # where = {
    #     "$or": [
    #         {"$and": [{"name": "John"}, {"age": {"$gt": 25}}]},
    #         {"$and": [{"name": "Jane"}, {"age": {"$lt": 30}}]}
    #     ]
    # }
    # condition = destruct_where(User, where)
    # query = select(User).where(condition)

    # case6
    # # Tìm người dùng có tag "python" và "sqlalchemy"
    # where = {
    #     "tags": {"$all": ["python", "sqlalchemy"]}
    # }
    # condition = destruct_where(User, where)
    # query = select(User).where(condition)

    # # Tìm người dùng có chính xác 3 tags
    # where = {
    #     "tags": {"$size": 3}
    # }
    # condition = destruct_where(User, where)
    # query = select(User).where(condition)

    # case 7
    # Tìm người dùng không có tuổi trong khoảng 20-30 và không có email kết thúc bằng "@example.com"
    # where = {
    #     "age": {"$not": {"$in": list(range(20, 31))}},
    #     "email": {"$not": {"$regex": "@example.com$"}}
    # }
    # condition = destruct_where(User, where)
    # query = select(User).where(condition)

    # case 8
    # Tìm người dùng có score lớn hơn age
    # where = {
    #     "$expr": "User.score > User.age"
    # }
    # condition = destruct_where(User, where)
    # query = select(User).where(condition)

    # case 9
