import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="s3_share",
    version="0.0.1",

    description="S3 file share",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Hélio Nagamachi",

    package_dir={"": "s3_share"},
    packages=setuptools.find_packages(where="s3_share"),

    install_requires=[
        "aws-cdk.core",
        "aws-cdk.aws_s3",
        "aws-cdk.aws_cloudfront"
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
