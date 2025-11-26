FROM node:18-alpine

WORKDIR /app

# 1. Install Dependencies
COPY package.json package-lock.json* ./
# Force install to ensure node_modules are fresh
RUN npm install --legacy-peer-deps

# 2. Copy Source
COPY . .

# 3. Build (This generates the .next folder)
RUN npm run build

# 4. Runtime Configuration
ENV NODE_ENV=production
# Hostname 0.0.0.0 is MANDATORY for Render/Docker networking
ENV HOSTNAME="0.0.0.0"

# We do not hardcode PORT. We let Render inject it.
EXPOSE 10000

# 5. Start Command
# calls 'next start' from package.json
CMD ["npm", "start"]
