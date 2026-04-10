FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py app.py
COPY models.py models.py
COPY analyzer.py analyzer.py

EXPOSE 7860

CMD ["python", "app.py"]
