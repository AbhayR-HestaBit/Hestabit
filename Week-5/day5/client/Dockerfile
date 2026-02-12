# -------- BUILD STAGE --------
FROM node:20-alpine AS builder

WORKDIR /app


COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build


# -------- RUNTIME STAGE --------
FROM nginx:alpine

# Remove default nginx config if needed
# RUN rm /etc/nginx/conf.d/default.conf

# Copy build output only (no node, no npm)
COPY --from=builder /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

