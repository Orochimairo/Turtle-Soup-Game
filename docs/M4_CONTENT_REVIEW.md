# M4 题目候选与内容审查记录

## 1. 文档用途与边界

本文档是 `docs/M4_PUZZLE_CATALOG.md` 定义的 M4 策展证据记录，用于保存候选登记、追加式门禁历史、内容待办和人工内容安全预审结论。

本文档当前已经记录 30 道候选的逐题 `APPROVED` 转换：

- `ts-0001` 至 `ts-0030` 已按 `docs/M4_PUZZLE_CATALOG.md` §8.2 取得正式 ID 身份。
- 候选状态仍不映射为 M2 `PuzzleStatus`。
- 本文档不包含可直接导入的完整 `surface`、`solution` 或 `key_facts`。
- 当前 M4 验收状态如下：
  - 编码前内容冻结复核已通过。
  - M4 catalog 实现独立复核已通过。
  - 本地真实 SQLite 导入与幂等验收已通过。
  - 尚待 M4 最终冻结提交和上传；在此之前不得开始 M5。
- `REJECTED` 候选不进入本批次后续流程；重新提出时必须使用新的临时候选引用。

本文档属于可上传的脱敏审查记录，只保存候选引用、候选名称、非剧透内容分类、状态、日期、非敏感证据引用和结论。完整题面、题底、核心事实、完整内容工作稿和私有内容审查材料只允许保存在被忽略的 `var/catalog/private_review/`，不得复制到本文档。获准审核者必须直接检查私有材料；本文档中的摘要、结论或文件哈希不能替代该复核。

## 2. 批次登记

| 字段 | 记录 |
|---|---|
| 批次引用 | `BATCH-DOCX30-2026-08-26` |
| 登记日期 | `2026-08-26` |
| 计划候选数 | 30 |
| 实际登记数 | 30 |
| 目标语言 | 简体中文 |
| 目标受众 | 能接受非写实悬疑、死亡或犯罪背景的成年用户 |
| 拟定来源组合 | 本批 30 题均暂拟为 `PERMISSION`；不得改记为 `ORIGINAL` |
| 批次目的 | 从用户提供的整理改写文档中登记候选，为 M4 首批正式题库筛选至少 8 道来源清晰、推理公平且安全边界合格的题目 |
| 推理结构覆盖目标 | 因果误导、身份误导、观察视角、日常语义歧义、时间或顺序误导、科幻设定、家庭关系与危险场景 |

### 2.1 首轮内容安全边界

本节记录 `2026-08-26` 首轮安全预审实际采用的边界，用于解释第 5 节已经发生的追加式状态转换。该历史边界不得删除或改写，但已由第 7 节批准的新选题范围取代，不再用于排除新复议候选。

本批次允许非写实的悬疑、死亡或犯罪背景，但执行以下硬性排除：

- 未成年人死亡、严重伤害、被培养为伤害对象或成为暴力核心受害者。
- 自杀、自伤或明知致命的自毁行为成为核心反转，尤其是带有美化、表演化或模仿风险的内容。
- 动物虐杀或动物尸体作为主要恐怖机关。
- 酷刑、剥皮、肢解、取下人体器官、尸体侮辱或以血肉细节作为主要谜底。
- 以精神疾病、产后精神障碍、幻觉或住院患者为怪物化、危险化或猎奇反转。
- 露骨色情、仇恨内容、现实受害者娱乐化或其他与 `docs/M4_PUZZLE_CATALOG.md` 冲突的内容。

“未触发硬性排除”只表示可以等待后续门禁，不等于已完成 `CONTENT_REVIEWED`。正式内容质量审查仍须在候选登记之后进行。

## 3. 来源记录

### 3.1 来源记录索引

| 记录引用 | 内容 |
|---|---|
| `SOURCE-DOCX-2026-08-26` | 用户提供的 `海龟汤题库_30题_整理改写版.docx`；SHA-256：`30B328AEC6AAB5AE83BB2179BF887AE4F71DC4A1FC6917490269D434BA6B248D`。文档说明其题目顺序、标题和核心故事设定参考游侠网页面，题面和题底经过重新组织。 |
| `SOURCE-WEB-ALI213` | 文档列明的参考页面：`https://gl.ali213.net/html/2025-5/1643509.html`。该页面是题目改写所参考的原始来源引用，仅作来源记录。 |
| `USER-PERMISSION-DECLARATION-2026-08-26` | 用户在本项目任务记录中声明：拥有该文档中题目的复制、改编及项目内分发授权。该声明作为来源记录登记，不构成独立权利门禁。 |
| `USER-SCOPE-EXPANSION-2026-08-26` | 用户在本项目任务记录中明确要求：首轮设置限制的 17 道题也要纳入选题范围，并修改选题范围。 |
| `SAFETY-PRESCREEN-2026-08-26` | 依据本文件第 2.1 节和 `docs/M4_PUZZLE_CATALOG.md` 第 6.2 节，对 30 个候选的题面与题底进行的人工安全预审。 |

