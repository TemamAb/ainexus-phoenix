FROM node:18-alpine

WORKDIR /app

# 1. Install Dependencies
COPY package.json package-lock.json* ./
# using legacy-peer-deps to ignore version conflicts in your fragmented repo
RUN npm install --legacy-peer-deps

# 2. Copy Source Code
COPY . .

# 3. Build the Project
# This creates the standard .next folder
RUN npm run build

# 4. Expose and Start
ENV NODE_ENV production
ENV PORT 3000
EXPOSE 3000

# We explicitly call next start to avoid confusion with any legacy app.js
CMD ["npx", "next", "start"]
