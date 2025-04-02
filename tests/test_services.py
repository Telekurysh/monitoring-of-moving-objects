import unittest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime

# Импорт сервисов
from src.sensor_track_pro.business_logic.services.zone_service import ZoneService
from src.sensor_track_pro.business_logic.services.user_service import UserService
from src.sensor_track_pro.business_logic.services.telemetry_service import TelemetryService
from src.sensor_track_pro.business_logic.services.sensor_service import SensorService
from src.sensor_track_pro.business_logic.services.route_service import RouteService
from src.sensor_track_pro.business_logic.services.object_service import ObjectService
from src.sensor_track_pro.business_logic.services.event_service import EventService
from src.sensor_track_pro.business_logic.services.alert_service import AlertService


class TestZoneService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = AsyncMock()
        self.service = ZoneService(self.repo)

    async def test_create_zone(self):
        zone_data = {}  # тестовые данные
        expected = {'result': 'zone_created'}
        self.repo.create.return_value = expected
        result = await self.service.create_zone(zone_data)
        self.repo.create.assert_awaited_once_with(zone_data)
        self.assertEqual(result, expected)

    async def test_get_zone(self):
        zone_id = uuid4()
        expected = {'id': zone_id}
        self.repo.get_by_id.return_value = expected
        result = await self.service.get_zone(zone_id)
        self.repo.get_by_id.assert_awaited_once_with(zone_id)
        self.assertEqual(result, expected)

    async def test_get_zones(self):
        expected = [{'result': 'zone_list'}]
        self.repo.get_all.return_value = expected
        result = await self.service.get_zones(10, 5, dummy='value')
        self.repo.get_all.assert_awaited_once_with(10, 5, dummy='value')
        self.assertEqual(result, expected)

    async def test_update_zone(self):
        zone_id = uuid4()
        zone_data = {'name': 'new_zone'}
        expected = {'result': 'zone_updated'}
        self.repo.update.return_value = expected
        result = await self.service.update_zone(zone_id, zone_data)
        self.repo.update.assert_awaited_once_with(zone_id, zone_data)
        self.assertEqual(result, expected)

    async def test_delete_zone(self):
        zone_id = uuid4()
        self.repo.delete.return_value = True
        result = await self.service.delete_zone(zone_id)
        self.repo.delete.assert_awaited_once_with(zone_id)
        self.assertTrue(result)

    async def test_get_zones_by_type(self):
        zone_type = 'test_type'
        expected = [{'result': 'zone'}]
        self.repo.get_by_type.return_value = expected
        result = await self.service.get_zones_by_type(zone_type)
        self.repo.get_by_type.assert_awaited_once_with(zone_type)
        self.assertEqual(result, expected)

    async def test_get_zones_containing_point(self):
        lat, lon = 1.0, 2.0
        expected = [{'result': 'zone'}]
        self.repo.get_zones_containing_point.return_value = expected
        result = await self.service.get_zones_containing_point(lat, lon)
        self.repo.get_zones_containing_point.assert_awaited_once_with(lat, lon)
        self.assertEqual(result, expected)

    async def test_get_zones_for_object(self):
        obj_id = uuid4()
        expected = [{'result': 'zone'}]
        self.repo.get_zones_for_object.return_value = expected
        result = await self.service.get_zones_for_object(obj_id)
        self.repo.get_zones_for_object.assert_awaited_once_with(obj_id)
        self.assertEqual(result, expected)


class TestUserService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = AsyncMock()
        self.service = UserService(self.repo)

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


class TestTelemetryService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = AsyncMock()
        self.service = TelemetryService(self.repo)

    async def test_create_telemetry(self):
        data = {}
        expected = {'result': 'telemetry_created'}
        self.repo.create.return_value = expected
        result = await self.service.create_telemetry(data)
        self.repo.create.assert_awaited_once_with(data)
        self.assertEqual(result, expected)

    async def test_get_telemetry(self):
        tid = uuid4()
        expected = {'id': tid}
        self.repo.get_by_id.return_value = expected
        result = await self.service.get_telemetry(tid)
        self.repo.get_by_id.assert_awaited_once_with(tid)
        self.assertEqual(result, expected)

    async def test_get_all_telemetry(self):
        expected = [{'result': 'telemetry_list'}]
        self.repo.get_all.return_value = expected
        result = await self.service.get_all_telemetry(0, 10, dummy='value')
        self.repo.get_all.assert_awaited_once_with(0, 10, dummy='value')
        self.assertEqual(result, expected)

    async def test_update_telemetry(self):
        tid = uuid4()
        data = {'param': 'value'}
        expected = {'result': 'telemetry_updated'}
        self.repo.update.return_value = expected
        result = await self.service.update_telemetry(tid, data)
        self.repo.update.assert_awaited_once_with(tid, data)
        self.assertEqual(result, expected)

    async def test_delete_telemetry(self):
        tid = uuid4()
        self.repo.delete.return_value = True
        result = await self.service.delete_telemetry(tid)
        self.repo.delete.assert_awaited_once_with(tid)
        self.assertTrue(result)

    async def test_get_telemetry_by_object(self):
        oid = uuid4()
        expected = [{'result': 'telemetry'}]
        self.repo.get_by_object_id.return_value = expected
        result = await self.service.get_telemetry_by_object(oid)
        self.repo.get_by_object_id.assert_awaited_once_with(oid)
        self.assertEqual(result, expected)

    async def test_get_telemetry_by_timerange(self):
        start = datetime.now()
        end = datetime.now()
        expected = [{'result': 'telemetry'}]
        self.repo.get_by_time_range.return_value = expected
        result = await self.service.get_telemetry_by_timerange(start, end)
        self.repo.get_by_time_range.assert_awaited_once_with(start, end)
        self.assertEqual(result, expected)

    async def test_get_telemetry_by_signal_strength(self):
        expected = [{'result': 'telemetry'}]
        self.repo.get_by_signal_strength.return_value = expected
        result = await self.service.get_telemetry_by_signal_strength(0.5, 2.5)
        self.repo.get_by_signal_strength.assert_awaited_once_with(0.5, 2.5)
        self.assertEqual(result, expected)