### 3.2 来源记录结论

2026-08-26 由用户决定移除权利门禁：题目来源只作普通记录登记，不再要求外部权利证据，也不再使用 `RIGHTS_VERIFIED` 状态。30 个候选的题目内容来自用户提供的整理改写文档；按照 2026-08-27 修订后的门禁，内容是否进入正式题库由内容审查和用户逐题批准决定。

第 5 节与第 7.3 节已登记的追加式历史保持原样，不因本决定被改写或删除；其中“权利证据待补”等说明属于当时门禁下的历史记录。

## 4. 候选登记与安全预审

以下分类只用于区分候选的叙事类型和审查风险，不描述谜底、核心反转、具体伤害方式或关键因果关系。完整审查依据只保存在 `var/catalog/private_review/`。

| 临时候选引用 | 候选名称 | 非剧透内容分类 | 脱敏预审结论 | 登记时状态 |
|---|---|---|---|---|
| `DOCX30-C001` | 电梯 | 危险场景、空间误导 | 未触发首轮硬性排除；仍需复核推理公平性。 | `DISCOVERED` |
| `DOCX30-C002` | 黑猫 | 动物元素、因果误导、犯罪背景 | 未触发首轮硬性排除；仍需复核暴力表达。 | `DISCOVERED` |
| `DOCX30-C003` | 笑容（父亲） | 家庭关系、死亡背景、观察误导 | 未触发首轮硬性排除；仍需复核情绪强度。 | `DISCOVERED` |
| `DOCX30-C004` | 洗头 | 科幻设定、意外事件、身份误导 | 未触发首轮硬性排除；仍需复核设定公平性。 | `DISCOVERED` |
| `DOCX30-C005` | 女明星 | 未成年人、身体伤害、身份关系 | 触发首轮未成年人及身体伤害边界。 | `REJECTED` |
| `DOCX30-C006` | 睡好了 | 身体恐怖、死亡背景、视觉误导 | 触发首轮身体恐怖边界。 | `REJECTED` |
| `DOCX30-C007` | 手术 | 身体差异、医疗风险、自我伤害 | 触发首轮污名化及自我伤害边界。 | `REJECTED` |
| `DOCX30-C008` | 演出 | 表演场景、自我伤害、道具误导 | 触发首轮自我伤害美化风险边界。 | `REJECTED` |
| `DOCX30-C009` | 偏心 | 家庭关系、健康风险、因果误导 | 未触发首轮硬性排除；仍需复核设定公平性。 | `DISCOVERED` |
| `DOCX30-C010` | 笑容（柜子） | 身体恐怖、身份视角、犯罪背景 | 触发首轮身体恐怖边界。 | `REJECTED` |
| `DOCX30-C011` | 红色 | 暴力、视觉意象、犯罪背景 | 触发首轮血腥表达及模仿风险边界。 | `REJECTED` |
| `DOCX30-C012` | 听话 | 未成年人、自我伤害、危险场景 | 触发首轮未成年人及自我伤害边界。 | `REJECTED` |
| `DOCX30-C013` | 红衣服 | 群体暴力、身体恐怖、语言误导 | 触发首轮身体恐怖及群体伤害边界。 | `REJECTED` |
| `DOCX30-C014` | 凶杀 | 家庭危险、动物元素、行为误导 | 未触发首轮硬性排除；仍需复核情绪强度。 | `DISCOVERED` |
| `DOCX30-C015` | 狗 | 动物伤害、死亡背景、感官误导 | 触发首轮动物伤害边界。 | `REJECTED` |
| `DOCX30-C016` | 三弟 | 家庭关系、身体恐怖、行为误导 | 触发首轮身体恐怖边界。 | `REJECTED` |
| `DOCX30-C017` | 暗恋我的男同事 | 跟踪风险、位置隐私、行为误导 | 未触发首轮硬性排除；仍需复核针对性暴力风险。 | `DISCOVERED` |
| `DOCX30-C018` | 咚咚咚 | 未成年人遇险、死亡背景、声音误导 | 触发首轮未成年人及尸体不当呈现边界。 | `REJECTED` |
| `DOCX30-C019` | 交换照片 | 网络互动、入侵风险、观察误导 | 未触发首轮硬性排除；仍需复核逻辑闭合性。 | `DISCOVERED` |
| `DOCX30-C020` | 情人 | 未成年人、身体恐怖、家庭关系 | 触发首轮未成年人及血腥表达边界。 | `REJECTED` |
| `DOCX30-C021` | 找到你了 | 追逐风险、藏匿场景、声音误导 | 未触发首轮硬性排除；仍需复核问答稳定性。 | `DISCOVERED` |
| `DOCX30-C022` | 半瓶香水 | 丧亲、精神健康、身份误导 | 触发首轮精神健康污名化边界。 | `REJECTED` |
| `DOCX30-C023` | 塞 | 日常场景、语义歧义 | 未触发首轮硬性排除；仍需复核解释唯一性。 | `DISCOVERED` |
| `DOCX30-C024` | 1237 | 家庭关系、疾病背景、顺序误导 | 未触发首轮硬性排除；仍需复核情绪强度与多解性。 | `DISCOVERED` |
| `DOCX30-C025` | 灰姑娘 | 黑暗童话、连续犯罪、身体恐怖 | 触发首轮酷刑及尸体不当呈现边界。 | `REJECTED` |
| `DOCX30-C026` | 不要相信一号 | 科幻设定、身份误导、记忆问题 | 未触发首轮硬性排除；仍需复核角色与时间线。 | `DISCOVERED` |
| `DOCX30-C027` | 黑暗与绝望 | 身体伤害、连续犯罪、感官误导 | 触发首轮人体器官伤害边界。 | `REJECTED` |
| `DOCX30-C028` | 拔萝卜 | 精神健康、身体伤害、语义误导 | 触发首轮精神健康污名化及血腥表达边界。 | `REJECTED` |
| `DOCX30-C029` | 怀孕 | 产后精神健康、家庭暴力、未成年人 | 触发首轮精神健康污名化及未成年人伤害边界。 | `REJECTED` |
| `DOCX30-C030` | 妈妈 | 家庭关系、成长与丧亲、时间顺序 | 未触发首轮硬性排除；仍需复核多解性。 | `DISCOVERED` |

