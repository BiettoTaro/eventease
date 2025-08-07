FROM node:18-slim

# Install build tools for native dependencies
RUN apt-get update && apt-get install -y \
  python3 \
  make \
  g++ \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependencies first (cache layer)
COPY package*.json ./

# Rebuild lightningcss manually after installing all packages
RUN npm install && npm rebuild lightningcss --build-from-source || true

# Copy the rest of the app
COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]
