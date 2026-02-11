# -------- BASE / DEPENDENCY STAGE --------
FROM node:20-alpine AS deps

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev


# -------- RUNTIME STAGE --------
FROM node:20-alpine

WORKDIR /app

# Copy only production dependencies
COPY --from=deps /app/node_modules ./node_modules

# Copy application code
COPY . .

EXPOSE 3000

CMD ["node", "index.js"]

