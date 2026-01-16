# https://docs.docker.com/engine/reference/builder/

FROM python:3.12
COPY dist/*.whl .
RUN pip install *.whl
# Run the main function of the finrobot.infrastructure.messaging.kafka_app module
CMD ["python", "-m", "finrobot.infrastructure.messaging.kafka_app"]