## 5. 追加式门禁历史

下表是当前完整历史。任何后续转换只能追加新行，不得修改或删除这些记录。

| 临时候选引用 | 日期 | 转入状态 | 证据引用 | 说明 |
|---|---|---|---|---|
| `DOCX30-C001` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记；权利证据待补。 |
| `DOCX30-C002` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记；权利证据待补。 |
| `DOCX30-C003` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记；权利证据待补。 |
| `DOCX30-C004` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记；权利证据待补。 |
| `DOCX30-C005` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记。 |
| `DOCX30-C005` | `2026-08-26` | `REJECTED` | `SAFETY-PRESCREEN-2026-08-26` | 触发首轮未成年人及身体伤害边界。 |
| `DOCX30-C006` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记。 |
| `DOCX30-C006` | `2026-08-26` | `REJECTED` | `SAFETY-PRESCREEN-2026-08-26` | 触发首轮身体恐怖边界。 |
| `DOCX30-C007` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记。 |
| `DOCX30-C007` | `2026-08-26` | `REJECTED` | `SAFETY-PRESCREEN-2026-08-26` | 触发首轮污名化及自我伤害边界。 |
| `DOCX30-C008` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记。 |
| `DOCX30-C008` | `2026-08-26` | `REJECTED` | `SAFETY-PRESCREEN-2026-08-26` | 触发首轮自我伤害美化风险边界。 |
| `DOCX30-C009` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记；权利证据待补。 |
| `DOCX30-C010` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记。 |
| `DOCX30-C010` | `2026-08-26` | `REJECTED` | `SAFETY-PRESCREEN-2026-08-26` | 触发首轮身体恐怖边界。 |
| `DOCX30-C011` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记。 |
| `DOCX30-C011` | `2026-08-26` | `REJECTED` | `SAFETY-PRESCREEN-2026-08-26` | 触发首轮血腥表达及模仿风险边界。 |
| `DOCX30-C012` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记。 |
| `DOCX30-C012` | `2026-08-26` | `REJECTED` | `SAFETY-PRESCREEN-2026-08-26` | 触发首轮未成年人及自我伤害边界。 |
| `DOCX30-C013` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记。 |
| `DOCX30-C013` | `2026-08-26` | `REJECTED` | `SAFETY-PRESCREEN-2026-08-26` | 触发首轮身体恐怖及群体伤害边界。 |
| `DOCX30-C014` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记；权利证据待补。 |
| `DOCX30-C015` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记。 |
| `DOCX30-C015` | `2026-08-26` | `REJECTED` | `SAFETY-PRESCREEN-2026-08-26` | 触发首轮动物伤害边界。 |
| `DOCX30-C016` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记。 |
| `DOCX30-C016` | `2026-08-26` | `REJECTED` | `SAFETY-PRESCREEN-2026-08-26` | 触发首轮身体恐怖边界。 |
| `DOCX30-C017` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记；权利证据待补。 |
| `DOCX30-C018` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记。 |
| `DOCX30-C018` | `2026-08-26` | `REJECTED` | `SAFETY-PRESCREEN-2026-08-26` | 触发首轮未成年人及尸体不当呈现边界。 |
| `DOCX30-C019` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记；权利证据待补。 |
| `DOCX30-C020` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记。 |
| `DOCX30-C020` | `2026-08-26` | `REJECTED` | `SAFETY-PRESCREEN-2026-08-26` | 触发首轮未成年人及血腥表达边界。 |
| `DOCX30-C021` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记；权利证据待补。 |
| `DOCX30-C022` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记。 |
| `DOCX30-C022` | `2026-08-26` | `REJECTED` | `SAFETY-PRESCREEN-2026-08-26` | 触发首轮精神健康污名化边界。 |
| `DOCX30-C023` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记；权利证据待补。 |
| `DOCX30-C024` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记；权利证据待补。 |
| `DOCX30-C025` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记。 |
| `DOCX30-C025` | `2026-08-26` | `REJECTED` | `SAFETY-PRESCREEN-2026-08-26` | 触发首轮酷刑及尸体不当呈现边界。 |
| `DOCX30-C026` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记；权利证据待补。 |
| `DOCX30-C027` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记。 |
| `DOCX30-C027` | `2026-08-26` | `REJECTED` | `SAFETY-PRESCREEN-2026-08-26` | 触发首轮人体器官伤害边界。 |
| `DOCX30-C028` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记。 |
| `DOCX30-C028` | `2026-08-26` | `REJECTED` | `SAFETY-PRESCREEN-2026-08-26` | 触发首轮精神健康污名化及血腥表达边界。 |
| `DOCX30-C029` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记。 |
| `DOCX30-C029` | `2026-08-26` | `REJECTED` | `SAFETY-PRESCREEN-2026-08-26` | 触发首轮精神健康污名化及未成年人伤害边界。 |
| `DOCX30-C030` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-PERMISSION-DECLARATION-2026-08-26` | 完成候选登记；权利证据待补。 |
| `DOCX30-C001` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0001` | 内容质量审查通过。 |
| `DOCX30-C002` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0002` | 内容质量审查通过。 |
| `DOCX30-C003` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0003` | 内容质量审查通过。 |
| `DOCX30-C004` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0004` | 内容质量审查通过。 |
| `DOCX30-C009` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0009` | 内容质量审查通过。 |
| `DOCX30-C014` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0014` | 内容质量审查通过。 |
| `DOCX30-C017` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0017` | 内容质量审查通过。 |
| `DOCX30-C019` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0019` | 内容质量审查通过。 |
| `DOCX30-C021` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0021` | 内容质量审查通过。 |
| `DOCX30-C023` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0023` | 内容质量审查通过。 |
| `DOCX30-C024` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0024` | 内容质量审查通过。 |
| `DOCX30-C026` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0026` | 内容质量审查通过。 |
| `DOCX30-C030` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0030` | 内容质量审查通过。 |
| `DOCX30-C001` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-C002` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-C003` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-C004` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-C009` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-C014` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-C017` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-C019` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-C021` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-C023` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-C024` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-C026` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-C030` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |

