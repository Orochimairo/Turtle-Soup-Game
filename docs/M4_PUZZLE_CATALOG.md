# M4 受版本控制正式题库与导入规格

## 1. 阶段目标

M4 只负责建立经过内容审查和用户逐题批准的海龟汤题库，并提供使用 M3 冻结 Repository 将用户明确指定的题库显式导入已初始化 SQLite 数据库的能力。用户已明确授权将完整题面、题底、核心事实和内容审查材料纳入 Git；整个 `var/` 仍不得进入 Docker 构建上下文，且不得包含密钥、认证信息或未获授权的个人敏感信息。

M4 为 M5 提供具有真实内容质量和来源证据的代表性题目，使后续模型语义评测不依赖临时样例、来源不明的网络转载或为了测试而编写的过拟合题目。

M4 采用 SDD + TDD，并遵循 `docs/MODULE_IMPLEMENTATION_AND_SDD_TDD_ACCEPTANCE_PLAN.md` 的统一实施、复核、冻结和上传流程。本规格冻结 M4 专属的题目获取、内容准入、资源格式、身份生命周期、导入和验收契约；发生冲突时必须停止并报告。

本规格本身不批准搜索、收集、复制或录入任何具体题目。正式内容获取必须在本规格独立复核并经用户另行批准后开始。

本规格、M4 内容审查索引、正式题库和完整审查记录都属于 Git 冻结证据，应与获准实现一起提交和上传。

## 2. 所有者与依赖边界

M4 包含三个所有者边界：

- 题库策展负责在受版本控制的脱敏审查文档中完成候选登记、内容审查结论和批准记录，并在受版本控制的 `var/catalog/private_review/` 中保存完整内容工作稿与内容审查材料。
- `catalog` 模块负责调用方明确指定的本地 JSON 文件的确定性读取、解析、校验、M2 `Puzzle` 构造和显式导入。
- M3 `PuzzleRepository` 继续独占 SQLite 持久化实现；M4 只能调用其冻结公共 Port，不得直接操作 M3 表或连接。

依赖方向固定为：

```text
private local catalog resource
  -> catalog importer
      -> domain.models.Puzzle
      -> domain.ports.PuzzleRepository
      -> infrastructure.SQLitePuzzleRepository
```

约束：

- M4 不修改 M2 领域对象、枚举、构造器或测试。
- M4 不修改 M3 Repository Port、SQLite Schema、事务语义、序列化或测试。
- 来源元数据属于 `var/catalog/catalog.v1.json` 中的受控题库资源，不增加到 `Puzzle`，也不写入 SQLite。
- M4 不依赖 FastAPI、Pydantic、Agently、前端或第三方题库服务。
- M4 只使用 Python 标准库和现有 M2/M3 能力，不新增依赖。
- M4 不拥有随机选题、游戏状态、模型判定或题底公开逻辑。

## 3. 物理文件与隐私范围

### 3.1 可进入版本控制的实施文件

M4 实施只允许在 Git 候选范围新增：

```text
docs/
└── M4_CONTENT_REVIEW.md

backend/
├── src/
│   └── turtle_soup/
│       └── catalog/
│           ├── __init__.py
│           ├── __main__.py
│           └── importer.py
└── tests/
    └── catalog/
        └── test_catalog.py
```

职责：

- `docs/M4_CONTENT_REVIEW.md`：保存候选引用、来源记录、追加式门禁历史、内容审查摘要、预冻结题库引用或正式 ID、逐题批准记录和题库哈希；不得保存完整题面、题底、核心事实或完整内容审查原文。
- `importer.py`：读取、解析并严格校验显式指定的本地资源，构造 M2 `Puzzle`，执行导入预检并调用 M3 Repository。
- `__main__.py`：提供显式命令行导入入口。
- `__init__.py`：只导出本规格冻结的 M4 公共入口。
- `test_catalog.py`：只使用与真实题目无关的合成测试数据，验证资源格式、本地路径、身份冲突、真实 SQLite 导入和失败契约。

真实完整题面、题底、核心事实和私有内容审查原文不得进入上述目录、Git 未跟踪候选或其他可上传文件。候选名称、非剧透内容分类、脱敏证据引用、审查结论、预冻结题库引用和正式 ID 可以进入 `docs/M4_CONTENT_REVIEW.md`；不得用“识别摘要”重新描述谜底、核心反转、具体伤害方式或关键因果关系。

### 3.2 受版本控制的内容文件

正式内容固定保存在：

```text
var/
└── catalog/
    ├── catalog.v1.json
    └── private_review/
```

职责：

- `var/catalog/catalog.v1.json`：内容冻结后保存获准的正式题目及其来源元数据；内容冻结前允许原路径保存本批次本地预冻结工作稿，但该工作稿不具有正式题库身份，禁止导入、运行时加载或用于 M4 冻结验收。
- `var/catalog/private_review/`：保存门禁复核所需的正式入库前完整内容工作稿和内容审查材料；当前文件作为 Git 冻结证据提交，内部文件名和格式不属于运行时公共契约。

隐私与版本控制契约：

