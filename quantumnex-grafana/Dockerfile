FROM node:18-alpine
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build
ENV NODE_ENV=production
ENV HOSTNAME="0.0.0.0"
EXPOSE 10000
CMD ["npm", "start"]
