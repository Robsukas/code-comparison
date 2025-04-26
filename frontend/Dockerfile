FROM node:22.2-bullseye AS build
WORKDIR /web

COPY package*.json ./

ARG NPM_USER
ARG NPM_PASS

RUN printf '%s\n' \
    "//npm.taltech.ee/:username=${NPM_USER}" \
    "//npm.taltech.ee/:_password=$(echo -n ${NPM_PASS} | base64)" \
    "//npm.taltech.ee/:always-auth=true" > .npmrc

RUN npm ci

COPY . .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /web/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
