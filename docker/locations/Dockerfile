FROM node:16-alpine

RUN \
    echo "==> Install app..."                && \
    npm install -g --production json-server  && \
    \
    \
    echo "==> Remove unused temp..."         && \
    rm -rf /root/.npm                  \
           /usr/lib/node_modules/npm

ENV TERM xterm
WORKDIR /
COPY locations.json /
EXPOSE 8080

CMD ["json-server", "--host", "0.0.0.0", "--port", "8080" , "--watch", "locations.json"]
