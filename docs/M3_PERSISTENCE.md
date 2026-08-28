# M3 Repository Port 与 SQLite 持久化规格

## 1. 阶段目标

M3 只负责为已冻结的 M2 领域对象建立 Repository Port、SQLite Schema 和真实 SQLite 适配器，使题目与游戏会话能够被可靠地保存和重建。

M3 采用 SDD + TDD。实施前必须以本规格编写契约测试，再实现满足测试的最小持久化代码。

M3 的通用实施、TDD、独立复核、冻结和上传流程遵循 `docs/MODULE_IMPLEMENTATION_AND_SDD_TDD_ACCEPTANCE_PLAN.md`。本规格负责冻结 M3 专属的 Repository Port、SQLite Schema、事务、序列化和测试契约；两份文档发生冲突时必须停止并报告，不得自行选择、放宽契约或继续实施。

M3 不收集、录入或发布正式题目。正式题库仍从 M4 开始整理；M3 测试中的题目只允许作为确定性测试数据。

## 2. 模块所有权与依赖方向

M3 包含两个所有者层：

- `domain/ports.py`：定义业务核心所需的持久化 Port，不依赖 SQLite 或其他基础设施。
- `infrastructure/sqlite.py`：实现 Port，拥有 SQLite 连接、Schema 初始化、序列化和事务。

依赖方向固定为：

```text
infrastructure.sqlite
  -> domain.ports
  -> domain.models
```

约束：

- `domain/ports.py` 只能依赖 Python 标准库类型和 M2 领域类型。
- `domain` 不得依赖 `infrastructure`、`sqlite3`、FastAPI、Pydantic、Agently 或前端类型。
- SQLite 适配器可以依赖标准库 `sqlite3`、`json`、`datetime` 和 `pathlib`，不得新增第三方依赖。
- M3 不修改 M2 已冻结的领域模型、领域测试或 `domain/__init__.py` 公共导出。
- M3 不引入 ORM、迁移框架、通用 Unit of Work、缓存层或异步数据库封装。
- M3 不使用 Agently；模型请求与持久化是不同所有者。

## 3. 物理文件范围

M3 实施仅允许新增：

```text
backend/
├── src/
│   └── turtle_soup/
│       ├── domain/
│       │   └── ports.py
│       └── infrastructure/
│           ├── __init__.py
│           └── sqlite.py
└── tests/
    └── persistence/
        └── test_sqlite.py
```

职责：

- `domain/ports.py`：定义 `PuzzleRepository` 与 `GameSessionRepository` Protocol。
- `infrastructure/sqlite.py`：定义 Schema 初始化函数、SQLite Repository 实现和 Schema 错误。
- `infrastructure/__init__.py`：只导出本规格明确列出的 SQLite 公共类型与函数。
- `tests/persistence/test_sqlite.py`：使用临时目录中的真实 SQLite 文件验证 Port 语义、Schema、事务和重建结果。

不得创建空的 `application/`、`services/`、`workflows/`、`migrations/`、`seed/` 或题库目录。不得修改依赖文件，因为 M3 只使用 Python 标准库。

## 4. Repository Port 公共契约

`domain/ports.py` 使用 `typing.Protocol` 定义同步 Port。M3 不使用 `@runtime_checkable`，不通过运行时反射判断适配器类型。

### 4.1 `PuzzleRepository`

公共签名固定为：

```python
class PuzzleRepository(Protocol):
    def save(self, *, puzzle: Puzzle) -> None: ...

    def get(self, *, puzzle_id: str) -> Puzzle | None: ...

    def list_enabled(self) -> tuple[Puzzle, ...]: ...
```

语义：

- `save` 按 `Puzzle.id` 保存完整快照。
- 相同 ID 已存在时，`save` 原子覆盖该题目的完整持久化字段；不得产生第二条记录。
- `get` 返回完整 `Puzzle`；不存在时返回 `None`。
- `list_enabled` 只返回 `status=ENABLED` 的题目，按 `Puzzle.id` 升序排列并返回元组。
- Repository 不负责随机选择题目。题目选择属于后续应用用例。
- Repository 不删除题目，也不提供搜索、分页、标签或统计接口。

