FROM python:latest
COPY requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt
COPY app.py /src
COPY __init__.py /src
COPY cogs /src/cogs
COPY utils /src/utils
CMD python3 /src/app.py
