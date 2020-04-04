import tempfile
import shutil
import string
import random
import os

from os import environ
from pathlib import Path

from aws_cdk import core

from aws_cdk.aws_cloudfront import (
    CloudFrontWebDistribution, S3OriginConfig, SourceConfiguration, Behavior,
    OriginAccessIdentity, LambdaFunctionAssociation, LambdaEdgeEventType
)

from aws_cdk.aws_s3 import Bucket, BlockPublicAccess

from aws_cdk.aws_lambda import Function, Code, Runtime, Version

from aws_cdk.aws_iam import ServicePrincipal, PolicyStatement


class S3ShareStack(core.Stack):

    def init_lambda(self):

        tmp_dir = install_lambda_code_requirements()

        lambda_code = Code.from_asset(
            str(tmp_dir),
            exclude=[
                ".env",
                "__main*",
                "*.dist-info",
                "bin",
                "requirements.txt",
            ]
        )

        lambda_function = Function(
            self,
            "lambda",
            code=lambda_code,
            handler="main.handler",
            runtime=Runtime.PYTHON_3_8
        )

        lambda_function.role.assume_role_policy.add_statements(
            PolicyStatement(
                actions=["sts:AssumeRole"],
                principals=[ServicePrincipal("edgelambda.amazonaws.com")]
            )
        )

        version = Version(self, "version", lambda_=lambda_function)

        apply_removal_policy(lambda_function, version, lambda_function.role)

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

        apply_removal_policy(bucket)

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

def apply_removal_policy(*args):
    for el in args:
        resource = el.node.find_child('Resource')
        resource.apply_removal_policy(core.RemovalPolicy.RETAIN)

def install_lambda_code_requirements():
    tmp_dir = Path(tempfile.mkdtemp())
    origin_dir = Path(__file__).parent.parent.joinpath("lambda")

    shutil.copy(origin_dir.joinpath("requirements.txt"), tmp_dir)

    random_key = ''.join(
        random.choices(string.printable, k=30)
    ).replace('"', "").replace("\\", "")

    key = environ.get("JWT_KEY", random_key)

    with open(tmp_dir.joinpath("main.py"), "w") as dest, \
         open (origin_dir.joinpath("main.py")) as original:
            for l in original:
                dest.write(l.replace("#KEY_TO_BE_REPLACED#", key))

    # Installing the dependencies, maybe could be done better?
    os.chdir(tmp_dir)
    os.system("pip install -r requirements.txt --target .")

    return tmp_dir
