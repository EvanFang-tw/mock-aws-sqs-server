# Mock AWS SQS Server

A simple example of a mocked AWS SQS server.

Provide only one function: `get_queue_url`.

Start mock aws server:

```sh
export FLASK_APP=server
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=8866
```

Run client:

```sh
python ./client.py
```

Or use cli:

```sh
aws sqs get-queue-url --queue-name q1 --endpoint-url http://localhost:8866 --profile test-user
```
