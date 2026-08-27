# M2 领域核心规格

## 1. 阶段目标

M2 只负责建立海龟汤游戏的领域核心代码与语义契约，使后续应用用例、持久化、模型判定、HTTP API 和前端都依赖同一组稳定的业务定义。

M2 采用 SDD + TDD。实施前必须以本规格为准先编写契约测试，再实现满足测试的最小领域代码。

M2 不收集、录入或发布正式题目。正式题库从 M4 开始整理。

## 2. 模块所有权与依赖边界

M2 的唯一所有者是后端 `domain` 模块。该模块负责：

- 题目、游戏会话、问题记录和最终猜测记录的领域表示。
- 题目状态、游戏状态和问题判定结果枚举。
- 游戏状态转换和题底可公开条件。
- 领域对象自身能够确定的输入、不变量和失败行为。

依赖规则：

- `domain` 只能依赖 Python 标准库。
- `domain` 不得依赖 FastAPI、Pydantic、Agently、SQLite、HTTP DTO、前端类型或环境变量。
- M2 不定义 Repository、模型调用 Port、应用服务或传输层接口。
- M2 不创建数据库、数据表、题库资源文件、Prompt 或模型配置。

## 3. 物理文件范围

M2 实施后允许新增的文件仅为：

```text
backend/
├── src/
│   └── turtle_soup/
│       └── domain/
│           ├── __init__.py
│           └── models.py
└── tests/
    └── domain/
        └── test_models.py
```

职责：

- `domain/models.py`：承载本规格定义的枚举、值对象、领域实体、领域异常和状态转换。
- `domain/__init__.py`：只导出本规格明确列出的公共领域类型，不包含业务实现或兼容别名。
- `tests/domain/test_models.py`：验证公共语义契约和领域不变量，不锁定私有方法或内部实现细节。

`domain/__init__.py` 的公共导出固定为：

- `PuzzleStatus`
- `GameStatus`
- `Verdict`
- `Puzzle`
- `QuestionRecord`
- `GuessRecord`
- `GameSession`
- `InvalidGameStateError`

不得为了形式完整增加 `services/`、`repositories/`、`ports/`、`infrastructure/`、`workflows/` 或其他空目录。

## 4. 公共枚举契约

所有枚举必须使用字符串值。枚举名称和值均属于冻结公共契约。

### 4.1 `PuzzleStatus`

| 成员 | 字符串值 | 语义 |
|---|---|---|
| `ENABLED` | `ENABLED` | 题目允许被后续应用用例选择 |
| `DISABLED` | `DISABLED` | 题目不得被后续应用用例选择 |

M2 只定义状态，不实现题目选择逻辑。

### 4.2 `GameStatus`

| 成员 | 字符串值 | 语义 |
|---|---|---|
| `PLAYING` | `PLAYING` | 游戏进行中，可记录问题或最终猜测 |
| `SOLVED` | `SOLVED` | 玩家已提交命中核心真相的最终猜测 |
| `ABANDONED` | `ABANDONED` | 玩家主动结束或放弃游戏 |

`SOLVED` 和 `ABANDONED` 都是终局状态，终局后不得再记录问题、猜测或执行第二次终局转换。

### 4.3 `Verdict`

| 成员 | 字符串值 | 语义 |
|---|---|---|
| `YES` | `YES` | 玩家问题根据题底应回答“是” |
| `NO` | `NO` | 玩家问题根据题底应回答“不是” |
| `IRRELEVANT` | `IRRELEVANT` | 玩家问题与题底真相无关或无法由题底确定 |

中文显示文本不属于 M2；枚举到“是 / 不是 / 无关”的映射由后续应用或传输投影负责。

## 5. 公共领域类型

领域对象应使用明确类型，并避免暴露可由调用方绕过不变量直接修改的可变集合。实现可以使用标准库 `dataclass`，但不得为了隐藏实现而引入额外框架或抽象层。

