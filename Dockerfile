FROM nginx:1.27-alpine

COPY reports/nginx.conf /etc/nginx/conf.d/default.conf
COPY reports /usr/share/nginx/html
