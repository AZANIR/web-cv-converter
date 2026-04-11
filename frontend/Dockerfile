FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG NUXT_PUBLIC_API_URL
ENV NUXT_PUBLIC_API_URL=${NUXT_PUBLIC_API_URL}
RUN npm run build

FROM node:20-alpine AS runner
RUN adduser --disabled-password --no-create-home appuser
WORKDIR /app
ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=3000
COPY --from=builder --chown=appuser:appuser /app/.output ./.output
USER appuser
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
