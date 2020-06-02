FROM python:3.8-slim-buster
WORKDIR /cashflow_project
ADD . /cashflow_project
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]