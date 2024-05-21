# get nginx image
FROM nginxinc/nginx-unprivileged

# update image with custom config file
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/conf.d/local.conf /etc/nginx/conf.d
