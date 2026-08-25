# M1 架构与项目文件结构规格

## 1. 阶段目标

M1 只负责冻结项目的技术栈、架构边界、物理目录、依赖管理、基础启动契约和 ignore 规则，为后续业务模块提供稳定基线。

M1 不实现题库、游戏状态、模型判定、持久化业务、正式页面或其他产品功能。

## 2. 技术栈

### 前端

- React 19 与 TypeScript 6。
- Vite 负责开发服务器与生产构建。
- pnpm 负责依赖解析和锁定。
- Vitest 负责前端单元测试。
- ESLint 负责静态检查。

### 后端

- 后端固定在已有 Conda `web` 环境中运行；M1 基线为 Python 3.11.15。
- FastAPI 提供异步 HTTP API。
- Uvicorn 提供 ASGI 开发运行时。
- Agently 提供模型请求、Prompt 和结构化输出能力。
- pip 根据后端 requirements 文件安装精确固定的直接依赖版本；不得另建项目 `.venv`。
- pytest 负责后端测试，Ruff 负责静态检查。

### 数据

- MVP 的持久化方案为 SQLite。
- M1 不创建数据库、数据表或 Repository；只有实际持久化模块开始时才创建相应所有者。
- 本地数据库和运行时数据放入被 Git 忽略的 `var/`，不得提交。

## 3. 系统边界

```text
Browser
  -> frontend: React SPA
  -> backend transport: FastAPI
  -> application use cases
  -> domain rules and ports
  -> infrastructure adapters
       -> SQLite
       -> Agently ModelRequest
       -> configured model provider
```

依赖方向必须朝向业务核心：

- `frontend` 只通过公开 HTTP 契约访问后端，不读取题底或服务端文件。
- FastAPI 只负责入站校验、调用应用用例和投影公开响应，不拥有游戏规则。
- application 负责用例编排和事务边界，不依赖 FastAPI。
- domain 负责状态、领域不变量和 Port，不依赖 FastAPI、Agently、SQLite 或前端类型。
- infrastructure 实现 domain/application 定义的 Port。
- Agently 只能出现在后端模型基础设施所有者中，不得进入 domain、普通 DTO、文件处理或 Repository。

## 4. 模型请求所有权

本项目当前只有两个同类但契约独立的模型语义操作：问题三分类和最终猜测判断。它们属于请求侧能力，使用 Agently 原生 ModelRequest 和结构化输出。

M1 不引入 TriggerFlow。当前产品没有需要框架可见的分支、并发、暂停恢复、审批或重启安全工作流。后续只有在 SDD 明确出现这些生命周期要求时才允许评估 TriggerFlow。

模型负责语义判断；宿主程序负责状态、枚举与 DTO 校验、权限、持久化和副作用。模型返回值在通过宿主校验前不可信。

M1 在 Conda `web` 环境中确认 Agently 4.1.4.6，安装位置为该环境的 `Lib/site-packages`。后续模型模块仍必须核对该环境中的真实源码、公开 API 和代表性最小调用，不得仅凭本规格或历史记忆实施。

M1 已直接核对该安装版本的公开接口与源码所有者：

- `AgentlyMain` 定义在 `agently/base.py`，并提供 `load_settings(..., auto_load_env=...)`。
- `ModelRequest` 定义在 `agently/core/model/ModelRequest.py`。
- `ModelRequest` 提供 `input`、`info`、`instruct`、`output` 和 `async_get_data`。
- 后续实现仍需针对将要使用的参数和行为再次读取真实源码并编写代表性测试。

M1 的直接依赖版本基线为：

- Agently 4.1.4.6。
- FastAPI 0.141.1。
- Uvicorn 0.52.4。
- React 与 React DOM 19.2.8。
- TypeScript 6.0.3。
- Vite 8.2.2。

## 5. M1 物理文件结构

```text
Turtle-Soup-Game/
├── .dockerignore
├── .env.example
├── .gitignore
├── AGENTS.md
├── README.md
├── docs/
│   ├── M1_ARCHITECTURE.md
│   └── PRODUCT_REQUIREMENTS.md
├── backend/
│   ├── pyproject.toml
│   ├── requirements-dev.txt
│   ├── requirements.txt
│   ├── src/
│   │   └── turtle_soup/
│   │       ├── __init__.py
│   │       └── main.py
│   └── tests/
│       └── test_health.py
└── frontend/
    ├── eslint.config.js
    ├── index.html
    ├── package.json
    ├── pnpm-lock.yaml
    ├── tsconfig.app.json
    ├── tsconfig.json
    ├── tsconfig.node.json
    ├── vite.config.ts
    └── src/
        ├── App.test.tsx
        ├── App.tsx
        ├── main.tsx
        ├── styles.css
        └── vite-env.d.ts
```