class TestSensorService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = AsyncMock()
        self.service = SensorService(self.repo)

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


class TestRouteService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = AsyncMock()
        self.service = RouteService(self.repo)

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


class TestObjectService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = AsyncMock()
        self.service = ObjectService(self.repo)

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
        data = {'name': 'updated'}
        expected = {'result': 'object_updated'}
        self.repo.update.return_value = expected
        result = await self.service.update_object(oid, data)
        self.repo.update.assert_awaited_once_with(oid, data)
        self.assertEqual(result, expected)

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


class TestEventService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = AsyncMock()
        self.service = EventService(self.repo)

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
        self.repo.get_by_coordinates.assert_awaited_once_with(lat, lon, rad)
        self.assertEqual(result, expected)


class TestAlertService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = AsyncMock()
        self.service = AlertService(self.repo)

    async def test_create_alert(self):
        data = {}
        expected = {'result': 'alert_created'}
        self.repo.create.return_value = expected
        result = await self.service.create_alert(data)
        self.repo.create.assert_awaited_once_with(data)
        self.assertEqual(result, expected)

    async def test_get_alert(self):
        aid = uuid4()
        expected = {'id': aid}
        self.repo.get_by_id.return_value = expected
        result = await self.service.get_alert(aid)
        self.repo.get_by_id.assert_awaited_once_with(aid)
        self.assertEqual(result, expected)

    async def test_get_alerts(self):
        expected = [{'result': 'alert_list'}]
        self.repo.get_all.return_value = expected
        result = await self.service.get_alerts(0, 10, dummy='value')
        self.repo.get_all.assert_awaited_once_with(0, 10, dummy='value')
        self.assertEqual(result, expected)

    async def test_update_alert(self):
        aid = uuid4()
        data = {'level': 'high'}
        expected = {'result': 'alert_updated'}
        self.repo.update.return_value = expected
        result = await self.service.update_alert(aid, data)
        self.repo.update.assert_awaited_once_with(aid, data)
        self.assertEqual(result, expected)

    async def test_delete_alert(self):
        aid = uuid4()
        self.repo.delete.return_value = True
        result = await self.service.delete_alert(aid)
        self.repo.delete.assert_awaited_once_with(aid)
        self.assertTrue(result)

    async def test_get_alerts_by_event(self):
        eid = uuid4()
        expected = [{'result': 'alert'}]
        self.repo.get_by_event_id.return_value = expected
        result = await self.service.get_alerts_by_event(eid)
        self.repo.get_by_event_id.assert_awaited_once_with(eid)
        self.assertEqual(result, expected)

    async def test_get_alerts_by_severity(self):
        severity = 'critical'
        expected = [{'result': 'alert'}]
        self.repo.get_by_severity.return_value = expected
        result = await self.service.get_alerts_by_severity(severity)
        self.repo.get_by_severity.assert_awaited_once_with(severity)
        self.assertEqual(result, expected)

    async def test_get_alerts_by_type(self):
        atype = 'system'
        expected = [{'result': 'alert'}]
        self.repo.get_by_type.return_value = expected
        result = await self.service.get_alerts_by_type(atype)
        self.repo.get_by_type.assert_awaited_once_with(atype)
        self.assertEqual(result, expected)

    async def test_get_alerts_by_timerange(self):
        start = datetime.now()
        end = datetime.now()
        expected = [{'result': 'alert'}]
        self.repo.get_by_time_range.return_value = expected
        result = await self.service.get_alerts_by_timerange(start, end)
        self.repo.get_by_time_range.assert_awaited_once_with(start, end)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()