- 仓库根目录 `.gitignore` 不得排除 `var/`；正式题库、审查材料和获准 SQLite 基线必须通过普通 `git add` 纳入版本控制，不得依赖 `-f` 绕过规则。
- 仓库根目录 `.dockerignore` 必须继续以 `var` 排除整个目录；Docker 构建上下文不得包含正式题库、内容审查材料、评测证据或 SQLite 数据。
- `private_review/` 不是运行时题库，不得被 catalog 解析器、导入器、应用或测试读取；内容冻结后，正式运行唯一允许加载的题库文件仍是 `var/catalog/catalog.v1.json`。同一路径下的预冻结工作稿不得因此被视为可运行或可导入资源。
- `docs/M4_CONTENT_REVIEW.md` 只保存可映射到私有材料的非敏感证据引用、日期和结论。获准审核者必须直接读取相应私有材料后才能通过门禁，聊天声明、公开摘要或文件存在本身不能替代复核。
- 正式题库和审查材料只允许存在于获准的 `var/catalog/` 路径，不得复制到 `backend/`、`frontend/`、`docs/`、测试夹具、日志、`.agently/`、缓存或构建产物。
- 不创建或提交真实题库示例、删减副本、快照、补丁、备份或导出文件；正式题库 SHA-256 可以记录在脱敏的 `docs/M4_CONTENT_REVIEW.md` 中。
- `catalog.v1.json` 缺失时加载和导入必须明确失败。门禁所需的内容证据或审查记录缺失时，对应候选不得转换状态或冻结；代码和测试不得生成、下载或补齐任何正式内容。

### 3.3 版本控制规格与工作规则文档

以下 Markdown 属于 Git 候选和 GitHub 交付物：

- `AGENTS.md`。
- `docs/M4_PUZZLE_CATALOG.md`。
- `docs/M4_CONTENT_REVIEW.md`。
- `docs/MODULE_IMPLEMENTATION_AND_SDD_TDD_ACCEPTANCE_PLAN.md` 及其他 `docs/*.md`。

约束：

- `.gitignore` 不得以通配规则忽略 `AGENTS.md` 或 `docs/*.md`。
- M4 开工、复核和交接必须直接读取这些文档，并通过 Git 差异确认变更。
- 规格、工作规则和脱敏审查记录由 Git 提交冻结；提交不能替代对当前工作区真实文件的直接复核。
- `docs/M4_CONTENT_REVIEW.md` 只保存长期需要的脱敏证据，不得因允许上传 Markdown 而泄露完整题库内容。

不得创建爬虫、下载器、远程客户端、生成器、CMS、后台任务、迁移、额外 Repository、数据库表或候选题目缓存目录。不得修改依赖文件、前端文件或既有冻结文件。

## 4. 题库来源记录

### 4.1 来源类型

题目来源只作为普通记录登记，不设立权利门禁，不要求额外权利证据。`source_kind` 保留以下四个描述性标签：

| `source_kind` | 含义 |
|---|---|
| `ORIGINAL` | 为本项目原创的题目 |
| `LICENSED` | 依据明确许可使用的内容 |
| `PERMISSION` | 权利人已向本项目授权的使用内容 |
| `PUBLIC_DOMAIN` | 可确认进入公有领域的素材 |

标签只用于来源可追溯记录，不决定题目能否进入题库。内容是否采用由第 6 节的内容审查和用户逐题批准决定。

### 4.2 来源记录要求

每道题必须记录：

- 原始来源引用（URL、书目信息、内部文档引用或原创记录）。
- 发现或提供日期。
- 使用的 `source_kind` 标签。
- 改编说明（如有）。

来源信息仅作追溯记录，不进入 M2、SQLite 或公开 API。M4 运行时和导入过程始终不得访问互联网。

### 4.3 获取批次

每一批内容获取开始前必须先记录：

- 批次目标和计划数量。
- 使用语言和目标受众。
- 内容安全边界。
- 期望覆盖的不同叙事和推理结构。
- 为 M5 真实模型评测提供代表性的理由。

M4 私有内容首次冻结时，`var/catalog/catalog.v1.json` 必须至少包含 8 道 `ENABLED` 正式题目。数量不能替代逐题质量和内容审查；不足时必须报告，不能用低质量、来源不明、合成测试数据或测试占位题目补足。

## 5. 候选登记与门禁状态

### 5.1 候选登记

发现候选时只登记必要元数据，不立即把完整题面和题底复制到正式资源。候选登记至少包含：

- 临时候选引用，不使用正式题目 ID。
- 候选名称和非剧透内容分类；不得包含谜底、核心反转、具体伤害方式或关键因果关系。
- 原始来源 URL、书目信息或内部原创记录。
- 发现日期。
- 拟归属的 `source_kind`。
- 尚待确认的问题。
- 当前门禁结论和理由。

不得在候选记录中复制与审查无关的大段外部原文，也不得提交包含私人邮箱、电话号码或其他个人敏感信息的证据。

### 5.2 门禁状态

`docs/M4_CONTENT_REVIEW.md` 必须为每个候选保存追加式状态转换历史，过程状态固定为：

