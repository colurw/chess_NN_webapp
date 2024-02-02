# start from official image
FROM python:3.10-slim

# arbitrary location choice: you can change the directory
RUN mkdir -p /services/djangoapp/src
WORKDIR /services/djangoapp/src

# install dependencies
COPY requirements.txt /services/djangoapp/src/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install opencv-python-headless

# copy project code
COPY . /services/djangoapp/src

# change to non-root user 'app'
RUN mkdir -p /home/app
RUN addgroup --system app && adduser --system --group app
RUN chown -R app:app /services/djangoapp/src
USER app

# start django server
RUN cd django_wrapper && python manage.py 

# expose port 8000
EXPOSE 8000

# define default command to run when starting the container
CMD ["gunicorn", "--chdir", "django_wrapper", "--bind", ":8000", "django_wrapper.wsgi:application", "--timeout", "0"]
