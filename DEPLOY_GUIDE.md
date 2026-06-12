# 华为云 CCE 部署指南

## 前置条件
1. 已完成任务1（应用容器化）和任务2（CCE集群搭建）
2. 已配置 kubectl 连接到 CCE 集群
3. 已创建 SWR 拉取密钥（swr-secret）

## 部署步骤

### 1. 创建 SWR 拉取密钥（如果还没有）
```bash
# 使用华为云提供的命令创建 swr-secret
# 请根据华为云控制台提示执行
```

### 2. 按顺序部署资源

```bash
# 进入 k8s 目录
cd k8s

# 1. 部署 ConfigMap（后端配置）
kubectl apply -f configmap.yaml

# 2. 部署 Nginx ConfigMap
kubectl apply -f nginx-configmap.yaml

# 3. 部署 Secret（Redis密码）
kubectl apply -f secret.yaml

# 4. 部署 PVC（Redis持久化）
kubectl apply -f pvc.yaml

# 5. 部署 Service
kubectl apply -f service.yaml

# 6. 部署 Deployment（Redis、Backend、Frontend）
kubectl apply -f deployment.yaml

# 7. 部署 HPA（弹性伸缩）
kubectl apply -f hpa.yaml
```

### 3. 验证部署

```bash
# 查看 Pod 状态
kubectl get pods -o wide

# 查看 Service 状态（获取 LoadBalancer 的 External IP）
kubectl get svc -o wide

# 查看 Deployment 状态
kubectl get deployments -o wide

# 查看 HPA 状态
kubectl get hpa -o wide

# 查看 PVC 状态
kubectl get pvc -o wide
```

### 4. 测试应用

```bash
# 等待 Service 获取到 External IP 后，通过以下方式测试：

# 测试后端 API（使用 backend-svc 的 External IP）
curl http://<BACKEND_EXTERNAL_IP>/api/ping

# 测试健康检查
curl http://<BACKEND_EXTERNAL_IP>/api/health

# 访问前端页面（使用 frontend-svc 的 External IP）
# 在浏览器中打开：http://<FRONTEND_EXTERNAL_IP>
```

## 配置说明

### 镜像信息
- Backend: `swr.cn-east-3.myhuaweicloud.com/zxy2023112454/backend:v1`
- Frontend: `swr.cn-east-3.myhuaweicloud.com/zxy2023112454/frontend:v1`
- Redis: `redis:7-alpine`

### Redis 密码
- 明文: `redis123`
- Base64: `cmVkaXMxMjM=`

### 资源限制
- Backend: 100m/128Mi (请求), 500m/512Mi (限制)
- Redis: 100m/128Mi (请求), 300m/256Mi (限制)
- Frontend: 50m/64Mi (请求), 200m/128Mi (限制)

### HPA 配置
- 最小副本: 1
- 最大副本: 4
- CPU 阈值: 60%

## 任务完成清单

- [x] 任务1：应用容器化
- [x] 任务2：CCE集群搭建
- [ ] 任务3：应用部署
- [ ] 任务4：持久化存储
- [ ] 任务5：ConfigMap Volume挂载
- [ ] 任务6：HPA弹性伸缩