- `DISCOVERED`：只完成候选登记，尚无准入资格。
- `CONTENT_REVIEWED`：内容一致性和安全审查通过。
- `APPROVED`：用户批准进入正式题库。
- `REJECTED`：不再进入当前题库，并记录拒绝原因。

正常转换顺序固定为：

```text
DISCOVERED
  -> CONTENT_REVIEWED
  -> APPROVED
```

任一尚未 `APPROVED` 的状态都可以转为 `REJECTED`。每次转换必须追加记录状态、`YYYY-MM-DD` 日期、非空证据引用和必要说明；不得覆盖、删除或改写先前转换。`APPROVED` 只能从 `CONTENT_REVIEWED` 转入，并且必须具有对应的私有内容审查证据和用户逐题批准证据。被拒绝的候选如需重新提出，必须使用新的临时候选引用重新开始流程。

状态历史只用于策展证据，不进入 M2、SQLite 或公开 API。

### 5.3 来源记录

候选来源按第 4 节登记为普通记录，不设立独立权利门禁，不要求权利证据或授权材料。来源记录只用于策展可追溯性，不进入 M2、SQLite 或公开 API。

## 6. 内容整理与人工审查

### 6.1 内容整理

完成候选登记后，才可以整理 M2 已冻结的以下字段：

- `title`
- `surface`
- `solution`
- `key_facts`
- `status`

整理要求：

- `surface` 只提供玩家开局需要的信息，不直接泄露决定性真相。
- `solution` 必须完整解释题面中的异常和核心因果关系。
- 每项 `key_facts` 表达一个可独立判断的关键事实，整体足以判断最终猜测是否破解。
- 不为了让某个模型或固定测试样例通过而改变题底或核心事实。
- 不加入原始材料和获准改编无法支持的关键设定。
- 改编内容必须在来源元数据和审查文档中记录改动性质。

### 6.2 内容质量审查

每道题至少检查：

- 标题和题面是否存在意外剧透。
- 题底是否自洽并完整解释题面。
- 是否存在明显同样合理但题底无法排除的替代解释。
- 核心事实是否必要、清晰、不互相重复且不依赖隐藏补充。
- 玩家问题能否依据题底合理判定为“是”“不是”或“无关”。
- 是否依赖图片、声音、字形、谐音或当前产品未提供的信息。
- 是否依赖过度冷门且未在题底解释的知识。
- 是否含有真实个人隐私、未妥善处理的真实案件或其他敏感事实。
- 是否符合已批准的目标受众和内容安全边界。

MVP 可以包含悬疑、死亡或犯罪背景。除第 6.3 节列出的本批次明确例外外，不得收录露骨色情、仇恨内容、过度血腥描写、对自伤行为的美化、以精神健康状况对群体作危险化归因，或以现实受害者为娱乐素材的内容。

自动化测试只能验证结构和确定性规则，不能证明题目有趣、推理公平、来源合法或内容适宜。以上结论必须保留人工证据。

### 6.3 当前批次明确风险例外

用户在知悉内容审查结论后，明确接受以下三个当前批次候选的特定风险：

| 候选引用 | 预冻结题库引用 | 明确接受的风险 |
|---|---|---|
| `DOCX30-R2-C008` | `ts-0008` | 自伤或明知致命的自毁行为可能具有浪漫化、表演化观感。 |
| `DOCX30-R2-C028` | `ts-0028` | 叙事可能造成对精神健康群体的危险化或污名化观感。 |
| `DOCX30-R2-C029` | `ts-0029` | 叙事可能造成对产后精神障碍的危险化或污名化观感。 |

该决定仅适用于上表三个候选及其本批次待复核内容，不构成未来题目的通用豁免或安全边界先例。接受上述风险不等于允许以下内容：

- 提供自伤、伤害或犯罪行为的可操作方法、模仿性细节、直接鼓励或号召。
- 露骨色情、仇恨内容、过度血腥或以现实受害者为娱乐素材。
- 把叙事中的敏感归因表述为医学事实、普遍规律或对现实群体的事实判断。

风险接受决定不替代内容质量审查或逐题正式批准。三个候选必须依据本节修订后的边界重新完成内容审查并保留私有证据；只有审查通过后才能追加 `CONTENT_REVIEWED`，其后仍须由用户逐题决定是否转入 `APPROVED`。M4 只记录风险类别与审核决定，不在本模块新增内容警告 UI、API 字段或运行时行为；相关展示需求由后续所属模块另行规划。

## 7. M4 人工盲测取消决定

用户于 `2026-08-27` 明确取消 M4 阶段的逐题人工盲测。M4 不再定义或要求 `BLIND_TESTED` 状态、盲测记录、盲测通过标准或盲测证据，正式题库准入流程改为内容质量审查通过后由用户逐题批准。

该决定不改变以下边界：

- 第 6 节的逐题人工内容质量审查仍为强制门禁，自动化结构测试或模型自测不能替代。
- 用户必须基于最终内容和脱敏审查结论逐题批准；批量默认批准、推定批准或由实施者代为批准均不允许。
- `surface`、`solution` 或 `key_facts` 在批准前发生实质修改时，必须重新完成内容质量审查。
- M4 不生成、伪造或保存用于模拟盲测通过的记录，也不把自动化测试或 M5 模型评测标记为人工盲测。
- 取消盲测意味着 M4 不再提供真实玩家可解性、提问稳定性或敏感内容实际观感的人工验证证据；该限制必须在 M4 冻结报告中明确记录。

