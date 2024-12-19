from pydantic import BaseModel, Field


class NotificationSchemaUPdateToRead(BaseModel):
    notification_id: int = Field(..., title="Notification id will update to read", examples=[1])

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
