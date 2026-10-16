
import importlib.util
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "lambda"
    / "retail_glue_job_trigger.py"
)

spec = importlib.util.spec_from_file_location(
    "retail_glue_job_trigger", MODULE_PATH
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_ignores_wrong_bucket():
    event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "wrong-bucket"},
                "object": {"key": "processed/test.csv"}
            }
        }]
    }

    with patch.object(module.glue, "start_job_run") as start:
        result = module.lambda_handler(event, None)

    start.assert_not_called()
    assert result["statusCode"] == 200


def test_ignores_non_csv_file():
    event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "calfus-retail-pipeline"},
                "object": {"key": "processed/test.txt"}
            }
        }]
    }

    with patch.object(module.glue, "start_job_run") as start:
        result = module.lambda_handler(event, None)

    start.assert_not_called()
    assert result["statusCode"] == 200
