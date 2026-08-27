# Turtle Soup Game

一个可供单人游玩的海龟汤游戏。

当前项目文档：

- [产品需求](docs/PRODUCT_REQUIREMENTS.md)
- [模块实施与 SDD-TDD 验收计划](docs/MODULE_IMPLEMENTATION_AND_SDD_TDD_ACCEPTANCE_PLAN.md)
- [M1 架构与项目文件结构](docs/M1_ARCHITECTURE.md)
- [M2 领域核心规格](docs/M2_DOMAIN.md)
- [M3 Repository Port 与 SQLite 持久化](docs/M3_PERSISTENCE.md)

## 开发

后端：

```powershell
conda run -n web python -m pip install -r backend/requirements-dev.txt
conda run -n web python -m pytest backend/tests
conda run -n web python -m ruff check backend
conda run -n web python -m pip check
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
