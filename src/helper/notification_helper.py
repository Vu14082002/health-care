


from src.repositories.notification_repository import NotificationRepository


class NotificationHelper:
    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository

    def get_all_notifications(self,user_id:int):
        return self.notification_repository.get_all_notifications(user_id= user_id)
    def get_all_unread_notifications(self,user_id:int):
        return self.notification_repository.get_total_message_unread(session=self.notification_repository.session, user_id=user_id)
