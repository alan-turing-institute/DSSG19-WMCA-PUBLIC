FROM python:3.7

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /wmca/src

EXPOSE 8050
CMD ["python", "run_dashboard.py"]
#CMD ["python", "run_dashboard_test.py"]
