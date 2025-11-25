FROM node:18-alpine AS base
WORKDIR /usr/src/app

# Install production dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy app source
COPY . .

# Create non-root user
RUN addgroup -S app && adduser -S app -G app
USER app

# Expose port (Render injects PORT at runtime)
EXPOSE 3000

CMD ["node", "app.js"]