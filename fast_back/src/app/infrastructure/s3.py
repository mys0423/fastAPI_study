from botocore.config import Config
import aioboto3
import os
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")

session = aioboto3.Session()

s3_config = Config(
    signature_version="s3v4",
    s3={"addressing_style": "virtual"}
)

async def get_s3_client():
    async with session.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
        config=s3_config
    ) as client:
        yield client