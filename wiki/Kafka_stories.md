# Kafka Integration Stories

## Overview

The Kafka Integration feature enables FinRobot to operate as a scalable, event-driven service. It allows the system to consume prediction requests from a Kafka topic, process them using MLflow-loaded models, and publish the results to an output topic. This is crucial for integrating FinRobot into larger, asynchronous microservices architectures.

## User Stories

### As a DevOps Engineer

I want to deploy FinRobot as a containerized service that listens to Kafka topics so that I can scale prediction processing independently of the web server.

### As a Data Scientist

I want my MLflow models to be automatically loaded and used for inference by the messaging app so that I don't have to write custom inference code for deployment.

### As a System Architect

I want to decouple the prediction service from the client application using Kafka so that the system handles high loads gracefully and provides fault tolerance.

## Functional Requirements

1. **Message Consumption**: The application must consume messages from a configurable Kafka input topic (`DEFAULT_INPUT_TOPIC`).
2. **Data Validation**: Incoming messages must be validated against a defined schema (`InputsSchema`) using `pandera`.
3. **Inference**: Validated data must be passed to a loaded MLflow model for prediction.
4. **Message Production**: Prediction results must be published to a configurable Kafka output topic (`DEFAULT_OUTPUT_TOPIC`).
5. **Data Serialization**: Input and output messages must be serialized as JSON.
6. **Error Handling**: Malformed messages or prediction errors should be logged and reported without crashing the service.

## Technical Details

### Architecture

- **FastAPI Application**: Acts as the host for the service.
- **Kafka Consumer/Producer**: Implemented using `confluent-kafka` running in background threads.
- **MLflow Adapter**: A `CustomLoader` adapts MLflow PyFunc models for the application's inference interface.

### Configuration

The application is configured via environment variables:

- `DEFAULT_KAFKA_SERVER`: Address of the Kafka broker.
- `DEFAULT_GROUP_ID`: Kafka consumer group ID.
- `DEFAULT_INPUT_TOPIC`: Topic to consume requests from.
- `DEFAULT_OUTPUT_TOPIC`: Topic to publish results to.
- `MLFLOW_MODEL_URI`: URI of the MLflow model to load.
- `LITELLM_API_KEY`: API key for model inference (if applicable).

### Schemas

- **InputsSchema**: Validates the input JSON structure.
- **OutputsSchema**: Defines the structure of the prediction response.