### 4.2 `GameSessionRepository`

公共签名固定为：

```python
class GameSessionRepository(Protocol):
    def save(self, *, session: GameSession) -> None: ...

    def get(self, *, session_id: str) -> GameSession | None: ...
```

语义：

- `save` 按 `GameSession.id` 保存整个聚合快照，包括问题与猜测记录。
- 相同 ID 已存在时，`save` 在一个事务内覆盖会话字段和两类记录的完整快照。
- 覆盖后不得残留新快照中不存在的旧记录。
- `get` 返回经 M2 公共构造器完整校验的 `GameSession`；不存在时返回 `None`。
- Repository 不执行领域状态转换，不生成 ID 或时间，也不判断模型语义。
- M3 不增加删除会话、列出会话、按用户查询或分页接口。

### 4.3 Port 输入规则

- `save` 只接受对应的 M2 领域对象实例；类型错误抛出 `ValueError`。
- `get` 的 ID 必须满足 `type(value) is str`，且 `strip()` 后非空；不得修剪、转换或替换输入。
- 输入契约错误抛出 `ValueError`。
- 所有 Port 方法都是同步方法。后续异步调用方必须在其所有者层决定线程调度，不得偷偷改变冻结方法的同步属性。

## 5. SQLite 公共入口

`infrastructure/sqlite.py` 的公共签名固定为：

```python
class SQLiteSchemaError(RuntimeError):
    ...


def initialize_sqlite_database(*, database_path: str | Path) -> None:
    ...


class SQLitePuzzleRepository:
    def __init__(self, *, database_path: str | Path) -> None: ...

    def save(self, *, puzzle: Puzzle) -> None: ...

    def get(self, *, puzzle_id: str) -> Puzzle | None: ...

    def list_enabled(self) -> tuple[Puzzle, ...]: ...


class SQLiteGameSessionRepository:
    def __init__(self, *, database_path: str | Path) -> None: ...

    def save(self, *, session: GameSession) -> None: ...

    def get(self, *, session_id: str) -> GameSession | None: ...
```

`infrastructure/__init__.py` 的公共导出固定为：

- `SQLiteSchemaError`
- `initialize_sqlite_database`
- `SQLitePuzzleRepository`
- `SQLiteGameSessionRepository`

### 5.1 数据库路径规则

- `database_path` 只接受 `str` 或 `pathlib.Path`。
- 字符串路径去除首尾空白后不得为空，但合法路径必须原样交给文件系统，不执行字符串修剪。
- M3 只支持文件型 SQLite 数据库，不支持 `:memory:`、SQLite URI 或共享内存模式。
- 父目录必须已经存在；初始化函数和 Repository 不得隐式创建目录。
- `initialize_sqlite_database` 必须在调用时立即验证路径类型、空白字符串、`:memory:`、以 `file:` 开头的 SQLite URI、父目录存在性以及目标不是目录；路径合法后才允许打开或创建数据库。
- 两个 SQLite Repository 构造器必须立即执行相同的无副作用路径验证，但不得打开连接、创建数据库、初始化或检查 Schema。第一次 Repository 操作才打开连接；数据库尚未初始化时必须保留真实失败，不得返回“未找到”。
- 真实运行数据库固定放在 `var/`。M3 实施阶段不创建或提交开发者数据库；经后续模块验收并由用户明确批准后，指定 SQLite 基线可以作为版本控制证据提交。
- 测试必须使用 pytest `tmp_path` 下的数据库，不得读写项目 `var/` 或开发者现有数据库。

### 5.2 初始化与版本规则

