from aws_cdk import core
from aws_cdk.aws_cloudfront import CloudFrontWebDistribution
from aws_cdk.aws_cloudfront import S3OriginConfig
from aws_cdk.aws_cloudfront import SourceConfiguration
from aws_cdk.aws_cloudfront import Behavior
from aws_cdk.aws_cloudfront import OriginAccessIdentity
from aws_cdk.aws_s3 import Bucket
from aws_cdk.aws_s3 import BlockPublicAccess

from os import environ

class S3ShareStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # configure S3 origin...

        bucket = Bucket(
            self,
            "bucket",
            block_public_access=BlockPublicAccess.BLOCK_ALL,
            bucket_name=environ.get("BUCKET_NAME", None)
        )

        identity = OriginAccessIdentity(
            self,
            "cloudFrontIAMUser",
            comment="cloud front identity"
        )

        bucket.grant_read(identity)

        source_config = SourceConfiguration(
            s3_origin_source=S3OriginConfig(
                s3_bucket_source=bucket,
                origin_access_identity=identity
            ),
            behaviors=[Behavior(is_default_behavior=True)],
        )

        distribution = CloudFrontWebDistribution(
            self,
            "CloudFront",
            origin_configs=[
                source_config,
            ],
        )
