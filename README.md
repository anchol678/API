# &#x20;全栈 API 项目

## 这是什么？

一个**用户文章管理系统**，包含：

- **后端**：Python FastAPI 写的 API 服务
- **前端**：Vue3 写的网页界面
- **数据库**：SQLite（自动创建，无需安装）

你可以：注册账号 → 登录 → 写文章 → 改文章 → 删文章，所有操作都有 JWT 权限保护。

***

## 一分钟启动

```powershell
# 1. 进入后端目录
cd week1-fullstack\backend

# 2. 安装依赖（只需一次）
pip install -r requirements.txt

# 3. 启动后端（窗口不要关）
uvicorn main:app --host 127.0.0.1 --port 8001

# 4. 用浏览器打开前端页面
start ..\frontend\index.html
```

看到网页后，点右上角"注册"，输入用户名、邮箱、密码，注册成功就能用了。

***

## API 接口一览

启动后在浏览器打开 <http://127.0.0.1:8001/docs> 可以看到所有接口的交互式文档。

| 方法     | 地址                        | 说明             | 需要登录 |
| ------ | ------------------------- | -------------- | ---- |
| GET    | `/health`                 | 健康检查           | 否    |
| POST   | `/api/v1/users/register`  | 注册             | 否    |
| POST   | `/api/v1/users/login`     | 登录             | 否    |
| GET    | `/api/v1/users/me`        | 查看自己的信息        | 是    |
| GET    | `/api/v1/items`           | 文章列表           | 是    |
| POST   | `/api/v1/items`           | 创建文章           | 是    |
| GET    | `/api/v1/items/{id}`      | 查看一篇文章         | 是    |
| PUT    | `/api/v1/items/{id}`      | 修改文章           | 是    |
| DELETE | `/api/v1/items/{id}`      | 删除文章           | 是    |
| WS     | `/ws/{user_id}?token=xxx` | WebSocket 实时通知 | 是    |

***

## 项目文件说明

```
week1-fullstack/
├── README.md                ← 你在看的这个文件
│
├── backend/                 ← 后端（Python FastAPI）
│   ├── main.py              ← 程序入口，启动服务器
│   ├── config.py            ← 配置文件（数据库地址、密钥等）
│   ├── database.py          ← 数据库连接
│   ├── models.py            ← 数据库表结构（User用户表、Item文章表）
│   ├── schemas.py           ← 数据校验规则（注册时用户名至少3位，等）
│   ├── auth.py              ← 登录认证（JWT加密、密码哈希）
│   ├── websocket.py         ← WebSocket 实时推送管理
│   ├── routers/
│   │   ├── users.py         ← 用户相关接口（注册、登录）
│   │   └── items.py         ← 文章相关接口（增删改查）
│   └── requirements.txt     ← 依赖包列表
│
└── frontend/                ← 前端（Vue3 网页）
    ├── index.html           ← 网页结构
    ├── app.js               ← 页面逻辑（注册、登录、文章管理）
    └── style.css            ← 样式
```

### 后端核心流程

```
用户请求 → FastAPI 路由 → JWT 认证检查 → 数据库操作 → 返回 JSON
```

#### 注册流程：

1. 用户在前端填写用户名、邮箱、密码
2. 前端发 POST 请求到 `/api/v1/users/register`
3. 后端检查用户名和邮箱是否已被占用
4. 密码用 `pbkdf2_sha256` 加密后存入数据库
5. 返回一个 JWT Token（相当于一张临时通行证）

#### 登录后发文章流程：

1. 每次请求时，前端自动在 HTTP Header 里带上 Token
2. 后端 `get_current_user` 函数验证 Token
3. 验证通过，取出当前用户信息
4. 文章自动绑定到当前用户，只能看到和操作自己的文章

***

## 用命令行测试 API

想跳过前端直接用命令测试？在 PowerShell 里执行：

```powershell
# 1. 注册
$body = '{"username":"test","email":"t@test.com","password":"123456"}'
$r = Invoke-RestMethod -Uri http://127.0.0.1:8001/api/v1/users/register -Method Post -Body $body -ContentType 'application/json'
$token = $r.access_token
Write-Host "注册成功，用户: $($r.user.username)"

# 2. 创建文章
$h = @{Authorization="Bearer $token"}
$r = Invoke-RestMethod -Uri http://127.0.0.1:8001/api/v1/items -Method Post -Body '{"title":"我的博客","content":"正文内容"}' -ContentType 'application/json' -Headers $h
Write-Host "文章ID: $($r.id)"

# 3. 查看文章列表
$r = Invoke-RestMethod -Uri http://127.0.0.1:8001/api/v1/items -Headers $h
Write-Host "共 $($r.total) 篇文章"

# 4. 修改文章（把文章ID换成你的）
$r = Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/v1/items/1" -Method Put -Body '{"content":"修改后的内容"}' -ContentType 'application/json' -Headers $h

# 5. 删除文章
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/v1/items/1" -Method Delete -Headers $h

# 6. 查看自己的用户信息
$r = Invoke-RestMethod -Uri http://127.0.0.1:8001/api/v1/users/me -Headers $h
Write-Host "用户名: $($r.username), 邮箱: $($r.email)"
```

***

