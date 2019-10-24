FROM python:3.7

# Run before copying requirements for cache efficiency
RUN pip install --upgrade pip \
    && apt-get -y update

# Run before installing packages for cache efficiency
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt 
RUN apt-get install -y osm2pgsql
RUN apt-get install -y gdal-bin && apt-get install -y python3-gdal

#ENTRYPOINT ["python"]

#RUN mkdir -p /wmca/src /wmca/sql /wmca/data 

ARG pgpass

# PG Pass
RUN echo ${pgpass} > ~/.pgpass \
    && chmod 0600 ~/.pgpass

#RUN echo ${pgpass}

# Set the working directory
WORKDIR /wmca/src
ENTRYPOINT ["python"]

# works
#ENTRYPOINT ["python","run_etl_test.py"]

#RUN run_etl_test.py
#RUN run_pipeline_test.py

#RUN pwd

#RUN ls

#ENTRYPOINT ["/bin/ping"]
#CMD ["localhost"]

#ENTRYPOINT ["python"]
#ENTRYPOINT ["python", "run_etl_test.py"]
#CMD ["run_etl_test.py"]

#ADD ../../src/run_etl.py wmca/src/run_etl.py
#ADD ../src/run_pipeline.py /wmca/src/run_pipeline.py


# This runs these py files when the container launches...

#CMD ["python", "run_etl.py"]
#CMD ["python", "run_pipeline.py"]
