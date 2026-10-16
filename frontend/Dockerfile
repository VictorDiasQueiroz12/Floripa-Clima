# Imagem do Nginx com uma distribuição Linux pequena.
FROM nginx:stable-alpine

# Substitui a configuração padrão pela configuração do projeto.
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copia somente os arquivos usados pela página.
COPY frontend/index.html /usr/share/nginx/html/index.html
COPY frontend/style.css /usr/share/nginx/html/style.css
COPY frontend/script.js /usr/share/nginx/html/script.js

# Porta interna utilizada pelo Nginx.
EXPOSE 80

# Mantém o Nginx em primeiro plano.
# Assim, o processo principal do container continua funcionando.
CMD ["nginx", "-g", "daemon off;"]