from http import HTTPStatus
from unittest import TestCase
import os

class TestTablePreviewAPI(TestCase):

    def setUp(self) -> None:
        import pathlib
        current = pathlib.Path(__file__).parent.absolute()
        os.environ["PREVIEW_FILE_REPO"] = str(current)
        from preview_service import create_app
        self.app = create_app(config_module_class='preview_service.config.LocalConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tear_down(self) -> None:
        self.app_context.pop()

    def test_should_get_result_for_search(self) -> None:
        response = self.app.test_client().post('/preview_data', json={'database': 'customer_gauge', 'schema':'customer_gauge', 'tableName':'nps'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.json["data"]), 10)