- Schema 版本使用 SQLite `PRAGMA user_version`，M3 版本固定为 `1`。
- 新数据库的 `user_version=0` 且不存在 M3 表时，初始化函数在单个事务内创建完整 Schema 并设置版本为 `1`。
- 对已正确初始化的版本 `1` 数据库重复调用必须安全且不改变业务数据。
- `user_version=0` 但已存在任一 M3 表表示不完整或来源不明的 Schema，必须抛出 `SQLiteSchemaError`，不得猜测或修补。
- 版本 `1` 重复初始化时，必须复核四张 M3 表的精确列集合、每列声明类型、`NOT NULL` 标志、主键序号，以及显式索引 `idx_puzzles_status_id`。任一表或列缺失、M3 表存在额外列、列属性不匹配或规定索引缺失时，抛出 `SQLiteSchemaError`，不得自动新增、删除、重建或修复。
- 数据库可以包含不属于 M3 的其他表；重复初始化不得修改、删除或拒绝这些表。
- 版本 `1` 重复初始化不承担对任意外部数据库进行完整取证审计。外键、唯一约束和 `CHECK` 约束的真实性由初始化函数新建数据库上的真实行为测试证明，不通过脆弱的完整 DDL 文本匹配锁定 SQL 排列。
- 完成新数据库版本 `0` 和已初始化版本 `1` 的分支判断后，其他任何 `user_version` 均抛出 `SQLiteSchemaError`，不得自动降级、升级或清空数据库。
- M3 不实现历史迁移。以后确需版本 `2` 时，必须由新的已批准 SDD 定义迁移和兼容证据。
- Repository 构造器不隐式初始化 Schema；宿主必须先显式调用初始化函数。

### 5.3 连接规则

每次数据库连接必须：

- 启用 `PRAGMA foreign_keys = ON`。
- 使用参数化 SQL，不拼接领域字段到 SQL 字符串。
- 正常结束时关闭连接；异常时回滚当前事务并关闭连接。
- 不在模块导入时打开连接、创建文件或修改数据库。

M3 不启用 WAL、不增加连接池，也不定义跨进程并发策略。MVP 当前假定单应用实例；如果以后需要多进程写入或乐观并发控制，必须另行设计，不得暗中改变 Repository 契约。

## 6. SQLite Schema 版本 1

Schema 中只保存 M2 已冻结字段，不增加来源、标签、用户、模型元数据、Prompt、Token、置信度或隐藏推理字段。

### 6.1 `puzzles`

| 列 | SQLite 类型 | 约束 | 映射 |
|---|---|---|---|
| `id` | `TEXT` | `NOT NULL PRIMARY KEY` | `Puzzle.id` |
| `title` | `TEXT` | `NOT NULL` | `Puzzle.title` |
| `surface` | `TEXT` | `NOT NULL` | `Puzzle.surface` |
| `solution` | `TEXT` | `NOT NULL` | `Puzzle.solution` |
| `key_facts_json` | `TEXT` | `NOT NULL` | `Puzzle.key_facts` 的 JSON 数组 |
| `status` | `TEXT` | `NOT NULL`，值限 `ENABLED`、`DISABLED` | `Puzzle.status.value` |

建立索引：

```sql
CREATE INDEX idx_puzzles_status_id ON puzzles(status, id);
```

该索引服务 `list_enabled`。M3 不在 SQL 中随机排序。

### 6.2 `game_sessions`

| 列 | SQLite 类型 | 约束 | 映射 |
|---|---|---|---|
| `id` | `TEXT` | `NOT NULL PRIMARY KEY` | `GameSession.id` |
| `puzzle_id` | `TEXT` | `NOT NULL`，外键引用 `puzzles(id)` | `GameSession.puzzle_id` |
| `status` | `TEXT` | `NOT NULL`，值限 `PLAYING`、`SOLVED`、`ABANDONED` | `GameSession.status.value` |
| `started_at` | `TEXT` | `NOT NULL` | `GameSession.started_at` |
| `ended_at` | `TEXT` | 可空 | `GameSession.ended_at` |

数据库必须通过 `CHECK` 保证：

- `PLAYING` 的 `ended_at` 为 `NULL`。
- `SOLVED`、`ABANDONED` 的 `ended_at` 非 `NULL`。

完整聚合不变量仍由 M2 `GameSession` 构造器负责，SQLite 约束不能替代领域校验。

### 6.3 `question_records`

