FROM nginx:alpine

# Установка wget для health check
RUN apk add --no-cache wget

# Копирование статических файлов
COPY index.html /usr/share/nginx/html/
COPY styles/ /usr/share/nginx/html/styles/
COPY modules/ /usr/share/nginx/html/modules/
COPY core/ /usr/share/nginx/html/core/

# nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
