import unittest
from unittest.mock import AsyncMock
from uuid import uuid4
from conftest import record_pid

from src.sensor_track_pro.business_logic.services.user_service import UserService

class TestUserService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = AsyncMock()
        self.service = UserService(self.repo)
        record_pid()

    async def test_create_user(self):
        user_data = {}
        password = 'secret'
        expected = {'result': 'user_created'}
        self.repo.create.return_value = expected
        result = await self.service.create_user(user_data, password)
        self.repo.create.assert_awaited_once_with(user_data, password)
        self.assertEqual(result, expected)

    async def test_authenticate_user(self):
        auth_data = {}
        expected = {'result': 'user_auth'}
        self.repo.authenticate.return_value = expected
        result = await self.service.authenticate_user(auth_data)
        self.repo.authenticate.assert_awaited_once_with(auth_data)
        self.assertEqual(result, expected)

    async def test_get_user(self):
        user_id = uuid4()
        expected = {'id': user_id}
        self.repo.get_by_id.return_value = expected
        result = await self.service.get_user(user_id)
        self.repo.get_by_id.assert_awaited_once_with(user_id)
        self.assertEqual(result, expected)

    async def test_get_users(self):
        expected = [{'result': 'user_list'}]
        self.repo.get_all.return_value = expected
        result = await self.service.get_users(0, 10, dummy='value')
        self.repo.get_all.assert_awaited_once_with(0, 10, dummy='value')
        self.assertEqual(result, expected)

    async def test_update_user(self):
        user_id = uuid4()
        user_data = {'email': 'test@test.com'}
        expected = {'result': 'user_updated'}
        self.repo.update.return_value = expected
        result = await self.service.update_user(user_id, user_data)
        self.repo.update.assert_awaited_once_with(user_id, user_data)
        self.assertEqual(result, expected)

    async def test_delete_user(self):
        user_id = uuid4()
        self.repo.delete.return_value = True
        result = await self.service.delete_user(user_id)
        self.repo.delete.assert_awaited_once_with(user_id)
        self.assertTrue(result)

    async def test_change_password(self):
        user_id = uuid4()
        new_password = 'new_secret'
        self.repo.change_password.return_value = True
        result = await self.service.change_password(user_id, new_password)
        self.repo.change_password.assert_awaited_once_with(user_id, new_password)
        self.assertTrue(result)

    # Негативные тесты
    async def test_authenticate_user_invalid(self):
        auth_data = {}
        self.repo.authenticate.return_value = None
        result = await self.service.authenticate_user(auth_data)
        self.assertIsNone(result)

    async def test_create_user_repo_error(self):
        user_data = {}
        password = 'secret'
        self.repo.create.side_effect = Exception('create failed')
        with self.assertRaises(Exception):
            await self.service.create_user(user_data, password)

if __name__ == '__main__':
    unittest.main()