目录只能在出现真实所有者和当前消费者时创建。M1 不预建空的 `domain/`、`application/`、`infrastructure/`、`repositories/`、`services/` 或 `workflows/`。

后续模块可以按照冻结 SDD 增加这些目录，但不能改变本规格的依赖方向。

## 6. 基础公开契约

后端只提供 M1 健康检查：

```http
GET /health
```

成功响应固定为：

```json
{
  "status": "ok"
}
```

该端点不检查外部模型或数据库，不伪造它们的健康状态；它只证明 ASGI 应用能够处理请求。

前端 M1 只渲染静态应用壳，包含“海龟汤”和“单人推理游戏”。不得在 M1 中加入模拟题目、假模型回答或业务状态。

## 7. 配置与密钥

`.env.example` 只声明变量名，不包含真实值：

- `MODEL_API_KEY`
- `MODEL_BASE_URL`
- `MODEL_NAME`

真实 `.env`、供应商密钥和环境专属地址不得提交。后续模型模块必须在集成层将这些变量映射到 Agently 设置，并在启动或调用边界 fail-fast 校验。

## 8. Ignore 契约

`.gitignore` 必须排除：

- 本地环境变量和密钥文件，但保留 `.env.example`。
- Python 虚拟环境、缓存、覆盖率和构建产物。
- Node 依赖、Vite 缓存、前端构建与覆盖率产物。
- pnpm 本地内容寻址缓存目录。
- Agently 在 `.agently/` 下生成的 TaskWorkspace、执行暂存文件和其他本地运行时数据。
- SQLite、运行时数据和日志。
- 常见 IDE 与操作系统临时文件。

`.dockerignore` 必须阻止 Git 元数据、密钥、本地依赖、缓存、测试覆盖率、构建输出、`.agently` 运行时目录和其他运行时数据进入未来容器构建上下文。

需要版本控制的 Prompt、配置、题库或最终产物必须进入其 SDD 指定的项目目录，不得直接从 `.agently/` 提交。

后端 requirements 文件精确固定直接依赖版本，`frontend/pnpm-lock.yaml` 锁定前端依赖图；这些文件必须提交，不得加入 ignore。M1 不宣称共享 Conda 环境中的所有传递依赖均已独立锁定。

## 9. 开发命令

后端：

```powershell
conda run -n web python -m pip install -r backend/requirements-dev.txt
conda run -n web python -m pytest backend/tests
conda run -n web python -m ruff check backend
conda run -n web python -m uvicorn turtle_soup.main:app --app-dir backend/src --reload
```

前端：

```powershell
pnpm --dir frontend install
pnpm --dir frontend test
pnpm --dir frontend lint
pnpm --dir frontend build
pnpm --dir frontend dev
```

## 10. TDD 与质量门禁

M1 的语义契约测试包括：

- 后端 `/health` 的状态码与完整响应体。
- 前端应用壳的两个固定产品标识。

冻结前必须检查：

- `git status`
- 所有未跟踪文件的实际内容
- `git diff`
- `git diff --check`
- 后端 pytest 与 Ruff
- 前端 Vitest、ESLint 与生产构建
- 文档和配置中的密钥模式

M1 没有真实模型行为，因此不以 fake/stub 声称模型集成成功，也不运行模型语义评测。

## 11. M1 冻结范围

M1 冻结以下内容：

- React/TypeScript/Vite 前端与 Python/FastAPI 后端的双目录单仓库结构。
- Conda `web` 后端运行环境、pip requirements 与 pnpm 锁文件位置。
- 架构依赖方向与 Agently 所有者边界。
- `/health` 响应契约。
- 根目录环境变量和 ignore 策略。
- M1 最小应用壳与质量门禁。

后续模块不得删除、弱化或改写 M1 契约测试。确需改变上述冻结项时，必须停止并取得用户批准。
