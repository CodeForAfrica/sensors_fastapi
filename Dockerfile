
FROM python:3.13.0

ENV PYTHONUNBUFFERED 1

WORKDIR /src

COPY . /src/

RUN pip install --no-cache-dir --upgrade -q -r requirements.txt

COPY ./entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 80

CMD ["fastapi", "run", "main.py", "--port", "80"]
