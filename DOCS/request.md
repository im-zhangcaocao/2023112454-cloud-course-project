# 云计算课程设计项目总结（供 AI 辅助参考）

## 一、课程设计目标
基于华为云 CCE（云容器引擎）完成：
1. 容器化 Web 应用（Flask + Redis + Nginx）的部署与运维（第一部分，50 分）。
2. 在 K8s 上运行 Spark 大数据分析作业（方向 A，40 分）。
3. 附加题（监控 / CI/CD / 前沿专题，最高 +15 分）。

## 二、任务书核心要求（已简化）

### 第一部分（50 分）
| 任务 | 要求 | 分值 |
|------|------|------|
| 任务1：应用容器化 | 构建后端+前端镜像，推送到 SWR，本地 docker-compose 验证 | 10 |
| 任务2：CCE 集群搭建 | 创建 K8s 集群（≥1.27），2 个 Worker 节点，kubectl 可访问 | 8 |
| 任务3：应用部署 | 部署 Deployment、Service（LoadBalancer）、ConfigMap、Secret | 12 |
| 任务4：持久化存储 | Redis PVC，Pod 重建数据不丢失 | 10 |
| 任务5：ConfigMap Volume 挂载 | Nginx 配置通过 Volume 挂载，动态更新 | 5 |
| 任务6：HPA 弹性伸缩 | CPU 超过 60% 扩容，压测验证 | 5 |

### 第二部分（40 分，方向 A：Spark 大数据分析）
| 子任务 | 要求 | 分值 |
|--------|------|------|
| A-0 环境部署 | 安装 Spark Operator，提交 wordcount 示例 | 10 |
| A-1 数据清洗 | 选择数据集（豆瓣电影/共享单车），缺失值处理 | 10 |
| A-2 Spark SQL 分析 | 至少 4 个查询（GROUP BY, TOP-N, 时间维度, JOIN/窗口函数） | 15 |
| A-3 性能对比与 Amdahl 分析 | Pandas vs PySpark (1/2 executor)，绘图与分析 | 5 |

## 三、用户已完成的任务

### ✅ 任务1：应用容器化（完成）
- 项目结构：`D:\project\cloud_project\`，包含 `backend/`、`frontend/`、`docker-compose.yml`。
- 修改了 `requirements.txt`（添加 `pandas`, `requests` 等）和 `frontend/static/index.html`（含学号姓名：**2023112454 张芯莹**）。
- 本地构建镜像成功：
  - `cloud_project-backend:latest`
  - `cloud_project-frontend:latest`
- 本地 `docker-compose up` 测试通过：
  - 后端 API：`http://localhost:5000/api/ping` 返回 `{"status":"ok"}`
  - 前端页面：`http://localhost:8080` 显示学号姓名（端口映射为 8080:80）
- 推送镜像到华为云 SWR（区域：**华东-上海一，cn-east-3**）：
  - 组织：`zxy2023112454`
  - 镜像：`backend:v1`、`frontend:v1`
  - 推送命令成功，无报错。

### ✅ 任务2：CCE 集群搭建（完成）
- 集群名称：`course-cluster`（以实际为准）
- 区域：`华东-上海一`
- K8s 版本：`v1.35.3`（≥1.27）
- Worker 节点：2 个，规格 `s6.large.2`（2vCPU/4GiB），操作系统 `Huawei Cloud EulerOS 2.0`
- 通过 CloudShell 连接集群，`kubectl get nodes -o wide` 输出：