# start from official image
FROM python:3.10-slim

# create working directory
RUN mkdir -p /wakeup
WORKDIR /wakeup

# install dependencies
RUN pip install urllib3

# copy wakeup script
COPY wakeup/wakeup.py /wakeup

# run script on startup
CMD ["python", "/wakeup/wakeup.py"]

