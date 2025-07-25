FROM python:3.13.5-bookworm
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./db_init.py /app/db_init.py
COPY ./dbdocker.env /app/dbdocker.env
COPY ./main.py /app/main.py

CMD ["python", "/app/db_init.py"]
CMD ["python", "/app/main.py"]

