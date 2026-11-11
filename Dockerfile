
FROM python:3.12-slim

WORKDIR /app

COPY usage_aggregation.py .
COPY sample_readings.csv .
COPY test_sample_readings.csv .

CMD ["python", "usage_aggregation.py", "sample_readings.csv"]
