FROM node:16-alpine

WORKDIR /

RUN \
    echo "==> Install app..."                && \
    npm install -g --production json-server  && \
    \
    \
    echo "==> Remove unused temp..."         && \
    rm -rf /root/.npm                  \
           /usr/lib/node_modules/npm

# to be able to use "nano" with shell on "docker exec -it [CONTAINER ID] bash"
ENV TERM xterm

COPY animals.json /

EXPOSE 8080

WORKDIR /
CMD ["json-server", "--host", "0.0.0.0", "--port", "8080" , "--watch", "animals.json"]