四个领域对象的公共构造器均只接受关键字参数。构造签名固定为：

```python
Puzzle(
    *,
    id: str,
    title: str,
    surface: str,
    solution: str,
    key_facts: tuple[str, ...],
    status: PuzzleStatus,
) -> Puzzle

QuestionRecord(
    *,
    id: str,
    question: str,
    verdict: Verdict,
    created_at: datetime,
) -> QuestionRecord

GuessRecord(
    *,
    id: str,
    guess: str,
    solved: bool,
    created_at: datetime,
) -> GuessRecord

GameSession(
    *,
    id: str,
    puzzle_id: str,
    status: GameStatus,
    started_at: datetime,
    ended_at: datetime | None,
    questions: tuple[QuestionRecord, ...] = (),
    guesses: tuple[GuessRecord, ...] = (),
) -> GameSession
```

`GameSession` 公共构造器用于根据完整可信字段直接创建或由后续持久化适配器重建聚合，并且必须立即校验全部聚合不变量。M2 不增加独立的 `restore`、`rehydrate` 或其他恢复工厂。新游戏仍必须通过 `GameSession.start(...)` 创建。

### 5.1 `Puzzle`

`Puzzle` 表示一份服务端持有的完整题目定义。

| 字段 | 类型 | 必填 | 契约 |
|---|---|---|---|
| `id` | `str` | 是 | 服务端可信且不可变的题目标识；去除首尾空白后不得为空 |
| `title` | `str` | 是 | 题目标题；去除首尾空白后不得为空 |
| `surface` | `str` | 是 | 展示给玩家的题面；去除首尾空白后不得为空 |
| `solution` | `str` | 是 | 完整题底；去除首尾空白后不得为空 |
| `key_facts` | `tuple[str, ...]` | 是 | 判断最终猜测的核心事实；至少一项，每项去除首尾空白后不得为空 |
| `status` | `PuzzleStatus` | 是 | 题目是否可供后续应用用例选择 |

契约规则：

- `Puzzle` 是不可变领域对象。
- 校验只拒绝非法输入，不静默修剪、改写、补齐或生成题目内容。
- `solution` 和 `key_facts` 是服务端秘密字段；`Puzzle` 本身不负责生成公开 DTO。
- M2 不增加难度、分类、标签、来源、版权、推荐权重、创建时间或统计字段；这些字段当前没有领域消费者。

### 5.2 `QuestionRecord`

`QuestionRecord` 表示一次已经得到有效判定的问题记录。

| 字段 | 类型 | 必填 | 契约 |
|---|---|---|---|
| `id` | `str` | 是 | 服务端生成的可信记录标识；去除首尾空白后不得为空 |
| `question` | `str` | 是 | 玩家原始问题；去除首尾空白后不得为空 |
| `verdict` | `Verdict` | 是 | 已通过宿主校验的三分类结果 |
| `created_at` | `datetime` | 是 | 带时区的记录时间 |

`QuestionRecord` 是不可变值对象。M2 不记录模型原始响应、Prompt、推理、置信度、Token 或供应商元数据。

### 5.3 `GuessRecord`

`GuessRecord` 表示一次已经得到有效判定的最终猜测记录。

| 字段 | 类型 | 必填 | 契约 |
|---|---|---|---|
| `id` | `str` | 是 | 服务端生成的可信记录标识；去除首尾空白后不得为空 |
| `guess` | `str` | 是 | 玩家原始最终猜测；去除首尾空白后不得为空 |
| `solved` | `bool` | 是 | 是否命中核心真相；必须是布尔值 |
| `created_at` | `datetime` | 是 | 带时区的记录时间 |

`GuessRecord` 是不可变值对象。未破解的猜测仍是有效记录，但不会结束游戏。

### 5.4 `GameSession`

`GameSession` 是一局游戏的领域聚合。

