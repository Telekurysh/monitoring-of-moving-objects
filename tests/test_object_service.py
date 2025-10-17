import unittest
from unittest.mock import AsyncMock
from uuid import uuid4
from conftest import record_pid

from src.sensor_track_pro.business_logic.services.object_service import ObjectService

class TestObjectService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = AsyncMock()
        self.service = ObjectService(self.repo)
        record_pid()

    async def test_create_object(self):
        data = {}
        expected = {'result': 'object_created'}
        self.repo.create.return_value = expected
        result = await self.service.create_object(data)
        self.repo.create.assert_awaited_once_with(data)
        self.assertEqual(result, expected)

    async def test_get_object(self):
        oid = uuid4()
        expected = {'id': oid}
        self.repo.get_by_id.return_value = expected
        result = await self.service.get_object(oid)
        self.repo.get_by_id.assert_awaited_once_with(oid)
        self.assertEqual(result, expected)

    async def test_get_objects(self):
        expected = [{'result': 'object_list'}]
        self.repo.get_all.return_value = expected
        result = await self.service.get_objects(0, 10, dummy='value')
        self.repo.get_all.assert_awaited_once_with(0, 10, dummy='value')
        self.assertEqual(result, expected)

    async def test_update_object(self):
        oid = uuid4()
        # Передаём объект с методом model_dump, как ожидает сервис
        class DummyModel:
            def __init__(self, d):
                self._d = d
            def model_dump(self, exclude_unset=True):
                return self._d

        data = DummyModel({'name': 'updated'})
        expected = {'result': 'object_updated'}
        self.repo.update.return_value = expected
        result = await self.service.update_object(oid, data)
        # сервис вызывает repository.update с уже распакованными данными
        self.repo.update.assert_awaited_once_with(oid, {'name': 'updated'})
        assert result == expected

    async def test_delete_object(self):
        oid = uuid4()
        self.repo.delete.return_value = True
        result = await self.service.delete_object(oid)
        self.repo.delete.assert_awaited_once_with(oid)
        self.assertTrue(result)

    async def test_get_objects_by_type(self):
        otype = 'type'
        expected = [{'result': 'object'}]
        self.repo.get_by_type.return_value = expected
        result = await self.service.get_objects_by_type(otype, 0, 10)
        self.repo.get_by_type.assert_awaited_once_with(otype, 0, 10)
        self.assertEqual(result, expected)

    # Негативные тесты
    async def test_update_object_repo_error(self):
        oid = uuid4()
        class DummyModel:
            def model_dump(self, exclude_unset=True):
                return {'name': 'x'}
        data = DummyModel()
        self.repo.update.side_effect = Exception('update failed')
        with self.assertRaises(Exception):
            await self.service.update_object(oid, data)

    async def test_get_objects_by_type_empty(self):
        otype = 'type'
        self.repo.get_by_type.return_value = []
        result = await self.service.get_objects_by_type(otype, 0, 10)
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()