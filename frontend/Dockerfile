FROM node:18-slim

# Install build tools for native dependencies
RUN apt-get update && apt-get install -y \
  python3 \
  make \
  g++ \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependencies first
COPY package*.json ./

# Install all dependencies (including devDependencies)
RUN npm install --include=dev

# Copy the rest of the app
COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]