| 列 | SQLite 类型 | 约束 | 映射 |
|---|---|---|---|
| `session_id` | `TEXT` | `NOT NULL`，外键引用 `game_sessions(id)`，删除会话时级联 | 所属会话 |
| `position` | `INTEGER` | `NOT NULL` 且非负 | 在 `questions` 元组中的位置 |
| `record_id` | `TEXT` | `NOT NULL` | `QuestionRecord.id` |
| `question` | `TEXT` | `NOT NULL` | `QuestionRecord.question` |
| `verdict` | `TEXT` | `NOT NULL`，值限 `YES`、`NO`、`IRRELEVANT` | `QuestionRecord.verdict.value` |
| `created_at` | `TEXT` | `NOT NULL` | `QuestionRecord.created_at` |

约束：

- 主键为 `(session_id, record_id)`。
- `(session_id, position)` 唯一。
- 读取时按 `position ASC` 重建元组。

### 6.4 `guess_records`

| 列 | SQLite 类型 | 约束 | 映射 |
|---|---|---|---|
| `session_id` | `TEXT` | `NOT NULL`，外键引用 `game_sessions(id)`，删除会话时级联 | 所属会话 |
| `position` | `INTEGER` | `NOT NULL` 且非负 | 在 `guesses` 元组中的位置 |
| `record_id` | `TEXT` | `NOT NULL` | `GuessRecord.id` |
| `guess` | `TEXT` | `NOT NULL` | `GuessRecord.guess` |
| `solved` | `INTEGER` | `NOT NULL`，值限 `0`、`1` | `GuessRecord.solved` |
| `created_at` | `TEXT` | `NOT NULL` | `GuessRecord.created_at` |

约束：

- 主键为 `(session_id, record_id)`。
- `(session_id, position)` 唯一。
- 读取时按 `position ASC` 重建元组。

## 7. 序列化与重建契约

### 7.1 枚举和布尔值

- 枚举只存储其冻结字符串值。
- 读取时必须通过对应枚举构造器恢复；未知值必须失败，不得映射到默认枚举。
- `GuessRecord.solved` 只以整数 `0` 或 `1` 保存，读取后明确恢复为 `bool`。

### 7.2 `key_facts`

- `Puzzle.key_facts` 以 UTF-8 JSON 数组文本保存。
- 序列化必须保留元素顺序和 Unicode 内容。
- 读取后必须先确认解码结果是列表，再转换为元组交给 `Puzzle` 构造器校验。
- 非法 JSON、非数组 JSON、空数组或非法元素必须明确失败，不得返回空核心事实。

### 7.3 时间

- 所有时间使用 `datetime.isoformat(timespec="microseconds")` 保存为 ISO 8601 文本，必须包含 UTC 偏移。
- `None` 的 `ended_at` 保存为 SQL `NULL`。
- 读取使用 `datetime.fromisoformat`，再交由 M2 构造器执行带时区和聚合时间校验。
- M3 不统一转换到 UTC，也不保存时区名称；往返必须保持同一时间点和 UTC 偏移。
- 非法时间文本必须失败，不得使用当前时间或默认时间替代。

### 7.4 聚合重建

- `get` 必须使用 M2 公共构造器创建 `Puzzle`、`QuestionRecord`、`GuessRecord` 和 `GameSession`。
- 不得绕过 `__post_init__`、修改冻结字段或新增私有 `restore` 路径。
- 持久化数据违反 M2 契约时必须让读取失败，不得删除坏记录、修正状态或返回部分聚合。
- 不得将数据库行、可变列表或 SQLite Connection 暴露给调用方。

## 8. 写入与事务契约

### 8.1 题目保存

- 一次 `PuzzleRepository.save` 是一个事务。
- 插入或按 ID 更新全部题目列必须原子完成。
- 失败时数据库保持调用前状态。

### 8.2 游戏会话保存

一次 `GameSessionRepository.save` 必须在同一事务中：

1. 插入或按 ID 更新 `game_sessions` 快照。
2. 删除该会话原有的问题记录和猜测记录。
3. 按元组顺序写入当前快照的全部问题记录和猜测记录。
4. 提交事务。

任一步失败都必须回滚全部步骤，保留调用前的完整旧聚合。不得出现会话已更新但记录只写入一部分的状态。

保存会话前，对应 `puzzle_id` 必须已经存在。外键失败必须明确抛出真实错误并回滚，不得自动创建空题目或伪造关联。

