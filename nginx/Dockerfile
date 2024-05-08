# get nginx image
FROM pagespeed/nginx-pagespeed:latest

# update image with custom config file
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/conf.d/local.conf /etc/nginx/conf.d
