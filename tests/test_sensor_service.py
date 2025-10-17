import unittest
from unittest.mock import AsyncMock
from uuid import uuid4
from conftest import record_pid

from src.sensor_track_pro.business_logic.services.sensor_service import SensorService

class TestSensorService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = AsyncMock()
        self.service = SensorService(self.repo)
        record_pid()

    async def test_create_sensor(self):
        data = {}
        expected = {'result': 'sensor_created'}
        self.repo.create.return_value = expected
        result = await self.service.create_sensor(data)
        self.repo.create.assert_awaited_once_with(data)
        self.assertEqual(result, expected)

    async def test_get_sensor(self):
        sid = uuid4()
        expected = {'id': sid}
        self.repo.get_by_id.return_value = expected
        result = await self.service.get_sensor(sid)
        self.repo.get_by_id.assert_awaited_once_with(sid)
        self.assertEqual(result, expected)

    async def test_get_sensors(self):
        expected = [{'result': 'sensor_list'}]
        self.repo.get_all.return_value = expected
        result = await self.service.get_sensors(5, 10, dummy='value')
        self.repo.get_all.assert_awaited_once_with(5, 10, dummy='value')
        self.assertEqual(result, expected)

    async def test_update_sensor(self):
        sid = uuid4()
        data = {'status': 'active'}
        expected = {'result': 'sensor_updated'}
        self.repo.update.return_value = expected
        result = await self.service.update_sensor(sid, data)
        self.repo.update.assert_awaited_once_with(sid, data)
        self.assertEqual(result, expected)

    async def test_delete_sensor(self):
        sid = uuid4()
        self.repo.delete.return_value = True
        result = await self.service.delete_sensor(sid)
        self.repo.delete.assert_awaited_once_with(sid)
        self.assertTrue(result)

    async def test_get_sensors_by_object(self):
        oid = uuid4()
        expected = [{'result': 'sensor'}]
        self.repo.get_by_object_id.return_value = expected
        result = await self.service.get_sensors_by_object(oid)
        self.repo.get_by_object_id.assert_awaited_once_with(oid)
        self.assertEqual(result, expected)

    async def test_get_sensors_by_type(self):
        sensor_type = 'temp'
        expected = [{'result': 'sensor'}]
        self.repo.get_by_type.return_value = expected
        result = await self.service.get_sensors_by_type(sensor_type)
        self.repo.get_by_type.assert_awaited_once_with(sensor_type)
        self.assertEqual(result, expected)

    async def test_get_sensors_by_status(self):
        status = 'active'
        expected = [{'result': 'sensor'}]
        self.repo.get_by_status.return_value = expected
        result = await self.service.get_sensors_by_status(status)
        self.repo.get_by_status.assert_awaited_once_with(status)
        self.assertEqual(result, expected)

    # Негативные тесты
    async def test_get_sensor_not_found(self):
        sid = uuid4()
        self.repo.get_by_id.return_value = None
        result = await self.service.get_sensor(sid)
        self.assertIsNone(result)

    async def test_delete_sensor_failure(self):
        sid = uuid4()
        self.repo.delete.return_value = False
        result = await self.service.delete_sensor(sid)
        self.repo.delete.assert_awaited_once_with(sid)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()