## 8. 正式批准、ID 与状态

### 8.1 正式批准

用户逐题批准前，候选必须同时满足以下前置条件：

- 当前状态为 `CONTENT_REVIEWED`。
- 追加式历史已记录 `CONTENT_REVIEWED` 的日期与私有证据引用。
- 来源元数据完整。

满足前置条件后，用户查看最终内容或其获准复核证据并明确逐题批准，策展记录必须追加从 `CONTENT_REVIEWED` 到 `APPROVED` 的转换。转换完成后，该候选的当前状态为 `APPROVED`。

只有当前状态为 `APPROVED`，且追加式历史同时包含对应 `CONTENT_REVIEWED` 私有证据和用户逐题批准证据的内容，才能取得正式题库身份并获准通过 `var/catalog/catalog.v1.json` 加载或导入。

当前已经存在的 `var/catalog/catalog.v1.json` 在所有候选完成相应门禁前只是本地预冻结工作稿，不得加载、导入、冻结或作为 M4 完成证据。工作稿中的草稿、待审或被拒绝候选不得通过改成 `DISABLED` 绕过门禁；正式内容冻结时，文件中每个题目都必须已经 `APPROVED`。

### 8.2 正式 ID

正式 ID 格式固定为 `ts-NNNN`，其中 `NNNN` 是从 `0001` 开始的四位十进制序号，例如 `ts-0001`。除下述当前批次预留映射外，ID 按批准顺序分配。

规则：

- 候选阶段不分配正式 ID。当前预冻结工作稿中已有的 `ts-0001` 至 `ts-0030` 仅是本批次候选与私有审查证据之间的临时预留引用，不是正式 ID。
- 只有对应候选依次完成 `CONTENT_REVIEWED → APPROVED` 后，该候选的预留引用才取得正式 ID 身份；未完成门禁的预留引用不得导入、冻结或被运行时使用。
- 当前批次预留映射只用于兼容已经形成的私有工作稿与证据引用，不构成以后在批准前分配正式 ID 的先例。未取得正式身份的预留引用不得改配给其他候选。
- 正式 ID 永久稳定且不得复用。
- ID 不编码题底、来源、分类、难度或状态。
- 删除或拒绝的 ID 不重新分配给其他题目。
- JSON 中题目必须按 ID 严格升序排列。

### 8.3 状态

- 首次进入正式题库的题目默认且必须为 `ENABLED`。
- `DISABLED` 只用于已经发布后被退役但仍需保留历史身份的题目。
- 候选状态不得映射为 `PuzzleStatus`。

## 9. 更新、退役与身份冲突

题目发布后必须保护既有游戏会话所引用的题目语义。

更新规则：

- 同一正式 ID 只允许变更 `status`；`title`、`surface`、`solution` 或 `key_facts` 的任何变化都必须分配新 ID，包括排版和错别字修正。
- 新 ID 必须重新完成内容审查和用户逐题批准；旧 ID 应保留原内容，并在不再用于新游戏时改为 `DISABLED`。
- 不改变 M2 `Puzzle` 字段的来源证据补充或脱敏修正可以保留原 ID，但必须保留审查记录。
- 旧题不再用于新游戏时改为 `DISABLED`，不得删除或用另一故事覆盖。
- 来源记录失效或发现严重内容问题时必须停用，并记录原因和日期。
- 已退役题目可以保留在正式资源中，以便新环境重建历史引用。

导入器发现数据库中已有相同 ID 时：

- 所有核心内容完全相同且状态相同：视为幂等导入，可以跳过。
- `title`、`surface`、`solution` 和 `key_facts` 完全相同但状态不同：允许只通过 M3 完整快照保存变更状态。
- 任一核心内容不同：抛出 `PuzzleCatalogError`，不得覆盖。

M4 不删除数据库中未出现在当前资源里的题目，也不自动禁用它们。

## 10. 正式题库 JSON 格式版本 1

### 10.1 文件编码与顶层结构

`var/catalog/catalog.v1.json` 必须是 UTF-8、无 BOM 的 JSON 文件，并以换行结束。顶层精确包含：

```json
{
  "catalog_version": 1,
  "puzzles": []
}
```

这里的空数组只说明结构，不是合法正式题库内容。正式资源必须满足第 4.3 节的数量要求。

规则：

- `catalog_version` 必须满足 `type(value) is int` 且精确为 `1`，布尔值不接受。
- `puzzles` 必须是 JSON 数组。
- 顶层缺少字段、存在额外字段或重复键均失败。
- 不支持注释、尾随逗号、JSON Lines、YAML 或其他格式。

### 10.2 题目对象

每项题目对象精确包含：

```json
{
  "id": "ts-0001",
  "title": "示意标题，不是正式题目",
  "surface": "示意题面，不是正式题目",
  "solution": "示意题底，不是正式题目",
  "key_facts": ["示意核心事实，不是正式题目"],
  "status": "ENABLED",
  "provenance": {
    "source_kind": "ORIGINAL",
    "source_reference": "internal-review-reference",
    "adaptation_note": null
  }
}
```

