import unittest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime
from conftest import record_pid

from src.sensor_track_pro.business_logic.services.event_service import EventService

class TestEventService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = AsyncMock()
        self.service = EventService(self.repo)
        record_pid()

    async def test_create_event(self):
        data = {}
        expected = {'result': 'event_created'}
        self.repo.create.return_value = expected
        result = await self.service.create_event(data)
        self.repo.create.assert_awaited_once_with(data)
        self.assertEqual(result, expected)

    async def test_get_event(self):
        eid = 1
        expected = {'id': eid}
        self.repo.get_by_id.return_value = expected
        result = await self.service.get_event(eid)
        self.repo.get_by_id.assert_awaited_once_with(eid)
        self.assertEqual(result, expected)

    async def test_get_events(self):
        expected = [{'result': 'event_list'}]
        self.repo.get_all.return_value = expected
        result = await self.service.get_events(0, 10, dummy='value')
        self.repo.get_all.assert_awaited_once_with(0, 10, dummy='value')
        self.assertEqual(result, expected)

    async def test_update_event(self):
        eid = 1
        data = {'param': 'value'}
        expected = {'result': 'event_updated'}
        self.repo.update.return_value = expected
        result = await self.service.update_event(eid, data)
        self.repo.update.assert_awaited_once_with(eid, data)
        self.assertEqual(result, expected)

    async def test_delete_event(self):
        eid = 1
        self.repo.delete.return_value = True
        result = await self.service.delete_event(eid)
        self.repo.delete.assert_awaited_once_with(eid)
        self.assertTrue(result)

    async def test_get_events_by_sensor(self):
        sid = uuid4()
        expected = [{'result': 'event'}]
        self.repo.get_by_sensor_id.return_value = expected
        result = await self.service.get_events_by_sensor(sid)
        self.repo.get_by_sensor_id.assert_awaited_once_with(sid)
        self.assertEqual(result, expected)

    async def test_get_events_by_timerange(self):
        start = datetime.now()
        end = datetime.now()
        expected = [{'result': 'event'}]
        self.repo.get_by_time_range.return_value = expected
        result = await self.service.get_events_by_timerange(start, end)
        self.repo.get_by_time_range.assert_awaited_once_with(start, end)
        self.assertEqual(result, expected)

    async def test_get_events_by_coordinates(self):
        lat, lon, rad = 1.0, 2.0, 5.0
        expected = [{'result': 'event'}]
        self.repo.get_by_coordinates.return_value = expected
        result = await self.service.get_events_by_coordinates(lat, lon, rad)
        # сервис передаёт параметры пагинации (skip=0, limit=100) как позиционные аргументы
        self.repo.get_by_coordinates.assert_awaited_once_with(lat, lon, rad, 0, 100)
        assert result == expected

    # Негативные тесты
    async def test_create_event_repo_error(self):
        data = {}
        self.repo.create.side_effect = Exception('create error')
        with self.assertRaises(Exception):
            await self.service.create_event(data)

    async def test_get_events_by_coordinates_repo_error(self):
        lat, lon, rad = 1.0, 2.0, 5.0
        self.repo.get_by_coordinates.side_effect = Exception('coords error')
        with self.assertRaises(Exception):
            await self.service.get_events_by_coordinates(lat, lon, rad)

if __name__ == '__main__':
    unittest.main()