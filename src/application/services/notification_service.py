import structlog

logger = structlog.get_logger()


class NotificationService:
    """Simulated notification service.

    In production this would delegate to SES/SendGrid via an async HTTP call.
    All methods log a structured event so the behaviour is observable in tests
    and staging without sending real email.
    """

    async def send_task_assignment_notification(
        self,
        assignee_email: str,
        assignee_username: str,
        task_title: str,
        task_list_name: str,
        assigned_by_username: str,
    ) -> None:
        logger.info(
            "notification.task_assignment",
            to=assignee_email,
            assignee=assignee_username,
            task=task_title,
            task_list=task_list_name,
            assigned_by=assigned_by_username,
        )

    async def send_task_list_invitation(
        self,
        invitee_email: str,
        invitee_username: str,
        task_list_name: str,
        invited_by_username: str,
    ) -> None:
        logger.info(
            "notification.task_list_invitation",
            to=invitee_email,
            invitee=invitee_username,
            task_list=task_list_name,
            invited_by=invited_by_username,
        )