该对象只用于说明字段，不得复制为正式内容或测试占位题目。

字段规则：

- `id`、`title`、`surface` 和 `solution` 必须满足 `type(value) is str` 且去除首尾空白后非空；不得静默修剪。
- `id` 必须符合第 8.2 节格式。
- `key_facts` 必须是非空 JSON 数组，每项必须是非空普通字符串；转换为元组后交由 M2 `Puzzle` 校验。
- `status` 必须是 `ENABLED` 或 `DISABLED`，通过 `PuzzleStatus` 构造。
- 缺少字段、额外字段或重复键失败。
- 正式资源中不得出现重复 ID，且顺序必须严格升序。
- 不增加标签、难度、推荐权重、模型期望答案或测试专用字段。

### 10.3 来源对象

`provenance` 精确包含：

- `source_kind`：第 4.1 节四个描述性标签之一。
- `source_reference`：非空普通字符串，引用原始来源、内部原创记录或文档引用。
- `adaptation_note`：没有改编时为 JSON `null`；发生改编时为非空普通字符串。

缺少字段、额外字段、重复键、空白字符串或未知 `source_kind` 均失败。来源对象只保存在受版本控制的正式题库和审查记录中，不传给 `PuzzleRepository`，也不得复制到 `docs/`、源码、测试或日志；`docs/M4_CONTENT_REVIEW.md` 只能记录必要的脱敏引用和结论。

### 10.4 严格解析

解析器必须：

- 使用标准库 `json`。
- 检测所有层级的重复对象键，不能接受 `json.loads` 默认的后值覆盖行为。
- 先完整解析和校验全部对象，再返回任何 `Puzzle`。
- 使用 M2 公共构造器完成最终领域校验。
- 返回按资源顺序排列的 `tuple[Puzzle, ...]`，不暴露可变列表或原始字典。
- 非法 UTF-8、BOM、非法 JSON、版本不支持或契约不匹配时明确失败，不返回部分题库。

## 11. 公共入口与失败契约

`catalog/importer.py` 的公共签名固定为：

```python
class PuzzleCatalogError(ValueError):
    ...


def parse_puzzle_catalog_document(*, document: bytes) -> tuple[Puzzle, ...]:
    ...


def load_puzzle_catalog(*, catalog_path: str | Path) -> tuple[Puzzle, ...]:
    ...


def import_puzzle_catalog(
    *,
    catalog_path: str | Path,
    database_path: str | Path,
) -> None:
    ...
```

`catalog/__init__.py` 只导出：

- `PuzzleCatalogError`
- `parse_puzzle_catalog_document`
- `load_puzzle_catalog`
- `import_puzzle_catalog`

失败边界：

- `parse_puzzle_catalog_document` 只接受满足 `type(document) is bytes` 的内存文档；其他类型抛出 `PuzzleCatalogError`，不转换输入。
- 该纯解析入口负责 UTF-8 解码、BOM 拒绝、JSON 和全部版本 1 契约校验，不读取文件、不访问网络且不产生持久化副作用。
- `load_puzzle_catalog` 只读取 `catalog_path` 明确指定的现有本地普通文件原始字节并调用 `parse_puzzle_catalog_document`，不得复制另一套解析规则。
- `catalog_path` 只接受满足 `type(value) is str` 的字符串或 `isinstance(value, Path)` 的路径对象；其他类型抛出 `PuzzleCatalogError`，不执行隐式字符串转换。
- 空白字符串、URL、URI、缺失路径和目录均抛出 `PuzzleCatalogError`，不修剪、不创建目录或文件，也不尝试远程访问。相对路径严格按调用进程当前工作目录解析。
- 禁止的 URL 或 URI 至少包括带 `://` 的 scheme 形式和 `file:` 形式；Windows 盘符绝对路径不是 URI，不得因此被误拒绝。
- 读取现有本地文件时发生的权限、设备或其他 `OSError` 原样暴露；不得转换为成功、空题库或默认题目。
- 资源编码、JSON、版本、字段、顺序、来源、正式 ID、数量和身份冲突错误抛出 `PuzzleCatalogError`。
- M2 `Puzzle` 构造失败对外归入 `PuzzleCatalogError`，保留异常链，但不得把完整题底或核心事实写入消息。
- 数据库路径、未初始化 Schema、SQLite 连接、约束和磁盘错误保留 M3 或 SQLite 的真实异常边界，不转换成成功或 `PuzzleCatalogError`。
- 不捕获宽泛异常后返回空题库、部分题库、默认题目或成功状态。
- 错误消息和命令输出不得包含完整 `solution`、完整 `key_facts` 或外部来源隐私。

