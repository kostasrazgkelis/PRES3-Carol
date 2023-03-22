FROM node:alpine

RUN mkdir /src

WORKDIR /src

COPY ./infrastructures/front-c /src

RUN npm install
RUN npm install --save react-helmet

COPY ./src/services/front-c /src

CMD ["npm", "start"]