FROM node:22-bookworm-slim AS frontend-builder

WORKDIR /workspace/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend ./
ARG VITE_BASE_PATH=/
ENV VITE_BASE_PATH=${VITE_BASE_PATH}
RUN npm run build

FROM nginx:1.27-alpine

COPY docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=frontend-builder /workspace/frontend/dist /usr/share/nginx/html
