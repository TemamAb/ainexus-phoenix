FROM node:18-alpine
WORKDIR /app
# Copy package.json (from the Grafana engine we just moved)
COPY package.json ./
# Clean install
RUN npm install
# Copy everything (now at root)
COPY . .
# Build Next.js
RUN npm run build
# Runtime
ENV NODE_ENV=production
ENV HOSTNAME="0.0.0.0"
EXPOSE 10000
CMD ["npm", "start"]
