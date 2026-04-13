# 使用官方Node.js镜像作为构建环境
FROM node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

<<<<<<< Updated upstream
# 复制package.json和package-lock.json
COPY package.json .

# 安装依赖
RUN npm install
=======
# 复制 package.json 和 package-lock.json (修改点)
COPY package*.json ./

# 配置国内淘宝镜像源并使用 npm ci 安装依赖 (修改点)
RUN npm config set registry https://registry.npmmirror.com/ && npm ci
>>>>>>> Stashed changes

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 使用nginx作为生产环境服务器
FROM nginx:alpine

# 复制构建好的前端文件到nginx默认目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]