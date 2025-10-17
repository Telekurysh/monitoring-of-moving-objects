import unittest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime
from conftest import record_pid

from src.sensor_track_pro.business_logic.services.alert_service import AlertService

class TestAlertService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = AsyncMock()
        self.service = AlertService(self.repo)
        record_pid()

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

    # Негативные тесты
    async def test_get_alert_not_found(self):
        aid = uuid4()
        self.repo.get_by_id.return_value = None
        result = await self.service.get_alert(aid)
        self.assertIsNone(result)

    async def test_get_alerts_by_severity_empty(self):
        severity = 'critical'
        self.repo.get_by_severity.return_value = []
        result = await self.service.get_alerts_by_severity(severity)
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()