FROM python:3.12-slim
RUN mkdir -p /app/www /data
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app.py .
COPY index.html /app/www/
COPY quiz.html /app/www/
COPY index.css /app/www/
COPY hintergrundmusik.opus /app/www/
COPY f32209c0-e396-4e9b-8774-4197303c54ff.png /app/www/
COPY f32209c0-e396-4e9b-8774-4197303c54ff.ico /app/www/
EXPOSE 5000
VOLUME ["/data"]
CMD ["python", "app.py"]
