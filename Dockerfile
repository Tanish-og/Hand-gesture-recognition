FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render assigns a dynamic $PORT. Expose a common port for local use, but bind to $PORT at runtime
EXPOSE 10000

CMD ["bash", "-lc", "streamlit run app.py --server.port=${PORT:-10000} --server.address=0.0.0.0"]