M3 的 `save` 是完整快照覆盖，不提供局部追加 SQL 接口。M2 不可变聚合已经表达完整可信状态，局部更新会增加当前没有消费者的契约与一致性风险。

## 9. 失败契约

- Port 输入类型或空白 ID 错误抛出 `ValueError`。
- Schema 版本、结构或初始化前提错误抛出 `SQLiteSchemaError`。
- SQLite 打开、约束、锁定、磁盘或事务错误不得被吞掉，也不得转换成成功或 `None`。
- `get` 只有在目标 ID 确实不存在时返回 `None`；读取错误或数据损坏不得返回 `None`。
- 序列化、枚举、JSON、时间或 M2 聚合校验失败必须明确抛出异常。
- 不增加隐藏重试、自动重建数据库、自动清表、fallback 数据库或内存降级。
- 日志和异常不得包含完整题底、完整核心事实或数据库中的敏感内容。M3 不新增生产日志。

具体 SQLite 异常消息和底层错误码不属于冻结契约；测试验证失败类别、事务结果和未伪造成功，不锁定平台相关消息文本。

## 10. TDD 契约测试

`backend/tests/persistence/test_sqlite.py` 必须使用真实临时 SQLite 文件，至少覆盖以下语义。

### 10.1 Schema

- 新数据库初始化后 `user_version` 为 `1`，四张表和规定索引存在。
- 重复初始化版本 `1` 数据库不删除或改变已有业务数据。
- 版本 `0` 的部分 M3 Schema，以及版本 `1` 中缺少表/列、含 M3 额外列、列声明类型/`NOT NULL`/主键序号不匹配或缺少规定索引的 Schema 均明确失败且不被修复。
- 版本 `1` 数据库存在其他非 M3 表时允许重复初始化，且其他表和数据保持不变。
- 新建数据库必须以真实 SQLite 约束证明四张表的主键组成、外键、唯一约束、`CHECK` 约束和显式索引；不得仅检查建表 SQL 字符串。
- `puzzles.id`、`game_sessions.id`、`question_records.session_id` 和 `guess_records.session_id` 写入 SQL `NULL` 时必须失败。
- 完成版本 `0` 和版本 `1` 分支后，其他任何 `user_version` 均明确失败。
- 外键约束在实际 Repository 连接中生效。
- 初始化函数和两个 Repository 构造器都必须对错误类型、空白字符串、父目录不存在、目标是目录、`:memory:` 或 `file:` URI 输入立即失败；Repository 构造器失败前不得创建文件或打开连接。

### 10.2 题目 Repository

- 保存后能够完整读取 M2 `Puzzle`，包括 Unicode 与 `key_facts` 顺序。
- 相同 ID 再次保存会覆盖完整快照且只保留一条记录。
- 不存在的 ID 返回 `None`。
- `list_enabled` 排除禁用题目并按 ID 升序返回元组。
- 非法 Port 输入明确失败且不写入数据。

### 10.3 游戏会话 Repository

- `PLAYING`、`SOLVED` 和 `ABANDONED` 聚合都能完整往返。
- 问题与猜测分别按原元组顺序重建。
- 相同 ID 再次保存会覆盖聚合快照，不残留旧记录。
- 不存在的 ID 返回 `None`。
- 引用不存在题目的会话保存失败，且不留下会话或部分记录。
- 覆盖现有会话的事务回滚测试必须先保存一份完整旧聚合，再在 `tmp_path` 数据库中创建仅供该测试使用的真实 SQLite `BEFORE INSERT` 触发器，通过 `RAISE(ABORT, ...)` 强制子记录插入失败，并确认会话字段和两类旧记录仍完整可读。
- 事务失败注入不得 monkeypatch 私有函数、依赖内部辅助方法、增加生产测试分支或修改生产 Schema 初始化逻辑。
- 非法 Port 输入明确失败且不写入数据。

### 10.4 数据损坏与失败路径

- 未知枚举、非法 JSON、非法时间或违反 M2 聚合不变量的持久化数据在读取时明确失败。
- 数据损坏不得被转换为 `None`、空元组、默认枚举或默认时间。
- 测试必须核对事务失败后的真实数据库状态。

