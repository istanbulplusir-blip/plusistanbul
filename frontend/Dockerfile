# Multi-stage build for Next.js frontend
FROM node:20.18.0-alpine AS builder

# Set working directory
WORKDIR /app

# Set build-time environment variables for Next.js
ARG NEXT_PUBLIC_API_URL=https://peykantravelistanbul.com/api/v1
ARG NEXT_PUBLIC_SITE_URL=https://peykantravelistanbul.com
ARG NEXT_PUBLIC_GOOGLE_CLIENT_ID=728579658716-t2emm074v3kj3scv8mtrqhl55e7rnhdq.apps.googleusercontent.com
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_SITE_URL=$NEXT_PUBLIC_SITE_URL
ENV NEXT_PUBLIC_GOOGLE_CLIENT_ID=$NEXT_PUBLIC_GOOGLE_CLIENT_ID

# Copy package files
COPY package*.json ./

# Install dependencies with clean cache
RUN npm ci --only=production --no-audit --no-fund

# Copy source code
COPY . .

# Build the application with optimization
RUN npm run build

# Production stage
FROM node:20.18.0-alpine AS production

# Set environment variables
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Set working directory
WORKDIR /app

# Copy built application from builder
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/package*.json ./
COPY --from=builder --chown=nextjs:nodejs /app/next.config.js ./
# Copy i18n directory instead of i18n.ts
COPY --from=builder --chown=nextjs:nodejs /app/i18n ./i18n

# Install only production dependencies
RUN npm ci --only=production --no-audit --no-fund && npm cache clean --force

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1

# Start the application
CMD ["npm", "start"] 