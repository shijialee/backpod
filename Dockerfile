FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-warn-script-location --user -r requirements.txt

ENV PYTHONUNBUFFERED="true" \
    PATH=$PATH:/root/.local

COPY . .

CMD ["python3", "-m", "backpod.cli", "--quiet"]