`parse_puzzle_catalog_document` 接受内存字节只为冻结确定性格式校验和提供公共测试入口，不授予发布其中内容的能力。M4 只支持通过 `catalog_path` 显式指定现有本地 JSON 文件，不接受 URL、文件对象或目录，不发现目录中的其他题库，也不把调用方直接提供的 `bytes` 导入 SQLite。内容冻结后的正式运行题库位置固定为 `var/catalog/catalog.v1.json`；路径参数用于显式选择并验证该文件，不授予其他本地文件正式题库身份，也不要求生产代码依赖目录名判断内容身份。正式 CLI 只能在脱敏审查记录证明文件内全部候选已经 `APPROVED`、预留引用已经取得正式 ID 身份并完成本地内容冻结后运行；这是操作与验收门禁，不要求解析器读取 Git 文档或私有审查记录。测试可以在 pytest `tmp_path` 中创建不含真实题目的合成文件验证相同公共入口。

## 12. 显式 SQLite 导入契约

### 12.1 命令行入口

显式导入命令固定为：

```powershell
conda run -n web --cwd backend/src python -m turtle_soup.catalog --catalog-path ../../var/catalog/catalog.v1.json --database-path ../../var/turtle_soup.sqlite3
```

约束：

- `--catalog-path` 必填，并且正式运行时必须显式传入从 `backend/src` 解析到 `var/catalog/catalog.v1.json` 的 `../../var/catalog/catalog.v1.json`。
- `--database-path` 必填。
- CLI 不读取环境变量、默认路径或当前目录中的其他文件来猜测题库位置。
- 数据库及 M3 Schema 必须由宿主事先显式初始化。
- M4 不隐式调用 `initialize_sqlite_database`，不创建父目录或替代数据库。
- 模块导入、应用启动和测试收集不得自动导入题库。
- 成功返回进程状态 `0`，标准输出只写入固定摘要 `puzzle catalog import completed`，不报告数量或打印题目内容。
- 参数、资源、身份预检或数据库失败返回非零状态，不伪造成功。
- `--catalog-path` 只允许本地文件语义；不增加 URL、远程来源、目录发现、覆盖冲突或清空数据库选项。

### 12.2 导入步骤

`import_puzzle_catalog` 必须按以下顺序执行：

1. 使用 `load_puzzle_catalog` 完整读取并校验 `catalog_path` 指向的本地 JSON。
2. 构造全部 M2 `Puzzle`。
3. 创建现有 M3 `SQLitePuzzleRepository`；构造器不得初始化数据库。
4. 对全部正式 ID 调用 `get` 完成身份冲突预检。
5. 任一冲突存在时，在任何 `save` 前失败。
6. 预检全部通过后，按 ID 顺序对新增或允许状态变化的题目调用 `save`。
7. 完全相同的已有题目可以跳过。

不得直接使用 `sqlite3`、导入 M3 私有函数、访问 M3 内部连接或复制 M3 UPSERT SQL。

### 12.3 幂等和失败原子性

- 在数据库状态不变时重复导入必须幂等，不增加重复题目或改变内容。
- 资源校验或身份预检失败时必须零写入。
- 每道题的保存原子性由 M3 `PuzzleRepository.save` 保证。
- M3 没有冻结批量事务 Port，因此 M4 不宣称整个题库跨多次 `save` 全有或全无。
- 数据库在写入阶段失败时，已经成功提交的前序题目可能保留；必须立即失败并如实报告，不执行隐藏补偿、直接 SQL 回滚、自动重试或伪造完整导入。

需要真正的跨题库批量事务时，必须停止并由新的已批准 SDD 设计公共 Port，不能在 M4 私自绕过 M3。

## 13. TDD 契约测试

`backend/tests/catalog/test_catalog.py` 至少覆盖以下确定性语义。

### 13.1 资源解析与本地加载

- 通过公共 `parse_puzzle_catalog_document` 解析的合成文档能够生成按 ID 升序的 `tuple[Puzzle, ...]`。
- 通过公共 `load_puzzle_catalog` 从 pytest `tmp_path` 中的合成本地 JSON 加载相同结果。
- 所有合成题目由 M2 公共构造器创建，字段与测试 JSON 精确一致。
- 合法 Unicode、元素顺序和来源元数据校验正常。
- 非法 UTF-8、BOM、非法 JSON、重复键、错误版本、空题库和少于 8 道启用题目失败。
- 顶层、题目和来源对象的缺失字段、额外字段、错误类型和空白值失败。
- 重复 ID、ID 格式错误、非升序和未知枚举失败。
- 非数组或非法 `key_facts` 失败。
- `adaptation_note` 只接受 `null` 或非空普通字符串。
- 解析失败不返回部分结果，异常消息不包含完整题底或核心事实。
- `catalog_path` 的错误类型、空白字符串、URL、URI、缺失路径和目录明确失败；合法 Windows 盘符路径不被误判为 URI。
- 本地文件权限或设备读取错误不触发远程访问、fallback、默认内容或自动创建。

格式和失败路径测试必须把纯合成 JSON 编码为字节并通过公共 `parse_puzzle_catalog_document` 验证；文件读取测试把同类合成内容写入 pytest `tmp_path` 并通过公共 `load_puzzle_catalog` 验证。必须覆盖非 `bytes` 输入明确失败。测试内容不得复制、改写、概述或暗示任何真实候选题的标题、题面、题底或核心事实，不得当作正式题库或来源证据，也不得反射私有解析函数或锁定内部文件拓扑。

