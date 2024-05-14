# start from official image
FROM python:3.10-slim

# create working directory
RUN mkdir -p /services
WORKDIR /services

# install dependencies
COPY requirements.txt /services/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install opencv-python-headless

# copy project code
COPY . /services

# change to non-root user 'app'
RUN mkdir -p /home/app
RUN addgroup --system app && adduser --system --group app
RUN chown -R app:app /services
USER app

# start django server
ARG DJANGO_SECRET_KEY
ENV DJANGO_SECRET_KEY ${DJANGO_SECRET_KEY}
RUN cd backend && python manage.py 

# expose port 8000
EXPOSE 8000

# default commands to run when starting the container - start gunicorn server
CMD ["gunicorn", "--chdir", "backend", "--bind", ":8000", "django_wrapper.wsgi:application", "--timeout", "0"]