## 6. 首轮批次结果

| 结果 | 数量 | 临时候选引用 |
|---|---:|---|
| 保留在 `DISCOVERED`，等待权利证据 | 13 | `DOCX30-C001`、`C002`、`C003`、`C004`、`C009`、`C014`、`C017`、`C019`、`C021`、`C023`、`C024`、`C026`、`C030` |
| 已转为 `REJECTED` | 17 | `DOCX30-C005`、`C006`、`C007`、`C008`、`C010`、`C011`、`C012`、`C013`、`C015`、`C016`、`C018`、`C020`、`C022`、`C025`、`C027`、`C028`、`C029` |
| `RIGHTS_VERIFIED` | 0 | 无 |
| `CONTENT_REVIEWED` | 0 | 无 |
| `BLIND_TESTED`（后于本表取消） | 0 | 无；M4 于 `2026-08-27` 取消该状态。 |
| `APPROVED` | 0 | 无 |

本节只记录首轮批次的历史结果。第 5 节的 17 条 `REJECTED` 转换保持有效且不可逆；根据 M4 追加式历史契约，这些题目只能通过第 7 节的新临时候选引用重新进入选题范围。

## 7. 复议批次与当前选题范围

### 7.1 范围变更记录

| 字段 | 记录 |
|---|---|
| 复议批次引用 | `BATCH-DOCX30-R2-2026-08-26` |
| 批准日期 | `2026-08-26` |
| 用户决定 | 首轮因安全边界被拒绝的 17 道题也纳入选题范围 |
| 新增复议候选数 | 17 |
| 批准时有效选题范围 | 原有 13 个 `DISCOVERED` 候选，加 17 个新 `DISCOVERED` 复议候选，共 30 道题 |
| 目标语言 | 简体中文 |
| 目标受众 | 年满 18 周岁、主动选择并能够接受死亡、犯罪、自伤暗示、未成年人遇险、动物死亡、身体恐怖和精神健康敏感情节的用户 |
| 拟定来源类型 | `PERMISSION` |
| 敏感内容记录 | M4 逐题记录黑暗、暴力和心理敏感内容类别，供后续模块规划时评估用户提示方式；本阶段不冻结或实施 UI/API 行为 |

