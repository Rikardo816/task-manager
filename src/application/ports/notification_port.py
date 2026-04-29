from abc import ABC, abstractmethod


class NotificationPort(ABC):
    @abstractmethod
    async def send_task_assignment_notification(
        self,
        assignee_email: str,
        assignee_username: str,
        task_title: str,
        task_list_name: str,
        assigned_by_username: str,
    ) -> None: ...

    @abstractmethod
    async def send_task_list_invitation(
        self,
        invitee_email: str,
        invitee_username: str,
        task_list_name: str,
        invited_by_username: str,
    ) -> None: ...
