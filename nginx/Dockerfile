FROM nginx:latest

# Удаляем стандартную конфигурацию
RUN rm /etc/nginx/conf.d/default.conf

# Копируем свою конфигурацию
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копируем собранный React (build/)
COPY ../microservices/pastebin_frontend/build /usr/share/nginx/html

# Открываем порт 80
EXPOSE 80
