FROM nginxinc/nginx-unprivileged:1.23-alpine

USER root

RUN rm -v /etc/nginx/nginx.conf
RUN rm -v /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/
COPY frontend.conf.template /etc/nginx/templates/
COPY /html /usr/share/nginx/html

# Enables and arbitrary user to write to nginx folder, Needed for vk8s deployments
RUN chmod -R 777 /etc/nginx

ENV SITE_ENV null
ENV SITE_ENV_MESSAGE null

EXPOSE 8080  
CMD ["nginx", "-g", "daemon off;"]