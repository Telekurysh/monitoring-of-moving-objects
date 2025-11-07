import unittest
import allure
from unittest.mock import AsyncMock
from uuid import uuid4
from conftest import record_pid

from src.sensor_track_pro.business_logic.services.zone_service import ZoneService

@allure.epic("Business Logic Services")
@allure.feature("Zone Service")
class TestZoneService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = AsyncMock()
        self.service = ZoneService(self.repo)
        record_pid()
    
    @allure.story("Create Zone")
    async def test_create_zone(self):
        zone_data = {}
        expected = {'result': 'zone_created'}
        self.repo.create_zone.return_value = expected
        result = await self.service.create_zone(zone_data)
        self.repo.create_zone.assert_awaited_once_with(zone_data)
        self.assertEqual(result, expected)

    @allure.story("Get Zone")
    async def test_get_zone(self):
        zone_id = uuid4()
        expected = {'id': zone_id}
        self.repo.get_by_id.return_value = expected
        result = await self.service.get_zone(zone_id)
        self.repo.get_by_id.assert_awaited_once_with(zone_id)
        self.assertEqual(result, expected)

    @allure.story("Get Zones")
    async def test_get_zones(self):
        expected = [{'result': 'zone_list'}]
        self.repo.get_all.return_value = expected
        result = await self.service.get_zones(10, 5, dummy='value')
        self.repo.get_all.assert_awaited_once_with(10, 5, dummy='value')
        self.assertEqual(result, expected)

    @allure.story("Update Zone")
    async def test_update_zone(self):
        zone_id = uuid4()
        zone_data = {'name': 'new_zone'}
        expected = {'result': 'zone_updated'}
        self.repo.update.return_value = expected
        result = await self.service.update_zone(zone_id, zone_data)
        self.repo.update.assert_awaited_once_with(zone_id, zone_data)
        self.assertEqual(result, expected)

    @allure.story("Delete Zone")
    async def test_delete_zone(self):
        zone_id = uuid4()
        self.repo.delete.return_value = True
        result = await self.service.delete_zone(zone_id)
        self.repo.delete.assert_awaited_once_with(zone_id)
        self.assertTrue(result)

    @allure.story("Get Zones by Type")
    async def test_get_zones_by_type(self):
        zone_type = 'test_type'
        expected = [{'result': 'zone'}]
        self.repo.get_by_type.return_value = expected
        result = await self.service.get_zones_by_type(zone_type)
        self.repo.get_by_type.assert_awaited_once_with(zone_type)
        self.assertEqual(result, expected)

    @allure.story("Get Zones Containing Point")
    async def test_get_zones_containing_point(self):
        lat, lon = 1.0, 2.0
        expected = [{'result': 'zone'}]
        self.repo.get_zones_containing_point.return_value = expected
        result = await self.service.get_zones_containing_point(lat, lon)
        self.repo.get_zones_containing_point.assert_awaited_once_with(lat, lon)
        self.assertEqual(result, expected)

    @allure.story("Get Zones For Object")
    async def test_get_zones_for_object(self):
        obj_id = uuid4()
        expected = [{'result': 'zone'}]
        self.repo.get_zones_for_object.return_value = expected
        result = await self.service.get_zones_for_object(obj_id)
        self.repo.get_zones_for_object.assert_awaited_once_with(obj_id)
        self.assertEqual(result, expected)

    # Негативные тесты
    @allure.story("Create Zone Repo Error")
    async def test_create_zone_repo_error(self):
        zone_data = {}
        self.repo.create_zone.side_effect = Exception('repo error')
        with self.assertRaises(Exception):
            await self.service.create_zone(zone_data)

    @allure.story("Get Zone not Found")
    async def test_get_zone_not_found(self):
        zone_id = uuid4()
        self.repo.get_by_id.return_value = None
        result = await self.service.get_zone(zone_id)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()