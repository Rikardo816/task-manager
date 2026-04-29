from uuid import UUID

from src.application.dtos.task_dtos import TaskOutput
from src.application.services.notification_service import NotificationService
from src.application.use_cases.task.create_task import _to_output
from src.domain.exceptions.domain_exceptions import ForbiddenError, NotFoundError
from src.domain.repositories.task_list_repository import TaskListRepository
from src.domain.repositories.task_repository import TaskRepository
from src.domain.repositories.user_repository import UserRepository


class AssignTaskUseCase:
    def __init__(
        self,
        task_repo: TaskRepository,
        task_list_repo: TaskListRepository,
        user_repo: UserRepository,
        notification_service: NotificationService,
    ) -> None:
        self._task_repo = task_repo
        self._task_list_repo = task_list_repo
        self._user_repo = user_repo
        self._notification_service = notification_service

    async def execute(
        self,
        task_id: UUID,
        task_list_id: UUID,
        assignee_id: UUID,
        requester_id: UUID,
    ) -> TaskOutput:
        task_list = await self._task_list_repo.get_by_id(task_list_id)
        if not task_list:
            raise NotFoundError("TaskList", str(task_list_id))
        if task_list.owner_id != requester_id:
            raise ForbiddenError()

        task = await self._task_repo.get_by_id(task_id)
        if not task or task.task_list_id != task_list_id:
            raise NotFoundError("Task", str(task_id))

        assignee = await self._user_repo.get_by_id(assignee_id)
        if not assignee:
            raise NotFoundError("User", str(assignee_id))

        requester = await self._user_repo.get_by_id(requester_id)

        task.assign_to(assignee_id)
        updated = await self._task_repo.update(task)

        await self._notification_service.send_task_assignment_notification(
            assignee_email=assignee.email,
            assignee_username=assignee.username,
            task_title=task.title,
            task_list_name=task_list.name,
            assigned_by_username=requester.username if requester else "unknown",
        )
        return _to_output(updated)
