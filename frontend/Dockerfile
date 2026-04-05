FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# Browser must reach API on the host (e.g. localhost:8000 when ports are published)
ARG NUXT_PUBLIC_API_URL=http://localhost:8000
ENV NUXT_PUBLIC_API_URL=$NUXT_PUBLIC_API_URL
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=3000
COPY --from=builder /app/.output ./.output
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
