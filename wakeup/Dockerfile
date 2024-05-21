# start from official image
FROM python:3.10-slim

# update OS
RUN apt-get update && apt-get upgrade -y 

# create working directory
RUN mkdir -p /wakeup
WORKDIR /wakeup

# install dependencies
RUN pip install urllib3

# copy wakeup script
COPY wakeup/wakeup.py /wakeup

# change to non-root user 'app'
RUN mkdir -p /home/app
RUN addgroup --system app && adduser --system --group app
RUN chown -R app:app /wakeup
USER app

# run script on startup
CMD ["python", "/wakeup/wakeup.py"]

