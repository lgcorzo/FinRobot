import json
from typing import Any
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from finrobot.infrastructure.messaging.kafka_app import FastAPIKafkaService, PredictionRequest, PredictionResponse


@pytest.fixture
def mock_kafka_config() -> dict[str, str]:
    return {
        "bootstrap.servers": "localhost:9092",
        "group.id": "test-group",
        "auto.offset.reset": "earliest",
    }


def test_prediction_request_validation() -> None:
    request = PredictionRequest(input_data={"input": ["test text"]})
    validated = request.validate_model()
    assert isinstance(validated, pd.DataFrame)
    assert "input" in validated.columns


def test_fastapi_kafka_service_init(mock_kafka_config: dict[str, str]) -> None:
    mock_callback = MagicMock()
    service = FastAPIKafkaService(
        prediction_callback=mock_callback,
        kafka_config=mock_kafka_config,
        input_topic="input-topic",
        output_topic="output-topic",
    )
    assert service.input_topic == "input-topic"
    assert service.output_topic == "output-topic"
    assert service.prediction_callback == mock_callback


@patch("finrobot.infrastructure.messaging.kafka_app.Producer")
@patch("finrobot.infrastructure.messaging.kafka_app.Consumer")
def test_fastapi_kafka_service_start(
    mock_consumer_cls: Any, mock_producer_cls: Any, mock_kafka_config: dict[str, str]
) -> None:
    mock_callback = MagicMock()
    service = FastAPIKafkaService(
        prediction_callback=mock_callback,
        kafka_config=mock_kafka_config,
        input_topic="input-topic",
        output_topic="output-topic",
    )

    with patch.object(service, "_run_server") as mock_run_server:
        service.start()
        mock_producer_cls.assert_called_once()
        mock_consumer_cls.assert_called_once()
        mock_run_server.assert_called_once()


@patch("finrobot.infrastructure.messaging.kafka_app.Producer")
@patch("finrobot.infrastructure.messaging.kafka_app.Consumer")
def test_process_message(mock_consumer_cls: Any, mock_producer_cls: Any, mock_kafka_config: dict[str, str]) -> None:
    mock_callback = MagicMock(return_value=PredictionResponse(result={"inference": [1.0]}))
    service = FastAPIKafkaService(
        prediction_callback=mock_callback,
        kafka_config=mock_kafka_config,
        input_topic="input-topic",
        output_topic="output-topic",
    )
    service.producer = mock_producer_cls.return_value
    service.consumer = mock_consumer_cls.return_value

    # Mock Kafka message
    mock_msg = MagicMock()
    mock_msg.value.return_value = json.dumps({"input_data": {"input": ["test"]}}).encode("utf-8")
    mock_msg.error.return_value = None

    service._process_message(mock_msg)

    # Verify callback was called
    mock_callback.assert_called_once()

    # Verify producer sent message
    service.producer.produce.assert_called_once()
    args, kwargs = service.producer.produce.call_args
    assert args[0] == "output-topic"
    assert b"inference" in kwargs["value"]

    # Verify consumer committed
    service.consumer.commit.assert_called_once_with(mock_msg)