| 字段 | 类型 | 必填 | 契约 |
|---|---|---|---|
| `id` | `str` | 是 | 服务端生成的可信游戏标识；去除首尾空白后不得为空 |
| `puzzle_id` | `str` | 是 | 本局使用的题目标识；去除首尾空白后不得为空 |
| `status` | `GameStatus` | 是 | 当前游戏状态 |
| `started_at` | `datetime` | 是 | 带时区的开始时间 |
| `ended_at` | `datetime | None` | 是 | 进行中必须为 `None`；终局必须为带时区时间 |
| `questions` | `tuple[QuestionRecord, ...]` | 是 | 按写入顺序保存的问题记录，默认为空元组 |
| `guesses` | `tuple[GuessRecord, ...]` | 是 | 按写入顺序保存的最终猜测记录，默认为空元组 |

`GameSession` 必须采用不可变聚合语义：状态转换方法返回新的 `GameSession`，不得原地修改原对象或向调用方暴露可变记录列表。

表中的“必填”表示字段在领域对象上始终存在。公共构造器允许省略 `questions` 和 `guesses`，且只允许使用签名中声明的空元组默认值；其他字段均必须显式传入。

### 5.5 严格运行时类型规则

所有公共构造器和状态转换方法必须执行严格的运行时类型校验：

- `str` 字段必须满足 `type(value) is str`，不接受字符串枚举、字符串子类或其他类型，也不将其他值转换为字符串。
- `PuzzleStatus`、`GameStatus` 和 `Verdict` 字段只接受对应枚举实例，不接受同值原始字符串或其他枚举实例。
- `key_facts`、`questions` 和 `guesses` 必须满足 `type(value) is tuple`，不接受元组子类、列表、生成器或其他可迭代对象，也不得自动转换为元组。
- `key_facts` 的每一项必须满足 `type(item) is str`；`questions` 和 `guesses` 的每一项必须分别是 `QuestionRecord` 和 `GuessRecord` 实例。
- `GuessRecord.solved` 必须满足 `type(solved) is bool`；整数 `0`、`1` 或其他真值对象均不合法。
- 时间字段必须是 `datetime` 实例，并满足第 6 节的带时区时间规则。
- 校验不得修剪或重写字符串。`strip()` 只能用于判断字符串是否为空或全空白，合法字段必须原样保存。
- 除构造器仅关键字调用方式本身由 Python 拒绝外，违反上述运行时类型契约统一抛出 `ValueError`，不得执行隐式转换或返回替代值。

## 6. 时间与标识所有权

- 所有 `id` 和时间都由宿主程序提供，领域模块不得自行读取系统时钟、生成 UUID 或产生随机值。
- 所有时间必须是带时区的 `datetime`。带时区的精确定义为 `value.tzinfo is not None` 且 `value.utcoffset() is not None`；任一条件不满足都必须立即失败。
- `ended_at` 不得早于 `started_at`。
- 问题和猜测的 `created_at` 不得早于 `started_at`。
- 终局会话中的记录时间不得晚于 `ended_at`。
- M2 不强制转换时区；调用方负责提供约定时区，后续持久化规格负责定义存储格式。

## 7. `GameSession` 创建与状态转换

### 7.1 创建新游戏

公共类方法：

```python
GameSession.start(
    *,
    id: str,
    puzzle_id: str,
    started_at: datetime,
) -> GameSession
```

返回契约：

- `status` 固定为 `PLAYING`。
- `ended_at` 固定为 `None`。
- `questions` 和 `guesses` 固定为空元组。
- 输入非法时明确失败，不生成替代 ID 或默认时间。

### 7.2 记录问题

公共方法：

```python
session.record_question(record: QuestionRecord) -> GameSession
```

行为：

- 只允许在 `PLAYING` 状态调用。
- 将记录追加到新会话的 `questions` 尾部。
- 不改变 `status`、`ended_at` 和既有记录。
- 原 `session` 保持不变。
- 同一会话内 `QuestionRecord.id` 不得重复。