“纳入选题范围”只恢复候选资格，不表示题目已经通过内容审查或用户逐题批准，也不表示必须原样采用文档中的表达。正式内容审查仍须满足 `docs/M4_PUZZLE_CATALOG.md`：

- 可以保留虚构的黑暗、死亡、犯罪、身体恐怖和心理惊悚核心设定。
- 题面不得用露骨血腥细节吸引玩家；题底只保留解释谜题所必需的敏感事实，并采用克制、非猎奇表达。
- 除 `docs/M4_PUZZLE_CATALOG.md` §6.3 对三个当前批次候选明确接受的风险外，不得美化、鼓励或提供可模仿的自杀、自伤、虐待、犯罪或伤害方法；例外题仍不得包含可操作方法、模仿性细节、直接鼓励或号召。
- 除同一节对两个当前批次候选明确接受的污名化观感风险外，不得把精神疾病、产后精神障碍、身体差异或其他群体身份本身描述为邪恶、低等或必然危险；例外题仍不得把叙事归因表述为医学事实、普遍规律或对现实群体的事实判断。
- 涉及未成年人、动物死亡、酷刑、肢解、器官伤害或尸体的题目必须逐题记录必要性、表达降敏方案和人工审查结论。
- 露骨色情、仇恨内容、现实受害者娱乐化，以及无法通过克制表达消除的鼓励伤害或歧视性内容仍不得进入正式题库。

如果降敏或去污名化必须改变题目的核心因果关系，应停止该候选并报告，不得把实质不同的新故事冒充同一候选。

### 7.2 新复议候选登记

以下新引用满足“被拒绝候选重新提出时必须使用新的临时候选引用”的冻结契约。原 `DOCX30-Cxxx` 的 `REJECTED` 历史继续保留。

| 新临时候选引用 | 对应历史候选 | 候选名称 | 进入正式内容审查前必须解决的问题 | 登记时状态 |
|---|---|---|---|---|
| `DOCX30-R2-C005` | `DOCX30-C005` | 女明星 | 执行未成年人及身体伤害高强度审查；验证降敏后推理结构是否完整。 | `DISCOVERED` |
| `DOCX30-R2-C006` | `DOCX30-C006` | 睡好了 | 移除身体恐怖的猎奇表达；验证降敏后推理结构是否完整。 | `DISCOVERED` |
| `DOCX30-R2-C007` | `DOCX30-C007` | 手术 | 消除身体差异污名化和自我伤害美化；验证内容必要性。 | `DISCOVERED` |
| `DOCX30-R2-C008` | `DOCX30-C008` | 演出 | 消除自我伤害浪漫化和模仿风险；验证内容必要性。 | `DISCOVERED` |
| `DOCX30-R2-C010` | `DOCX30-C010` | 笑容（柜子） | 移除身体恐怖细节；验证身份视角类推理是否仍然公平。 | `DISCOVERED` |
| `DOCX30-R2-C011` | `DOCX30-C011` | 红色 | 移除可模仿的暴力方法和血腥视觉；验证降敏后推理结构。 | `DISCOVERED` |
| `DOCX30-R2-C012` | `DOCX30-C012` | 听话 | 执行未成年人及自我伤害高强度审查；禁止方法性描述。 | `DISCOVERED` |
| `DOCX30-R2-C013` | `DOCX30-C013` | 红衣服 | 移除身体恐怖及群体伤害的血腥表达；验证降敏可行性。 | `DISCOVERED` |
| `DOCX30-R2-C015` | `DOCX30-C015` | 狗 | 执行动物伤害审查和内容提示评估；移除猎奇表达。 | `DISCOVERED` |
| `DOCX30-R2-C016` | `DOCX30-C016` | 三弟 | 移除身体恐怖细节并检查人物归因是否存在污名化。 | `DISCOVERED` |
| `DOCX30-R2-C018` | `DOCX30-C018` | 咚咚咚 | 执行未成年人及尸体不当呈现审查；移除娱乐化表达。 | `DISCOVERED` |
| `DOCX30-R2-C020` | `DOCX30-C020` | 情人 | 执行未成年人及身体伤害最高强度审查；验证降敏可行性。 | `DISCOVERED` |
| `DOCX30-R2-C022` | `DOCX30-C022` | 半瓶香水 | 消除丧亲与精神健康表现的危险化或污名化归因。 | `DISCOVERED` |
| `DOCX30-R2-C025` | `DOCX30-C025` | 灰姑娘 | 移除酷刑和尸体不当呈现；验证黑暗叙事的必要性。 | `DISCOVERED` |
| `DOCX30-R2-C027` | `DOCX30-C027` | 黑暗与绝望 | 移除人体器官伤害细节和残障污名化；验证推理公平性。 | `DISCOVERED` |
| `DOCX30-R2-C028` | `DOCX30-C028` | 拔萝卜 | 消除精神健康群体怪物化和血腥表达；无法降敏时停止。 | `DISCOVERED` |
| `DOCX30-R2-C029` | `DOCX30-C029` | 怀孕 | 消除产后精神健康污名化及未成年人伤害表达；无法降敏时停止。 | `DISCOVERED` |

