# Non-root nginx that listens on 8080, which is the port Cloud Run expects.
FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 8080
