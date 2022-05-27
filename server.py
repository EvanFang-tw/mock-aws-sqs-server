from flask import Flask, Request, Response, request
from fake_responses import (
    GET_QUEUE_URL_RESULT,
    INVALID_KEY_ERROR,
    NOT_FOUND_ERROR,
    SIGNATURE_NOT_MATCH,
)
from urllib import parse
from utils import hmac_sha256, sha256_hex

app = Flask(__name__)

# this is the mocked queue
queues = [{"name": "q1", "url": "http://sqs.aws.com/001/q1"}]

# hard code a key pair, just for testing
AWS_ACCESS_KEY_ID = "test_key"
AWS_SECRET_ACCESS_KEY = "test_secret"


@app.route("/", methods=["POST"])
def get_queue_url():
    """
    Simulate AWS SQS get-queue-url function.
    """
    # get access key id from header
    credential = request.headers["Authorization"].split("Credential=")[1]
    aws_access_key_id = credential.split("/")[0]

    # check key exists
    if aws_access_key_id != AWS_ACCESS_KEY_ID:
        return Response(INVALID_KEY_ERROR, mimetype="text/xml", status=403)

    # get signature from header
    signature = request.headers["Authorization"].split("Signature=")[1]

    # check signature
    if signature != _calculate_signature(request):
        return Response(SIGNATURE_NOT_MATCH, mimetype="text/xml", status=403)

    # try to get the queue by name
    queue_name = request.form["QueueName"]
    queue = [q for q in queues if q["name"] == queue_name]

    # queue not found
    if len(queue) == 0:
        return Response(NOT_FOUND_ERROR, mimetype="text/xml", status=400)

    return Response(GET_QUEUE_URL_RESULT, mimetype="text/xml")


def _calculate_signature(request: Request) -> str:
    """
    Get signature from http request.
    """
    method = request.method
    # example: POST

    path = request.path
    # example: /

    authorization = request.headers["Authorization"].split(" ")
    # example: AWS4-HMAC-SHA256 Credential=test_key/20220527/ap-northeast-1/sqs/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=a1cf407fc35ba5e0d9ba74781dc4998a7520071ba3c1e5bbaaf7443d1bf0f662

    algorithm = authorization[0].strip()
    # example: AWS4-HMAC-SHA256

    credential = authorization[1].strip(",").replace("Credential=", "").split("/")
    # example: test_key/20220527/ap-northeast-1/sqs/aws4_request

    signed_headers = authorization[2].strip(",").replace("SignedHeaders=", "")
    # example: content-type;host;x-amz-date

    signature = authorization[3].strip().replace("Signature=", "")
    # example: a1cf407fc35ba5e0d9ba74781dc4998a7520071ba3c1e5bbaaf7443d1bf0f662

    access_key_id = credential[0]
    # test_key

    date_stamp = credential[1]
    # 20220527

    region = credential[2]
    # ap-northeast-1

    service_type = credential[3]
    # sqs

    signature_version = credential[4]
    # aws4_request

    x_amz_date = request.headers["X-Amz-Date"]
    # exmaple: 20220527T062242Z

    # generate canonical query string
    sorted_params = sorted([param for param in request.args])
    canonical_query_string = "&".join(
        [
            parse.quote_plus(param) + "=" + parse.quote_plus(request.args[param])
            for param in sorted_params
        ]
    )
    # note that since there's no query parameters in this example,
    # canonical_query_string should by empty

    # generate canonical headers from signed headers
    canonical_headers = "\n".join(
        [
            h.strip() + ":" + request.headers[h].strip()
            for h in signed_headers.split(";")
        ]
    )
    canonical_headers += "\n"

    hashed_payload = sha256_hex(parse.urlencode(request.form))

    canonical_request = (
        method
        + "\n"
        + path
        + "\n"
        + canonical_query_string
        + "\n"
        + canonical_headers
        + "\n"
        + signed_headers
        + "\n"
        + hashed_payload
    )

    string_to_sign = (
        algorithm
        + "\n"
        + x_amz_date
        + "\n"
        + "/".join([date_stamp, region, service_type, signature_version])
        + "\n"
        + sha256_hex(canonical_request)
    )

    # make signing key
    key1 = hmac_sha256(("AWS4" + AWS_SECRET_ACCESS_KEY).encode("utf-8"), date_stamp)
    key2 = hmac_sha256(key1, region)
    key3 = hmac_sha256(key2, service_type)
    signing_key = hmac_sha256(key3, signature_version)

    # make signature
    signature = hmac_sha256(signing_key, string_to_sign).hex()

    return signature
