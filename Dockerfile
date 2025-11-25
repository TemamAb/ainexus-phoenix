FROM node:18-alpine AS base

# Create app directory
WORKDIR /usr/src/app

# Install only production dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy app source
COPY . .

# Expose port (Render sets PORT env at runtime)
EXPOSE 3000

# Start the API server
CMD ["node", "app.js"]