### 7.3 记录最终猜测

公共方法：

```python
session.record_guess(record: GuessRecord) -> GameSession
```

行为：

- 只允许在 `PLAYING` 状态调用。
- 将记录追加到新会话的 `guesses` 尾部。
- 当 `record.solved` 为 `False` 时，游戏保持 `PLAYING`，`ended_at` 保持 `None`。
- 当 `record.solved` 为 `True` 时，游戏转换为 `SOLVED`，`ended_at` 等于该记录的 `created_at`。
- 原 `session` 保持不变。
- 同一会话内 `GuessRecord.id` 不得重复。

### 7.4 放弃游戏

公共方法：

```python
session.abandon(*, ended_at: datetime) -> GameSession
```

行为：

- 只允许在 `PLAYING` 状态调用。
- 返回 `status=ABANDONED` 的新会话。
- 新会话的 `ended_at` 使用调用方提供的时间。
- 问题和猜测记录保持不变。
- `ended_at` 不得早于开始时间或任何现有记录时间。
- 原 `session` 保持不变。

### 7.5 题底可公开条件

只读属性：

```python
session.can_reveal_solution -> bool
```

返回规则：

- `PLAYING` 返回 `False`。
- `SOLVED` 和 `ABANDONED` 返回 `True`。

该属性只表达领域许可，不直接读取 `Puzzle.solution`，也不构造 API 响应。

## 8. 聚合不变量

无论通过工厂方法、状态转换还是后续持久化重建，`GameSession` 都必须满足：

1. `PLAYING` 的 `ended_at` 必须为 `None`，且所有现有猜测的 `solved` 必须为 `False`。
2. `SOLVED` 的 `ended_at` 必须存在，最后一条猜测必须为 `solved=True`，此前猜测必须为 `solved=False`。
3. `ABANDONED` 的 `ended_at` 必须存在，所有猜测必须为 `solved=False`。
4. `questions` 中的记录 ID 不得重复。
5. `guesses` 中的记录 ID 不得重复。
6. 记录顺序由元组顺序表达；同类记录的 `created_at` 不得倒序。
7. 终局状态不可再次转换，也不可增加记录。

M2 不规定问题记录和猜测记录彼此之间的全局排序。后续应用投影如需合并时间线，应根据记录时间执行确定性排序并定义相同时间的规则。

## 9. 失败契约

公开异常：

```python
class InvalidGameStateError(RuntimeError):
    ...
```

失败规则：

- 在非 `PLAYING` 状态记录问题、记录猜测或放弃游戏时，抛出 `InvalidGameStateError`。
- 字段类型错误、空白字符串、无时区时间、重复记录 ID、时间倒序或聚合组合非法时，抛出 `ValueError`。
- 不冻结异常消息文本；测试只验证异常类型和失败发生，不锁定措辞。
- 不捕获后返回空对象，不自动修正非法状态，不使用默认时间、默认 ID 或默认枚举掩盖错误。

## 10. TDD 契约测试

`backend/tests/domain/test_models.py` 至少覆盖：

### 枚举

- 三个枚举的成员和值与本规格完全一致。

### `Puzzle`

- 合法题目可以创建，字段保持原值且对象不可变。
- 构造器拒绝位置参数，只接受冻结签名声明的关键字参数。
- `id`、`title`、`surface`、`solution` 为空或全空白时失败。
- `key_facts` 为空或包含空白项时失败。
- 非 `PuzzleStatus` 状态失败。
- `key_facts` 为列表、生成器或包含非字符串项时失败，不执行元组转换。

### 记录类型

- 合法问题记录和猜测记录可以创建且不可变。
- 两个构造器都拒绝位置参数，只接受冻结签名声明的关键字参数。
- 空白 ID、空白玩家输入、错误枚举、非布尔 `solved` 或无时区时间失败。
- `verdict` 使用同值原始字符串时失败；`solved` 使用 `0`、`1` 或其他真值对象时失败。
- `tzinfo` 非空但 `utcoffset()` 返回 `None` 的时间仍按无时区时间拒绝。

