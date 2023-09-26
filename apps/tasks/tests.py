import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APIClient

from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import User

from apps.tasks.models import Task, Comment, TimeLog, Timer


class TestTasks(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create(first_name='User',
                                        last_name='For Testing',
                                        email='string@mail.ogg',
                                        password='StrongPassword')
        self.client.force_authenticate(user=self.user)
        self.task = Task.objects.create(title='Task to be used for testing.', assigned_to=self.user, created_by=self.user)

    def test_create_task(self):
        data = {
            "title": "string",
            "description": "string",
            "assigned_to": self.user.id
        }

        response = self.client.post(reverse('tasks-list'), data)

        self.assertEqual(201, response.status_code)

    def test_get_tasks(self):
        Task.objects.create(title='A interesting tile', assigned_to=self.user, created_by=self.user)

        response = self.client.get(reverse('tasks-list'))

        self.assertEqual(200, response.status_code)

    def test_get_tasks_by_id(self):
        task = Task.objects.create(title='A interesting tile', assigned_to=self.user, created_by=self.user)

        response = self.client.get(reverse('tasks-detail', kwargs={'pk': task.id}))

        self.assertEqual(200, response.status_code)

    def test_completed_tasks(self):
        Task.objects.create(title='A complete task', status='completed', assigned_to=self.user, created_by=self.user)
        Task.objects.create(title='Incomplete task', status='to_do', assigned_to=self.user, created_by=self.user)

        base_url = reverse('tasks-list')
        response = self.client.get(base_url + '?status=completed')

        self.assertEqual(200, response.status_code)

    def test_assign_task(self):
        task = Task.objects.create(title='Task to be assigned', assigned_to=self.user, created_by=self.user)
        user = User.objects.create(email='test@assign.com')

        data = {
            "assigned_to": user.id
        }
        response = self.client.patch(reverse('tasks-detail', kwargs={'pk': task.id}), data)

        self.assertEqual(200, response.status_code)

    def test_complete_task(self):
        task = Task.objects.create(title='Task to be completed', assigned_to=self.user, created_by=self.user)

        response = self.client.post(reverse('tasks-complete', kwargs={'pk': task.id}))

        self.assertEqual(200, response.status_code)

    def test_remove_task(self):
        task = Task.objects.create(title='Task to be deleted', assigned_to=self.user, created_by=self.user)

        response = self.client.delete(reverse('tasks-detail', kwargs={'pk': task.id}))

        self.assertEqual(204, response.status_code)

    def test_search_task(self):
        Task.objects.create(title='Task to be found.', assigned_to=self.user, created_by=self.user)

        base_url = reverse('tasks-list')
        response = self.client.get(base_url + '?search=found')

        self.assertEqual(200, response.status_code)

    def test_top20(self):
        timelog = TimeLog.objects.create(
            started_at=timezone.datetime(2023, 6, 22, 1, 22, 33),
            duration=datetime.timedelta(days=33),
            task_id=self.task.id,
            user_id=self.user.id
        )

        response = self.client.get(reverse('tasks-top20'))

        self.assertEqual(200, response.status_code)

        self.assertEqual(f'Timelog of \"{self.task.title}\" id({timelog.id})', str(timelog))


class TestComments(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create(email='string@mail.ogg', password='StrongPassword')
        self.client.force_authenticate(user=self.user, token=f'Bearer {RefreshToken.for_user(self.user)}')
        self.task = Task.objects.create(title='Task to be commented', assigned_to=self.user, created_by=self.user)

    def test_create_comment(self):
        data = {
            "task": self.task.id,
            "text": "New comment"
        }

        response = self.client.post(reverse('comments-list'), data)

        self.assertEqual(201, response.status_code)

    def test_list_comment(self):
        comment = Comment.objects.create(task_id=self.task.id, text='Testing comments')

        base_url = reverse('comments-list')

        response = self.client.get(base_url + f'?task={self.task.id}')

        self.assertEqual(200, response.status_code)

        self.assertEqual(f'{self.task.title} : Testing comments', str(comment))


class TestTimers(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create(email='string@mail.ogg', password='StrongPassword')
        self.client.force_authenticate(user=self.user, token=f'Bearer {RefreshToken.for_user(self.user)}')
        self.task = Task.objects.create(title='Testing timers', assigned_to=self.user, created_by=self.user)

    def test_start_timer(self):
        response = self.client.post(reverse('tasks-start', kwargs={'pk': self.task.id}))

        self.assertEqual(200, response.status_code)

    def test_stop_timer(self):
        Timer.objects.create(task_id=self.task.id, user_id=self.user.id, is_started=True,)

        response = self.client.post(reverse('tasks-stop', kwargs={'pk': self.task.id}))

        self.assertEqual(200, response.status_code)

    def test_stop_stale_timer(self):
        Timer.objects.create(task_id=self.task.id, user_id=self.user.id, is_started=False)

        response = self.client.post(reverse('tasks-stop', kwargs={'pk': self.task.id}))

        self.assertEqual(400, response.status_code)

    def test_add_time_log(self):
        data = {
            "started_at": "2023-07-28T11:10:25.210Z",
            "duration": "33.2",
            "task": self.task.id,
            "user": self.user.id
        }
        response = self.client.post(reverse('timelog-list'), data)

        self.assertEqual(201, response.status_code)

    def test_get_timelog_by_taskid(self):
        TimeLog.objects.create(
            started_at=timezone.datetime(2023, 7, 22, 1, 22, 33),
            duration=datetime.timedelta(days=33),
            task_id=self.task.id,
            user_id=self.user.id
        )
        base_url = reverse('timelog-list')

        response = self.client.get(base_url + f'?task={self.task.id}')

        self.assertEqual(200, response.status_code)

    def test_get_total_time_last_month(self):
        TimeLog.objects.create(
            started_at=timezone.datetime(2023, 7, 22, 1, 22, 33),
            duration=datetime.timedelta(days=33),
            task_id=self.task.id,
            user_id=self.user.id
        )

        TimeLog.objects.create(
            started_at=timezone.datetime(2023, 8, 21, 1, 22, 33),
            duration=datetime.timedelta(days=33),
            task_id=self.task.id,
            user_id=self.user.id
        )

        response = self.client.get(reverse('timelog-mytime'))

        self.assertEqual(200, response.status_code)


