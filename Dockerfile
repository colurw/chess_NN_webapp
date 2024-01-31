# start from official image
FROM python:3.10-slim

# arbitrary location choice: you can change the directory
RUN mkdir -p /opt/services/djangoapp/src
WORKDIR /opt/services/djangoapp/src

# install dependencies
COPY requirements.txt /opt/services/djangoapp/src/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install opencv-python-headless

# copy project code
COPY . /opt/services/djangoapp/src
# start django server
RUN cd django_wrapper && python manage.py 

# expose port 80
EXPOSE 80

# define default command to run when starting the container
CMD ["gunicorn", "--chdir", "django_wrapper", "--bind", ":80", "django_wrapper.wsgi:application", "--timeout", "0"]
