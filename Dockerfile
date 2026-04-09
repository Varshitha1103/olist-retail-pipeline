FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir pandas numpy matplotlib plotly sqlalchemy

COPY . .

ENV PYTHONPATH=/app

CMD ["python", "-c", "print('Olist Pipeline Ready!')"]