测试不得：

- 使用 fake、stub 或内存字典代替真实 SQLite 证明适配器行为。
- 使用 `:memory:` 绕过文件数据库契约。
- 使用反射锁定私有函数、SQL 语句排列或内部辅助方法。
- 修改、删除或放宽 M1/M2 冻结测试。
- 将测试题目当作正式题库或 M4 内容。
- 为了让测试变绿而在生产代码中加入测试分支、自动修复或隐藏 fallback。

## 11. M3 明确排除范围

M3 不实现或决定：

- 正式题目的内容、来源、授权、数量、难度或质量标准。
- M4 的题库文件格式、导入命令或种子数据。
- 随机选题、轮换、推荐或防重复策略。
- 应用用例、事务编排服务或游戏流程控制。
- 模型请求、Prompt、结构化模型输出或真实模型评测。
- FastAPI 路由、HTTP DTO、状态码或公开响应投影。
- 前端页面、状态管理或交互。
- 用户、登录、多人、排行榜、统计或审计日志。
- 数据库备份、加密、WAL、连接池、跨进程并发或生产迁移工具。

## 12. 实施与验证命令

开始实施前先确认冻结基线：

```powershell
conda run -n web python -m pytest backend/tests
conda run -n web python -m ruff check backend
pnpm --dir frontend test
pnpm --dir frontend lint
pnpm --dir frontend build
```

TDD 红灯必须来自缺少 M3 Port 或 SQLite 实现，而不是破坏 M1/M2 测试、环境错误或错误测试路径。

实施后至少运行：

```powershell
conda run -n web python -m pytest backend/tests/persistence
conda run -n web python -m pytest backend/tests
conda run -n web python -m ruff check backend
conda run -n web python -m pip check
pnpm --dir frontend test
pnpm --dir frontend lint
pnpm --dir frontend build
git status --short --branch --untracked-files=all
git diff
git diff --check
git ls-files --others --exclude-standard
```

还必须：

- 单独读取并核对所有未跟踪文件，因为普通 `git diff` 不包含它们。
- 对全部版本控制候选文件执行密钥扫描。
- 确认没有提交测试临时数据库、缓存或未获批准的运行时数据；获准的 `var/turtle_soup.sqlite3` 基线必须单独核对内容和提交授权。
- 逐项报告是否修改 M1/M2 冻结文件；正常 M3 实施不得修改它们。

M3 不包含模型行为，不运行真实模型语义评测，也不得用数据库测试声称模型集成成功。

## 13. 验收标准

M3 可以提交冻结的必要条件：

- 两个 Repository Port 的签名和同步属性与本规格一致。
- SQLite Schema 版本、表、约束、序列化格式和初始化失败行为有真实数据库证据。
- M2 领域对象能够完整往返，读取时仍经过 M2 不变量校验。
- 游戏聚合完整快照写入具有真实事务原子性证据。
- 不存在、输入错误、关联错误和损坏数据不会伪造成功或默认结果。
- 未引入第三方依赖、正式题库、Agently、API 或应用用例。
- M1/M2 冻结测试保持绿色且未被修改。
- Git、未跟踪文件、差异、空白和密钥检查通过。

## 14. M3 冻结范围

M3 完成实施、独立复核并获准提交后，冻结：

- `PuzzleRepository` 与 `GameSessionRepository` 的方法、参数、返回类型、同步属性和语义。
- SQLite 公共初始化函数、Repository 构造签名和 `SQLiteSchemaError` 类型边界。
- SQLite Schema 版本 `1` 的表、列、主外键、唯一约束、检查约束和索引。
- 枚举、布尔值、`key_facts` 与带时区时间的持久化格式。
- Repository 的完整快照覆盖、排序、缺失返回和事务回滚语义。
- M3 的真实 SQLite 契约测试。

后续模块不得删除、放宽或改写 M3 契约测试，也不得改变上述公共 Port、Schema 或同步语义。确需修改时必须停止并取得用户批准。

M3 冻结并上传后才能开始 M4。M4 只可在本契约之上整理合法题目内容和导入方式，不得反向弱化 M2/M3 契约。
