# Turtle Soup Game

一个可供单人游玩的海龟汤游戏。

当前项目文档：

- [产品需求](docs/PRODUCT_REQUIREMENTS.md)
- [M1 架构与项目文件结构](docs/M1_ARCHITECTURE.md)

## 开发

后端：

```powershell
conda run -n web python -m pip install -r backend/requirements-dev.txt
conda run -n web python -m pytest backend/tests
conda run -n web python -m uvicorn turtle_soup.main:app --app-dir backend/src --reload
```

前端：

```powershell
pnpm --dir frontend install
pnpm --dir frontend test
pnpm --dir frontend dev
```
