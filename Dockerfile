FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./
COPY photowebapp ./photowebapp
RUN mkdir -p /app/uploads && chmod 0777 /app/uploads

EXPOSE 3000

CMD ["gunicorn", "--bind", "0.0.0.0:3000", "app:app"]