# What it is

The idea behind this project is to enable sharing objects with a Cloudfront
distribution without having to open up a public S3 bucket.

Although you could use pre-signed URLs to allow such sharing, if there is a need
of supporting HEAD requests, this solution will not work.

The urls generated should expire, and work with both GET and HEAD requests.
