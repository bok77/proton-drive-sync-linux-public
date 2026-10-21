import unittest
from proton_sync_engine.v1_api_load_assessment import estimate

class ApiLoadAssessmentTests(unittest.TestCase):
    def test_half_hour_schedule_and_nested_folders(self):
        self.assertEqual(estimate(interval_minutes=30,cloud_directories=1).baseline_list_calls_per_day,48)
        self.assertEqual(estimate(interval_minutes=30,cloud_directories=12).baseline_list_calls_per_day,576)
        self.assertFalse(estimate(interval_minutes=30,cloud_directories=12).provider_request_count_known)
    def test_bad_inputs_fail_closed(self):
        for m,f in [(0,1),(7,1),(30,0),(30,-1),(True,2),(30,True)]:
            with self.subTest(m=m,f=f),self.assertRaises(ValueError):
                estimate(interval_minutes=m,cloud_directories=f)
