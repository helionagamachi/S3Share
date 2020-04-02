from aws_cdk import core

from aws_cdk.aws_cloudfront import (
    CloudFrontWebDistribution, S3OriginConfig, SourceConfiguration, Behavior,
    OriginAccessIdentity, LambdaFunctionAssociation, LambdaEdgeEventType
)

from aws_cdk.aws_s3 import Bucket
from aws_cdk.aws_s3 import BlockPublicAccess

from aws_cdk.aws_lambda import Function, Code, Runtime, Version

from aws_cdk.aws_iam import ServicePrincipal, PolicyStatement

from os import environ
from pathlib import Path

class S3ShareStack(core.Stack):

    def init_lambda(self):
        # need to code replacement for the key, and dependecies setup...
        asset_path = Path(__file__).parent.joinpath("..", "lambda")
        lambda_code = Code.from_asset(
            str(asset_path.absolute()),
            exclude=[".env", "__main*", "*.dist-info", "bin"]
        )

        checker_lambda = Function(
            self,
            "checker",
            code=lambda_code,
            handler="main.handler",
            runtime=Runtime.PYTHON_3_8
        )

        checker_lambda.role.assume_role_policy.add_statements(
            PolicyStatement(
                actions=["sts:AssumeRole"],
                principals=[ServicePrincipal("edgelambda.amazonaws.com")]
            )
        )


        version = Version(self, "version", lambda_=checker_lambda)

        return version

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

        default_behavior = Behavior(
            is_default_behavior=True,
            lambda_function_associations=[
                LambdaFunctionAssociation(
                    lambda_function=self.init_lambda(),
                    event_type=LambdaEdgeEventType.VIEWER_REQUEST
                )
            ]
        )

        source_config = SourceConfiguration(
            s3_origin_source=S3OriginConfig(
                s3_bucket_source=bucket,
                origin_access_identity=identity
            ),
            behaviors=[default_behavior],
        )

        distribution = CloudFrontWebDistribution(
            self,
            "CloudFront",
            origin_configs=[
                source_config,
            ],
        )
