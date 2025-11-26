FROM node:18-alpine

WORKDIR /app

# 1. Copy ONLY package.json (Ignored lockfile to force fresh install)
COPY package.json ./

# 2. Install Dependencies (Clean Slate)
RUN npm install

# 3. Copy Source Code
COPY . .

# 4. Build the Dashboard
RUN npm run build

# 5. DEBUG: Verify build output exists (Will show in build logs)
RUN echo ">> VERIFYING BUILD OUTPUT:" && ls -la .next

# 6. Runtime Config
ENV NODE_ENV=production
ENV HOSTNAME="0.0.0.0"
EXPOSE 10000

# 7. Start
CMD ["npm", "start"]
