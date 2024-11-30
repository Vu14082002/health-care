from pydantic import BaseModel, Field


class RequestGetAllPatientSchema(BaseModel):
    current_page: int = Field(
        default=1,
        description="Page numebr current,if not assign default = 1",
        examples=[1],
    )
    page_size: int = Field(
        default=10,
        description="Number of records per page,if not assign default = 10",
        examples=[10],
    )
