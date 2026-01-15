# https://docs.docker.com/engine/reference/builder/

FROM python:3.12
COPY dist/*.whl .
RUN pip install *.whl
# Run the FinRobot main module
CMD ["python", "-m", "finrobot"]
