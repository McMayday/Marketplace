FROM python:3.8.6
RUN apt-get update -y && apt-get -y upgrade
ENV PYTHONUNBUFFERED 1
RUN mkdir /service
COPY requirements.txt /service/requirements.txt
WORKDIR /service
RUN pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["runserver", "0.0.0.0:8000"]
