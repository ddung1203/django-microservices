FROM python:3.10.6
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app

# RUN python manage.py makemigrations products

# CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
# EXPOSE 8000

CMD ["python", "consumer.py"]