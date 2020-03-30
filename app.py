#!/usr/bin/env python3

from aws_cdk import core
from aws_cdk.aws_s3 import Bucket
from s3_share.s3_share_stack import S3ShareStack


app = core.App()

S3ShareStack(app, "s3-share")

app.synth()