### 13.2 身份与导入

- 使用 pytest `tmp_path` 下的合成本地题库文件和由 M3 初始化的真实 SQLite 文件完成导入。
- 导入后通过 `SQLitePuzzleRepository.get` 逐字段验证完整往返。
- `list_enabled` 的结果与合成测试资源中的启用题目一致，并保持 M3 的 ID 排序语义。
- 完全相同资源重复导入不增加记录或改变内容。
- 只改变状态的相同 ID 可以保存。
- 相同 ID 的标题、题面、题底或核心事实不同均在任何写入前失败。
- 数据库中额外题目不被删除或自动禁用。
- 未初始化数据库、非法路径和真实 SQLite 错误明确失败。
- 资源校验失败和身份预检失败时真实数据库零写入。
- 测试不得使用内存字典、fake Repository 或 `:memory:` 代替真实导入证据。

### 13.3 CLI 与副作用

- CLI 契约测试必须以 `backend/src` 为子进程工作目录，并显式传入从该目录可解析的 pytest 临时合成题库路径和临时数据库路径，验证与固定命令相同的包导入前提。
- 缺少 `--catalog-path` 或 `--database-path` 均失败。
- `--catalog-path` 为 URL、URI、缺失文件或目录时失败，不访问网络。
- 成功导入退出状态为 `0`，标准输出精确为固定摘要 `puzzle catalog import completed`，且不含题底和核心事实。
- 参数、资源或数据库失败时退出状态非零且不打印敏感内容。
- 导入模块和应用模块不会自动创建数据库或写入题目。
- 测试收集和模块导入不要求 `var/catalog/catalog.v1.json` 存在，也不读取正式题库。
- 正式题库和私有内容审查材料不出现在测试夹具、`backend/`、`frontend/`、前端构建产物或浏览器可访问静态资源中。

测试不得修改、删除或放宽 M1-M3 冻结测试，也不得通过生产测试分支、私有 SQL、隐藏 fallback 或降低资源校验使测试变绿。

## 14. 人工内容与来源验收

自动化测试绿色之前和之后，都不能替代以下逐题人工证据：

- 题目来源记录已按第 4 节登记。
- 内容质量审查表逐项完成。
- 获准审核者已按 `docs/M4_CONTENT_REVIEW.md` 的证据引用直接检查 `var/catalog/private_review/` 中对应的完整内容工作稿和私有内容审查材料；公开报告只记录结论和限制。
- 用户明确批准正式 ID、最终内容和启用状态。
- `var/catalog/catalog.v1.json` 与脱敏的 `docs/M4_CONTENT_REVIEW.md` 正式 ID 集合完全一致。
- 从 `backend/src` 使用固定正式 CLI 命令成功解析并导入正式题库，且通过 M3 公共 Repository 核对全部正式 ID、状态和字段往返。
- `docs/M4_CONTENT_REVIEW.md` 记录题库文件 SHA-256、题目总数、启用数、验收日期和用户逐题批准；只记录脱敏证据引用，不记录完整题目内容或私有内容审查原文。
- `git check-ignore` 必须证明正式题库和审查目录未被 Git 排除，`git ls-files` 必须证明获准文件已被跟踪；`AGENTS.md` 和 `docs/` Markdown 同样不得被 ignore。
- Docker 构建上下文检查证明 `var/` 未进入上下文；不得通过复制、构建参数或其他路径重新引入。
- 对 Git 已跟踪文件、全部未跟踪候选和暂存内容执行内容位置扫描，确认完整题面、题底、核心事实和审查原文只存在于获准的 `var/catalog/` 文件，不存在额外副本。

发现审查记录与资源不一致、逐题批准证据缺失、私有文件未被正确 ignore、真实内容进入上传候选或内容为了模型测试而定制时，M4 不得冻结。

## 15. M4 明确排除范围

M4 不实现或决定：

- 网络爬虫、运行时下载、远程同步或第三方题库 API。
- 模型自动生成、翻译、改写或内容审核。
- 玩家自定义题库、文件上传、目录扫描或 URL 导入。获准操作员通过必填 `--catalog-path` 指定唯一现有本地文件不属于玩家自定义题库。
- 随机选择、推荐、轮换、防重复、难度、标签或分类。
- 游戏开始、提问、猜测、放弃或状态转换。
- Agently、Prompt、结构化模型输出或 M5 语义适配器。
- 使用数据库测试声称模型判断正确。
- FastAPI 路由、HTTP DTO、前端页面或公开题底投影。
- 修改 M2 领域契约或 M3 Repository/SQLite Schema。
- 删除题目、批量事务、迁移、管理后台、审计数据库或定时任务。

## 16. 实施与验收顺序

M4 必须分阶段进行：

