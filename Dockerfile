# 1. Use a stable Python version
FROM python:3.12-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory (Every command after this happens HERE)
WORKDIR /app

# 4. Install system dependencies
RUN apt-get update && apt-get install -y netcat-traditional

# 5. Copy requirements and install
# We copy to "." which means the current WORKDIR (/app)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your project code to the current WORKDIR
COPY . /app

# 7. Run the server
# Since manage.py is now in /app, this will work perfectly
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]