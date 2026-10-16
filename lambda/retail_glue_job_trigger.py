import json
import boto3
import urllib.parse

glue = boto3.client("glue", region_name="ap-south-1")

JOB_NAME = "calfus-retail-etl-spark"
EXPECTED_BUCKET = "calfus-retail-pipeline"
EXPECTED_PREFIX = "processed/"
EXPECTED_SUFFIX = ".csv"
DRY_RUN = False


def lambda_handler(event, context):
    started_runs = []

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(
            record["s3"]["object"]["key"]
        )

        # Ignore anything outside the intended input location.
        if bucket != EXPECTED_BUCKET:
            continue

        if not key.startswith(EXPECTED_PREFIX):
            continue

        if not key.endswith(EXPECTED_SUFFIX):
            continue

        if DRY_RUN:
            print(json.dumps({
                "message": "Dry run - Glue job not started",
                "job_run_id": "N/A",
                "job_name": JOB_NAME,
                "bucket": bucket,
                "key": key
            }))
            continue

        response = glue.start_job_run(
            JobName=JOB_NAME
        )

        job_run_id = response["JobRunId"]
        started_runs.append(job_run_id)

        print(json.dumps({
            "message": "Glue job started",
            "job_name": JOB_NAME,
            "job_run_id": job_run_id,
            "bucket": bucket,
            "key": key
        }))

    return {
        "statusCode": 200,
        "body": json.dumps({
            "started_runs": started_runs
        })
    }