### 7.3 复议候选追加式历史

| 新临时候选引用 | 日期 | 转入状态 | 证据引用 | 说明 |
|---|---|---|---|---|
| `DOCX30-R2-C005` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-SCOPE-EXPANSION-2026-08-26` | 用户批准重新纳入选题范围；等待权利证据和降敏审查。 |
| `DOCX30-R2-C006` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-SCOPE-EXPANSION-2026-08-26` | 用户批准重新纳入选题范围；等待权利证据和降敏审查。 |
| `DOCX30-R2-C007` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-SCOPE-EXPANSION-2026-08-26` | 用户批准重新纳入选题范围；等待权利证据和降敏审查。 |
| `DOCX30-R2-C008` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-SCOPE-EXPANSION-2026-08-26` | 用户批准重新纳入选题范围；等待权利证据和降敏审查。 |
| `DOCX30-R2-C010` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-SCOPE-EXPANSION-2026-08-26` | 用户批准重新纳入选题范围；等待权利证据和降敏审查。 |
| `DOCX30-R2-C011` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-SCOPE-EXPANSION-2026-08-26` | 用户批准重新纳入选题范围；等待权利证据和降敏审查。 |
| `DOCX30-R2-C012` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-SCOPE-EXPANSION-2026-08-26` | 用户批准重新纳入选题范围；等待权利证据和降敏审查。 |
| `DOCX30-R2-C013` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-SCOPE-EXPANSION-2026-08-26` | 用户批准重新纳入选题范围；等待权利证据和降敏审查。 |
| `DOCX30-R2-C015` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-SCOPE-EXPANSION-2026-08-26` | 用户批准重新纳入选题范围；等待权利证据和降敏审查。 |
| `DOCX30-R2-C016` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-SCOPE-EXPANSION-2026-08-26` | 用户批准重新纳入选题范围；等待权利证据和降敏审查。 |
| `DOCX30-R2-C018` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-SCOPE-EXPANSION-2026-08-26` | 用户批准重新纳入选题范围；等待权利证据和降敏审查。 |
| `DOCX30-R2-C020` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-SCOPE-EXPANSION-2026-08-26` | 用户批准重新纳入选题范围；等待权利证据和降敏审查。 |
| `DOCX30-R2-C022` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-SCOPE-EXPANSION-2026-08-26` | 用户批准重新纳入选题范围；等待权利证据和降敏审查。 |
| `DOCX30-R2-C025` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-SCOPE-EXPANSION-2026-08-26` | 用户批准重新纳入选题范围；等待权利证据和降敏审查。 |
| `DOCX30-R2-C027` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-SCOPE-EXPANSION-2026-08-26` | 用户批准重新纳入选题范围；等待权利证据和降敏审查。 |
| `DOCX30-R2-C028` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-SCOPE-EXPANSION-2026-08-26` | 用户批准重新纳入选题范围；等待权利证据和降敏审查。 |
| `DOCX30-R2-C029` | `2026-08-26` | `DISCOVERED` | `SOURCE-DOCX-2026-08-26`; `USER-SCOPE-EXPANSION-2026-08-26` | 用户批准重新纳入选题范围；等待权利证据和降敏审查。 |
| `DOCX30-R2-C005` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0005` | 内容质量审查通过。 |
| `DOCX30-R2-C006` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0006` | 内容质量审查通过。 |
| `DOCX30-R2-C007` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0007` | 内容质量审查通过。 |
| `DOCX30-R2-C010` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0010` | 内容质量审查通过。 |
| `DOCX30-R2-C011` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0011` | 内容质量审查通过。 |
| `DOCX30-R2-C012` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0012` | 内容质量审查通过。 |
| `DOCX30-R2-C013` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0013` | 内容质量审查通过。 |
| `DOCX30-R2-C015` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0015` | 内容质量审查通过。 |
| `DOCX30-R2-C016` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0016` | 内容质量审查通过。 |
| `DOCX30-R2-C018` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0018` | 内容质量审查通过。 |
| `DOCX30-R2-C020` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0020` | 内容质量审查通过。 |
| `DOCX30-R2-C022` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0022` | 内容质量审查通过。 |
| `DOCX30-R2-C025` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0025` | 内容质量审查通过。 |
| `DOCX30-R2-C027` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0027` | 内容质量审查通过。 |
| `DOCX30-R2-C008` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0008` | 依据修订后安全边界复审通过。 |
| `DOCX30-R2-C028` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0028` | 依据修订后安全边界复审通过。 |
| `DOCX30-R2-C029` | `2026-08-26` | `CONTENT_REVIEWED` | `PRIVATE-CONTENT-REVIEW-V1:ts-0029` | 依据修订后安全边界复审通过。 |
| `DOCX30-R2-C005` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-R2-C006` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-R2-C007` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-R2-C008` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-R2-C010` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-R2-C011` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-R2-C012` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-R2-C013` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-R2-C015` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-R2-C016` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-R2-C018` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-R2-C020` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-R2-C022` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-R2-C025` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-R2-C027` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-R2-C028` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |
| `DOCX30-R2-C029` | `2026-08-27` | `APPROVED` | `USER-PUZZLE-APPROVAL-2026-08-27` | 用户依据最终内容或获准复核证据逐题批准。 |

### 7.4 当前有效候选集合

当前有效选题范围共 30 道：

- 延续首轮的 13 个候选：`DOCX30-C001`、`C002`、`C003`、`C004`、`C009`、`C014`、`C017`、`C019`、`C021`、`C023`、`C024`、`C026`、`C030`。
- 重新提出的 17 个候选：`DOCX30-R2-C005`、`C006`、`C007`、`C008`、`C010`、`C011`、`C012`、`C013`、`C015`、`C016`、`C018`、`C020`、`C022`、`C025`、`C027`、`C028`、`C029`。

当前 30 道候选均处于 `APPROVED`，对应 `ts-0001` 至 `ts-0030` 均已取得正式 ID 身份。M4 已于 `2026-08-27` 取消 `BLIND_TESTED` 状态。逐题批准证据见第 5、7.3 节，三题首次审查、复审与风险接受历史见第 9、10 节。

## 8. 下一门禁

在不修改本文件既有历史的前提下，下一步只能是：

1. 对 M4 规格、脱敏审查记录、catalog 实现、合成测试、真实导入证据、全部未跟踪文件和 Git 差异执行最终独立复核。
2. 确认题库哈希、正式 ID 集合、Git/Docker 隐私边界和人工盲测取消后的证据限制仍与冻结证据一致。
3. 最终复核通过后，由用户明确授权 M4 冻结提交和上传；上传确认前不得开始 M5。

当前不得修改既有审查或批准历史、改变正式题目内容、重复导入题库或进入 M5。M4 不再要求或追加 `BLIND_TESTED`。

## 9. 内容审查批次结果（2026-08-26）

依据 `docs/M4_PUZZLE_CATALOG.md` §6.2 对 30 个当时的预冻结题库引用完成逐题内容质量审查；私有逐题记录与详细依据保存在被忽略的 `var/catalog/private_review/`（证据引用前缀 `PRIVATE-CONTENT-REVIEW-V1`）。审查发生时这些 `ts-NNNN` 只用于映射候选和私有证据；其后已因对应候选完成 `APPROVED` 转换而取得正式 ID 身份。

| 结果 | 数量 | 预冻结题库引用 |
|---|---:|---|
| `CONTENT_REVIEWED`（PASS） | 27 | `ts-0001`、`ts-0002`、`ts-0003`、`ts-0004`、`ts-0005`、`ts-0006`、`ts-0007`、`ts-0009`、`ts-0010`、`ts-0011`、`ts-0012`、`ts-0013`、`ts-0014`、`ts-0015`、`ts-0016`、`ts-0017`、`ts-0018`、`ts-0019`、`ts-0020`、`ts-0021`、`ts-0022`、`ts-0023`、`ts-0024`、`ts-0025`、`ts-0026`、`ts-0027`、`ts-0030` |
| `REVISE`（未推进，需修改后重新审查） | 3 | `ts-0008`（自伤/致命自毁行为的美化风险）、`ts-0028`（精神健康群体污名化风险）、`ts-0029`（产后精神障碍污名化风险） |
| `REJECT` | 0 | 无 |

上表保留首次审查时的历史结果，不因后续复审和批准而删除、覆盖或改写。2026-08-27 已完成30道题的逐题批准；批准后的当前状态见第 9.2 节。

### 9.1 复审后、批准前汇总（2026-08-26）

| 当前结果 | 数量 | 说明 |
|---|---:|---|
| `CONTENT_REVIEWED` | 30 | 首次审查通过 27 道；另 3 道依据修订后的 §6.2、§6.3 完成复审并通过。 |
| 待复审 | 0 | 无。 |
| `REJECTED` | 0 | 无。 |

三题原始 `REVISE` 结论仍由上表及私有审查材料保留为历史证据；本汇总只表示复审后、逐题批准前的状态。

### 9.2 逐题批准后当前汇总（2026-08-27）

| 当前结果 | 数量 | 说明 |
|---|---:|---|
| `APPROVED` | 30 | 30 道 `CONTENT_REVIEWED` 候选均已获得用户逐题批准。 |
| 待批准 | 0 | 无。 |
| `REJECTED` | 0 | 当前有效候选集合中无拒绝项；首轮被拒绝候选的历史仍保留。 |

批准证据统一引用 `USER-PUZZLE-APPROVAL-2026-08-27`，逐项转换记录见第 5、7.3 节。

## 10. 当前批次风险接受决定（2026-08-26）

用户在知悉第 9 节三项 `REVISE` 结论后，明确接受以下风险：

| 候选引用 | 预冻结题库引用 | 已接受风险 | 决定证据引用 |
|---|---|---|---|
| `DOCX30-R2-C008` | `ts-0008` | 自伤或明知致命的自毁行为可能具有浪漫化、表演化观感。 | `USER-RISK-ACCEPTANCE-2026-08-26` |
| `DOCX30-R2-C028` | `ts-0028` | 叙事可能造成对精神健康群体的危险化或污名化观感。 | `USER-RISK-ACCEPTANCE-2026-08-26` |
| `DOCX30-R2-C029` | `ts-0029` | 叙事可能造成对产后精神障碍的危险化或污名化观感。 | `USER-RISK-ACCEPTANCE-2026-08-26` |

本决定按 `docs/M4_PUZZLE_CATALOG.md` §6.3 的边界解释，仅适用于上述三个候选，不形成未来题目的通用豁免。第 7.2 节记录的原审查问题和第 9 节 `REVISE` 结论继续作为历史证据保留，不因本决定而删除、覆盖或改写。

风险接受本身不构成 `CONTENT_REVIEWED` 或 `APPROVED` 状态转换，也不授权自动推进候选状态。上述三个候选仍须依据修订后的安全边界重新完成内容审查并形成新的私有证据；审查通过后方可追加 `CONTENT_REVIEWED`，随后仍须由用户逐题决定是否转入 `APPROVED`。

上述三题已于 `2026-08-26` 依据修订后的安全边界完成复审并通过，公开转换记录见第 7.3 节，私有复审证据引用分别为 `PRIVATE-CONTENT-REVIEW-V1:ts-0008`、`PRIVATE-CONTENT-REVIEW-V1:ts-0028` 和 `PRIVATE-CONTENT-REVIEW-V1:ts-0029`。本条仅记录该次复审完成时的事实，不删除或改写原 `REVISE` 证据和风险接受决定；截至该次复审完成时，三题仍待用户逐题决定是否转入 `APPROVED`。

上述三题已于 `2026-08-27` 分别追加 `APPROVED` 转换，批准证据引用均为 `USER-PUZZLE-APPROVAL-2026-08-27`。本条只同步批准后的当前事实；原风险接受决定、首次 `REVISE` 和复审证据继续作为历史保留。

## 11. 脱敏题库批准摘要（2026-08-27）

| 项目 | 当前记录 |
|---|---|
| 题目总数 | 30 |
| `ENABLED` 数量 | 30 |
| 正式 ID 集合 | `ts-0001` 至 `ts-0030`，连续且严格升序 |
| 批准日期 | `2026-08-27` |
| 批准证据引用 | `USER-PUZZLE-APPROVAL-2026-08-27` |
| `catalog.v1.json` SHA-256 | `4741AF061EE85E0CE544296CD1BF9D53F7C8B00DC1A68527353BC508E30B5AF9` |
| 编码前内容冻结复核 | 已于 `2026-08-27` 通过 |
| M4 catalog 实现独立复核 | 已于 `2026-08-27` 通过 |
| SQLite 导入与幂等验收 | 已于 `2026-08-27` 通过 |
| 本地数据库 | 被忽略的 `var/turtle_soup.sqlite3` |
| 最终冻结状态 | 尚待 M4 冻结提交和上传 |

本摘要只记录脱敏事实，不包含题面、题底或核心事实。题库文件仍只允许保存在被忽略的 `var/catalog/catalog.v1.json`；本摘要不能替代对该文件、私有审查材料、Git/Docker 隐私边界和正式 ID 映射的独立内容冻结复核。

### 11.1 本地真实题库导入验收（2026-08-27）

- 正式题库包含 30 个正式 ID，范围为 `ts-0001` 至 `ts-0030`，全部为 `ENABLED`。
- 通过 M4 公共加载入口与 M3 公共 `SQLitePuzzleRepository` 核对，JSON 与 SQLite 中的全部 `Puzzle` 字段一致。
- 使用固定 CLI 命令重复导入后，数据库内容保持不变，幂等验收通过。
- 本地数据库保存在被忽略的 `var/turtle_soup.sqlite3`；数据库属于可变化的运行时状态，因此本文档不记录其 SHA-256。
- M4 人工盲测已按第 7 节取消，本次验收不提供真实玩家可解性、提问稳定性或敏感内容实际观感证据。