1. 本规格独立复核并由用户批准。
2. 用户单独批准候选内容获取范围。
3. 先在 `var/catalog/private_review/` 保存并直接复核完整内容工作稿和内容审查材料；在 `docs/M4_CONTENT_REVIEW.md` 只追加脱敏证据引用和门禁结论，完成用户逐题批准。
4. 将预冻结工作稿整理为只包含获准正式题目的 `var/catalog/catalog.v1.json`，确认所有预留引用均已取得正式 ID 身份，并验证 Git 跟踪与 Docker 排除边界；在此之前不得加载、导入或冻结该工作稿。
5. 先编写 M4 契约测试并形成有效红灯。
6. 实现满足规格的最小 catalog 模块和 CLI。
7. 运行 M4 测试、M1-M3 回归和全量检查。
8. 独立复核规格与审查文档、代码、全部未跟踪文件、Git 差异、正式题库及审查材料的跟踪状态、真实 SQLite 和人工证据；公开报告中不得复述真实题目内容。
9. 用户确认规格、实施和内容冻结后，`AGENTS.md`、`docs/`、源码、合成测试、必要配置及获准的 `var/` 文件一起提交并上传。

内容策展和编码可以由不同实施者完成。编码实施者不得自行搜索、生成、读取或替换真实题目，也不得把正式内容复制进测试；只根据格式契约和纯合成数据实现代码。正式题库导入的人工验收由获准访问 `var/catalog/` 的验收者执行。

开始任何内容或代码实施前必须重新运行上一冻结基线：

```powershell
conda run -n web python -m pytest backend/tests
conda run -n web python -m ruff check backend
conda run -n web python -m pip check
pnpm --dir frontend test
pnpm --dir frontend lint
pnpm --dir frontend build
```

实施完成后至少运行：

```powershell
conda run -n web python -m pytest backend/tests/catalog
conda run -n web python -m pytest backend/tests
conda run -n web python -m ruff check backend
conda run -n web python -m pip check
pnpm --dir frontend test
pnpm --dir frontend lint
pnpm --dir frontend build
git status --short --branch --untracked-files=all
git diff
git diff --check
git diff --cached
git ls-files --others --exclude-standard
git status --short --untracked-files=all -- var/catalog
git check-ignore var/catalog/catalog.v1.json var/catalog/private_review/content_review.v1.md
git ls-files var/catalog/catalog.v1.json var/catalog/private_review/content_review.v1.md
git ls-files AGENTS.md docs/M4_PUZZLE_CATALOG.md docs/M4_CONTENT_REVIEW.md docs/MODULE_IMPLEMENTATION_AND_SDD_TDD_ACCEPTANCE_PLAN.md
```

还必须单独读取全部未跟踪文件、规则与规格文档，以及明确路径下受版本控制的正式题库和审查材料；对所有版本控制候选文件执行密钥扫描，并确认完整题面、题底和核心事实只存在于获准的 `var/catalog/catalog.v1.json`、`var/catalog/private_review/` 和 SQLite 基线中，没有副本进入 Docker 构建上下文、前端、日志、`.agently/`、测试夹具、缓存或构建产物。复核必须使用明确路径检查文件存在性、证据映射、格式、哈希、Git 跟踪状态、Docker 排除状态和真实导入结果。对外报告仍只逐项报告结论和限制，不复述完整题目、题底或核心事实。

## 17. M4 冻结范围

M4 使用两个互不替代的冻结边界。

进入 Git 并可以上传的规格与实施冻结包括：

- `AGENTS.md`、`docs/M4_PUZZLE_CATALOG.md`、脱敏的 `docs/M4_CONTENT_REVIEW.md` 和相关模块计划。
- 题库来源记录政策。
- 内容审查和用户逐题批准门禁，以及取消 M4 人工盲测后的明确证据限制。
- 正式 ID、状态、更新、退役和同 ID 冲突规则。
- 正式题库 JSON 版本 1 的结构、严格校验和来源元数据契约。
- M4 公共本地加载与显式导入入口及失败边界。
- 真实 SQLite 导入、幂等、预检和非批量原子性语义。
- 只使用合成内容的 M4 自动化契约测试。
- Git、GitHub、Docker、测试和日志不得包含正式题库完整内容或私有内容审查原文的隐私边界。

必须进入 Git 冻结提交的内容证据包括：

- `var/catalog/catalog.v1.json` 的正式题库内容。
- `var/catalog/private_review/` 中支持内容审查结论的完整工作稿与记录。
- 使用固定 CLI 命令完成的本地真实 SQLite 导入与逐字段核对证据。

内容冻结以 Git 提交和题库 SHA-256 共同固定。正式题库或对应审查材料缺失、题库哈希变化、证据映射失效，或者与 `docs/M4_CONTENT_REVIEW.md` 的冻结记录不匹配时视为基线变化，必须重新验收；不得从测试夹具、网络或模型生成结果补齐或替换正式内容。

后续模块不得修改正式题目的核心内容、复用 ID、放宽内容门禁或改写 M4 契约测试。需要新增题目时必须遵循同一获取和审查流程；需要改变冻结格式或公共入口时必须停止并取得用户批准。

只有正式内容冻结已经由用户确认、且 Git 规格、内容与实施冻结已经提交并上传后，才能开始 M5。M5 可以通过规格冻结的显式本地评测入口读取 `var/catalog/catalog.v1.json`，也可以在后续运行时通过 SQLite 使用获准题目，但不得反向修改题库以迎合模型输出。
