import unittest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime
from conftest import record_pid

from src.sensor_track_pro.business_logic.services.route_service import RouteService

class TestRouteService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = AsyncMock()
        self.service = RouteService(self.repo)
        record_pid()

    async def test_create_route(self):
        data = {}
        expected = {'result': 'route_created'}
        self.repo.create.return_value = expected
        result = await self.service.create_route(data)
        self.repo.create.assert_awaited_once_with(data)
        self.assertEqual(result, expected)

    async def test_get_route(self):
        rid = uuid4()
        expected = {'id': rid}
        self.repo.get_by_id.return_value = expected
        result = await self.service.get_route(rid)
        self.repo.get_by_id.assert_awaited_once_with(rid)
        self.assertEqual(result, expected)

    async def test_get_routes(self):
        expected = [{'result': 'route_list'}]
        self.repo.get_all.return_value = expected
        result = await self.service.get_routes(0, 10, dummy='value')
        self.repo.get_all.assert_awaited_once_with(0, 10, dummy='value')
        self.assertEqual(result, expected)

    async def test_update_route(self):
        rid = uuid4()
        data = {'status': 'updated'}
        expected = {'result': 'route_updated'}
        self.repo.update.return_value = expected
        result = await self.service.update_route(rid, data)
        self.repo.update.assert_awaited_once_with(rid, data)
        self.assertEqual(result, expected)

    async def test_delete_route(self):
        rid = uuid4()
        self.repo.delete.return_value = True
        result = await self.service.delete_route(rid)
        self.repo.delete.assert_awaited_once_with(rid)
        self.assertTrue(result)

    async def test_get_routes_by_object(self):
        oid = uuid4()
        expected = [{'result': 'route'}]
        self.repo.get_by_object_id.return_value = expected
        result = await self.service.get_routes_by_object(oid)
        self.repo.get_by_object_id.assert_awaited_once_with(oid)
        self.assertEqual(result, expected)

    async def test_get_routes_by_status(self):
        status = 'active'
        expected = [{'result': 'route'}]
        self.repo.get_by_status.return_value = expected
        result = await self.service.get_routes_by_status(status)
        self.repo.get_by_status.assert_awaited_once_with(status)
        self.assertEqual(result, expected)

    async def test_get_active_routes(self):
        expected = [{'result': 'active_route'}]
        self.repo.get_active_routes.return_value = expected
        result = await self.service.get_active_routes()
        self.repo.get_active_routes.assert_awaited_once()
        self.assertEqual(result, expected)

    async def test_get_routes_by_timerange(self):
        start = datetime.now()
        end = datetime.now()
        expected = [{'result': 'route_time'}]
        self.repo.get_by_time_range.return_value = expected
        result = await self.service.get_routes_by_timerange(start, end)
        self.repo.get_by_time_range.assert_awaited_once_with(start, end)
        self.assertEqual(result, expected)

    # Негативные тесты
    async def test_get_route_not_found(self):
        rid = uuid4()
        self.repo.get_by_id.return_value = None
        result = await self.service.get_route(rid)
        self.assertIsNone(result)

    async def test_get_active_routes_empty(self):
        self.repo.get_active_routes.return_value = []
        result = await self.service.get_active_routes()
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()