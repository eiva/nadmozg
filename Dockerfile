FROM python:latest
COPY requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt
COPY app.py /src
CMD python3 /src/app.py