### `GameSession`

- `start` 创建空的 `PLAYING` 会话。
- 公共构造器拒绝位置参数；除 `questions` 和 `guesses` 外，其他冻结字段必须通过关键字显式传入。
- 公共构造器能够使用合法完整字段直接创建 `PLAYING`、`SOLVED` 和 `ABANDONED` 会话，作为后续持久化重建契约。
- `status` 使用同值原始字符串时失败；`questions` 或 `guesses` 使用列表、生成器、错误记录类型时失败，不执行隐式转换。
- 合法问题被追加，新旧会话对象相互独立。
- 未破解猜测被追加但不结束游戏。
- 破解猜测将游戏转换为 `SOLVED`，结束时间取猜测时间。
- 放弃将游戏转换为 `ABANDONED` 并保留记录。
- `can_reveal_solution` 只在两个终局状态为真。
- 两类记录分别拒绝重复 ID 和同类时间倒序。
- 记录时间早于游戏开始时失败。
- 非 `PLAYING` 状态拒绝记录问题、记录猜测和再次放弃。
- 直接构造或重建时拒绝 `status`、`ended_at`、猜测结果和记录时间不一致的组合。

测试不得：

- 使用反射锁定私有方法。
- 锁定 dataclass 的内部字段拓扑或具体实现语句。
- 为了通过测试加入生产代码测试分支。
- 将测试样例题目作为正式题库或模型语义质量证据。

## 11. M2 明确排除范围

M2 不实现或决定：

- 正式题目的数量、内容、来源、授权或整理流程。
- 网络爬取、自动生成、自动改写或在线导入题目。
- 题目随机选择、轮换、去重、推荐或难度策略。
- Repository、SQLite Schema、事务或数据迁移。
- 开始游戏、提问、猜测和放弃的应用用例编排。
- 输入长度、最大回合数、请求频率或模型超时。
- Agently ModelRequest、Prompt、结构化输出解析或真实模型评测。
- FastAPI 路由、Pydantic DTO、HTTP 状态码或公开响应投影。
- 前端组件、状态管理、样式或移动端交互。

上述内容分别由后续获批模块定义，不得提前进入 M2。

## 12. 实施与验证命令

开始 M2 实施前必须确认冻结基线：

```powershell
conda run -n web python -m pytest backend/tests
conda run -n web python -m ruff check backend
pnpm --dir frontend test
pnpm --dir frontend lint
pnpm --dir frontend build
```

M2 实施后至少运行：

```powershell
conda run -n web python -m pytest backend/tests/domain
conda run -n web python -m pytest backend/tests
conda run -n web python -m ruff check backend
pnpm --dir frontend test
pnpm --dir frontend lint
pnpm --dir frontend build
git status --short --untracked-files=all
git diff
git diff --check
```

还必须执行版本控制候选文件的密钥扫描。M2 不需要真实模型验证，因为本模块没有模型行为。

## 13. M2 冻结范围

M2 完成独立复核并获准提交后，冻结：

- `PuzzleStatus`、`GameStatus` 和 `Verdict` 的成员与字符串值。
- `Puzzle`、`QuestionRecord`、`GuessRecord` 和 `GameSession` 的公共字段、类型和语义。
- `GameSession.start`、`record_question`、`record_guess`、`abandon` 和 `can_reveal_solution` 的参数、返回类型、同步属性和行为。
- `InvalidGameStateError` 的异常类型边界。
- 本规格列出的领域不变量和契约测试。

后续模块不得删除、放宽或改写 M2 契约测试，也不得改变上述公共字段、枚举、方法参数、返回类型、同步属性或语义。确需调整时必须停止并取得用户批准。

M2 冻结并上传后才能开始 M3。正式题库仍必须等到 M4 才能整理和录入。
