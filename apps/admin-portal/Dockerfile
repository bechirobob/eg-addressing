FROM node:20-alpine

WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1

COPY apps/admin-portal/package.json ./package.json
RUN npm install

COPY apps/admin-portal/ ./
RUN npm run build

EXPOSE 3100

CMD ["npm", "run", "start", "--", "--hostname", "0.0.0.0", "--port", "3100"]
