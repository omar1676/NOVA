# Imagen del servidor Node. Se construye desde la raiz del repositorio
# (compose.yaml: context .) porque el servidor tambien entrega las paginas
# de 01_Interfaces (panel, tienda y portal).
FROM node:24-slim

WORKDIR /app

# Primero las dependencias: si no cambia package-lock.json, Docker reutiliza esta capa
COPY servidor-admin/package.json servidor-admin/package-lock.json servidor-admin/
RUN cd servidor-admin && npm ci --omit=dev

COPY servidor-admin servidor-admin
COPY 01_Interfaces/admin 01_Interfaces/admin
COPY 01_Interfaces/cliente 01_Interfaces/cliente
COPY 01_Interfaces/trabajador 01_Interfaces/trabajador

WORKDIR /app/servidor-admin
USER node
EXPOSE 3000
# Sin --env-file: la configuracion llega por las variables de compose.yaml
CMD ["node", "servidor.js"]
