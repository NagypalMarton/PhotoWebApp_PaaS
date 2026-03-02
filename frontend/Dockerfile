FROM nginxinc/nginx-unprivileged:1.27.5-alpine3.21

COPY index.html /usr/share/nginx/html/index.html
COPY nginx-cfg/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080