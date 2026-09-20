# P7.2 Human Review UI Simplification — Gate Review

> 在 P7.2 Priority 0 已通过 Gate 的基础上，仅优化 Human Review 交互方式。
> 目标：将 Human Review 从「人工 Annotation」转化为「机器建议 + Human Verification」。
> 本轮只新增 UI 文件，零修改后端模型/冻结基线。

---

## 1. 修改前 Human 操作步骤

**修改前**（CLI `review_interface.py`）：

1. 终端运行 `python3 p7_2_runner.py`
2. 逐条看到：hypothesis_type（HEADING_CANDIDATE）、confidence（MEDIUM）、document_id、page_number
3. 看到：candidate text、bbox 坐标、span_ids
4. 看到：system reason（signals 列表 + count/required + decision reason + confidence breakdown）
5. 输入：`a` / `r` / `n` / `s`（需要记忆字母含义）
6. 输入：reason（必填，自由文本）
7. 输入：notes（可选）
8. 看到时长记录
9. 下一条

**认知负担**：
- Human 需理解 StructureHypothesis / ValidationTask / decision_trace 等内部概念
- 需记忆 `a/r/n/s` 字母映射
- 无视觉证据（无页面图像，只有 bbox 坐标数字）
- 无语音输入
- 无草稿持久化（刷新丢失）
- 需手动输入 reason（每次都要打字）

---

## 2. 修改后 Human 操作步骤

**修改后**（Web UI `index.html`）：

1. 浏览器打开 `http://127.0.0.1:5072/`
2. 看到：**原始文档页面**（自动定位到候选区域，红色高亮框 + 编号）
3. 看到：**系统建议**（纯中文：「系统建议：这可能是一个标题，但系统不是完全确定。」）
4. 看到：**判断依据**（纯中文：「文字样式与周围正文不同；位于阅读顺序的特殊位置；文字行较短。」）
5. 看到：**候选文本**（「Contents」）+ 页码
6. 看到：**免责声明**（「这是系统建议，不是最终事实。你拥有最终决定权。」）
7. 点击：**✓ 对** / **✕ 不对** / **? 无法确定**（三选一，无需记忆字母）
8. （可选）输入文字说明 或 点击 🎤 语音输入
9. 自动进入下一条

**认知负担降低**：
- 无需理解任何内部概念（StructureHypothesis/ValidationTask/decision_trace 全部隐藏）
- 无需记忆字母映射（三按钮 + 图标）
- 视觉优先（页面图像 + 高亮框，不是 bbox 数字）
- 语音可选（点击录音，不强制打字）
- 草稿自动持久化（localStorage，刷新不丢失）
- 系统建议用纯中文，不展示技术字段

---

## 3. UI Cognitive Load Reduction Rationale

| 维度 | 修改前（CLI） | 修改后（Web UI） | 降低 |
|---|---|---|---|
| 内部概念暴露 | hypothesis_type, confidence, decision_trace, span_ids, signals | 全部隐藏 | 100% |
| 决策输入 | `a/r/n/s` 字母 | ✓/✕/? 图标按钮 | 记忆→直觉 |
| 视觉证据 | bbox 数字 [83,110,135,122] | 页面图像 + 红色高亮框 | 抽象→直观 |
| 反馈输入 | 必填 reason（打字） | 可选文字/语音 | 强制→可选 |
| 持久化 | 无（刷新丢失） | localStorage 自动保存 | 无→有 |
| 建议措辞 | 技术性（signals list） | 纯中文（「这可能是一个标题」） | 技术→自然语言 |
| 确认偏误风险 | 无建议（Human 自己判断） | 明确标注「系统建议」+ 免责声明 | 新增防护 |

**核心原则实现**：Human 的任务被压缩为「看原文 → 看系统建议 → 二选一/三选一确认 → （可选）补充一句话 → 下一条」。Human 不需要理解 DICE 内部模型，不承担系统可以承担的结构化工作。

---

## 4. Microphone Interaction Design

**采用「点击开始 → 点击停止」方式**（非按住录音/松开结束）：

| 状态 | UI 表现 | 触发 |
|---|---|---|
| 初始 | 🎤 | 页面加载 |
| 点击一次 | 🔴 正在录音 00:03 | `toggleMic()` → `speechRec.start()` |
| 再次点击 | ⏳ 正在进行语音转文字… | `toggleMic()` → `speechRec.stop()` |
| 完成 | 文本填入 textarea | `speechRec.onresult` |

**实现**：
- 使用 Web Speech API (`SpeechRecognition`)
- `speechRec.lang = "zh-CN"`（中文识别）
- `continuous = false`（单次录音）
- `interimResults = false`（只返回最终结果）
- 转写文本追加到 textarea（不覆盖已有内容）
- Human 可修改/删除/重新录音/保留并提交

**选择点击式而非按住式的原因**：桌面端长期使用时按住鼠标/触控板会产生额外操作负担（用户指令明确要求）。

---

## 5. Text Fallback

**当浏览器不支持录音或 Speech-to-Text 时，优雅降级为普通文字输入：**

```javascript
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
if (!SR) {
    micBtn.classList.add("hidden");   // 隐藏麦克风按钮
    document.getElementById("mic-status").textContent = "";
    return;                            // textarea 仍然可用
}
```

- textarea 始终存在（不依赖 SpeechRecognition）
- 麦克风按钮在不支持时隐藏（不报错、不阻塞）
- 整个 Review 流程不因录音不可用而失败
- 结构验证：`if (!SR)` 降级路径存在 ✅；textarea 始终在 HTML 中 ✅

---

## 6. Persistence / Export Verification

### localStorage 草稿持久化
- **保存**：`localStorage.setItem("p7_2_review_draft", JSON.stringify({currentIdx, decisions}))`
  - 触发时机：每次决策后自动调用 `saveDraft()`
  - 保存内容：当前索引 + 所有决策（observation_id → {decision, reviewer_note, duration_seconds, submitted, timestamp}）
- **恢复**：`localStorage.getItem("p7_2_review_draft")` 在 `init()` 中调用
  - 恢复内容：currentIdx + decisions
- **验证**：`setItem` ✅、`getItem` ✅、`saveDraft()` 在决策后调用 ✅

### Export 导出
- **API**：`GET /api/export` → 返回 `{records, evidence, audit_chains}`
- **前端**：`exportData()` → fetch /api/export → 下载 JSON 文件
- **reviewer_note 在导出中**：
  - Case 8 验证：导出数据中 record 的 `reviewer_notes` 字段包含 Human 输入的文本 ✅
  - 示例：`reviewer_notes: "这是目录页码不是标题"` ✅

### 现有 P7.2 数据链路保持
- ValidationRecord 通过现有 `create_validation_record()` 创建（后端 UNCHANGED）✅
- ValidatedEvidence 通过现有 `derive_evidence()` 派生（后端 UNCHANGED）✅
- 审计链通过现有 `build_audit_chain()` 构建（后端 UNCHANGED）✅
- reviewer_note 作为 `reviewer_notes` 字段保存到 ValidationRecord（现有字段，非新增）✅

---

## 7. P7.2 Backend Regression

| 检查项 | 文件 | SHA256 前缀 | 状态 |
|---|---|---|---|
| validation_config.py | 953796045a3ade5c | ✅ UNCHANGED |
| validation_models.py | 8bdcbcc0c530ae00 | ✅ UNCHANGED |
| validation_engine.py | 2d9204dedccacb6f | ✅ UNCHANGED |
| validation_tests.py | b7075e2afe096a37 | ✅ UNCHANGED |
| __init__.py | 3aee6c93c0e6c486 | ✅ UNCHANGED |
| review_interface.py (CLI) | 7b447fed80bed070 | ✅ UNCHANGED |
| p7_2_runner.py | b8e965cf37d7120a | ✅ UNCHANGED |
| p7_2_apply_decisions.py | d52090a8e0247615 | ✅ UNCHANGED |

**T1-T12 测试套件**：12/12 通过 ✅

**结论**：P7.2 后端完全未修改。UI 通过 HTTP 层调用现有后端函数，不新增/不修改任何数据模型。

---

## 8. Frozen Baseline Verification

| 检查项 | 结果 |
|---|---|
| P7.1 冻结文件（6 个）SHA256 | ✅ 全部匹配 |
| P1–P6 代码 SHA256 | ✅ 全部 UNCHANGED |
| Frozen 730 md5_8 | ✅ a10b368e |
| P7.1 regression_gate() | ✅ PASS |
| P7.1 structure 文件（4 个） | ✅ 全部 UNCHANGED |
| schema / annotation pool / capability / registry / runtime | ✅ 未触碰 |

**本轮新增文件（4 个，仅 UI）**：
- `perception/sandbox/validation/review_web/__init__.py`（73 bytes）
- `perception/sandbox/validation/review_web/suggestion.py`（5685 bytes）
- `perception/sandbox/validation/review_web/index.html`（19677 bytes）
- `perception/sandbox/validation/review_web/review_server.py`（8506 bytes）

**零修改已有文件**。无 React 重构、无新数据库、无新 schema、无新 LLM pipeline、无自动学习、无自动规则更新。

---

## 9. Browser Interaction Results

| Case | 测试内容 | 方法 | 结果 |
|---|---|---|---|
| 1 | 系统建议 → 对 → ACCEPT → Evidence | POST /api/submit decision=accept | ✅ evidence_derived=true, evidence_id=1ce36156 |
| 2 | 系统建议 → 不对 → REJECT → Blocked | POST /api/submit decision=reject | ✅ blocked=true, evidence_derived=false |
| 3 | 系统建议 → 无法确定 → NEED_REVIEW → 不生成 Evidence | POST /api/submit decision=need_review | ✅ blocked=true, evidence_derived=false |
| 4 | 不对 + 手动输入文字说明 → reviewer_note 保存 | POST + reviewer_note | ✅ reviewer_notes="这是目录页码不是标题" |
| 5 | 不对 + 点击麦克风 → 录音 → 停止 → 转文字 → 可修改 → 保存 | HTML 结构验证 | ✅ toggleMic() click-to-start/stop, 🎤→🔴→⏳→text |
| 6 | 录音不可用 → 文字输入正常 | HTML 结构验证 | ✅ if(!SR) 降级, textarea 始终存在 |
| 7 | 刷新页面 → draft/decision/reviewer_note 恢复 | JS 代码验证 | ✅ localStorage setItem/getItem/saveDraft |
| 8 | 导出 → reviewer_note 进入导出数据 | GET /api/export | ✅ reviewer_notes 在导出 records 中 |

**说明**：Case 1-4、8 通过 API 端点测试验证（真实 HTTP 请求 + 响应）。Case 5-7 通过 HTML/JS 结构分析验证（浏览器环境无法在此 agent 中运行真实浏览器，但代码逻辑已验证完整）。

---

## 10. Screenshots / Visual Verification

由于当前 agent 模型不支持图像输入，无法直接查看 UI 截图。以下为结构化验证：

### 页面结构（四个区域）
- **A. 原始文档区域**：`<div class="doc-area">` 包含 `<img id="page-img">` + `<div class="highlight-box">` ✅
  - 页面图像从 `/api/page-image` 加载（127KB PNG，150 DPI）
  - 高亮框通过 CSS 绝对定位 + bbox 缩放计算位置 ✅
- **B. 系统建议区域**：`<div class="suggestion">` 包含 suggestion-text + reasoning + alternatives + disclaimer ✅
- **C. Human 决策区域**：`<div class="decision-area">` 包含 3 个 dec-btn（accept/reject/uncertain）✅
- **D. 可选反馈区域**：`<div class="feedback">` 包含 textarea + mic-btn ✅

### 视觉优先级
1. 原始文档（左侧 flex:1，最大区域）✅
2. 候选区域（红色高亮框 + 编号标签）✅
3. 系统建议（右侧面板顶部）✅
4. 对/不对/无法确定（右侧中部）✅
5. 可选反馈（右侧下部）✅
6. 内部技术字段：默认隐藏（observation_id/confidence 等在 JSON 中但不显示）✅

### 系统建议示例
```
系统建议：这可能是一个标题，但系统不是完全确定。
系统有一定信心
判断依据：文字样式（粗体或字号）与周围正文不同；位于阅读顺序的特殊位置；文字行较短，不像完整段落。
这是系统建议，不是最终事实。你拥有最终决定权。
```

### LOW 置信候选示例（显示多种可能）
```
系统无法确定，建议人工判断。
可能是：
A. 正文章节标题
B. 目录或引用内容
C. 表格标签
D. 页眉页脚
请判断。
```

---

## 11. Geometry Integrity Report

**检查结果**：33 条候选的 bbox 全部通过完整性检查，**无 geometry 问题需要报告**。

| 检查项 | 结果 |
|---|---|
| bbox 在页面边界内（595×842） | ✅ 全部 33 条 |
| bbox 非退化（width > 0.5, height > 0.5） | ✅ 全部 33 条 |
| bbox 尺寸合理（width < 95% page, height < 10% page） | ✅ 全部 33 条 |
| span_ids 存在 | ✅ 全部 33 条 |
| span 文本非空 | ✅ 全部 33 条 |

**无 STOP 条件触发**。候选 geometry 正确，无需通过 UI 修正。

---

## 12. Anti-Confirmation-Bias 验证

| 要求 | 验证 | 结果 |
|---|---|---|
| 标注为「系统建议」 | HTML 中 2 处「系统建议」 | ✅ |
| 不使用诱导性文字 | grep「正确答案/确定是/请确认正确」= 0 匹配 | ✅ |
| 免责声明 | 「这是系统建议，不是最终事实。你拥有最终决定权。」 | ✅ |
| LOW confidence 明确不确定 | 「系统无法确定，建议人工判断。」 | ✅ |
| 两种解释并存 | LOW 候选显示 alternatives（A/B/C/D） | ✅ |
| 不诱导接受 | 建议用「可能」而非「是」 | ✅ |

---

## 综合判定

### 通过 ✅

| 验收项 | 结果 |
|---|---|
| A. Static/Structural Check | ✅ 无复杂 Annotation，三选一逻辑正确，mic + text + reviewer_note 存在，无冻结修改 |
| B. Browser Interaction Test (Case 1-8) | ✅ 全部通过（1-4/8 via API，5-7 via 结构验证） |
| C. Regression | ✅ P1–P7.1 UNCHANGED, Frozen 730 UNCHANGED, P7.2 backend UNCHANGED, T1-T12 12/12 |

### 理想 Human 操作已实现

```
看原文（页面图像 + 红色高亮框）
  → 看系统建议（纯中文，非技术字段）
  → 点击「对 / 不对 / 无法确定」
  → 必要时说一句话（语音或文字）
  → 下一条
```

Human 不需要学习 DICE 内部概念，不承担系统可以承担的结构化工作。

### 未触碰的禁止项

- P7.1 StructureHypothesis / candidate generation ✅ 未修改
- extractor / parser / geometry ✅ 未修改
- CandidateSpan / DocumentSpan ✅ 未修改
- Frozen 730 / annotation pool ✅ 未修改
- ValidationTask / ValidationRecord / ValidatedEvidence 数据模型 ✅ 未修改
- Evidence provenance / governance ✅ 未修改
- Capability / Registry / Runtime / schema ✅ 未修改
- 自动 ACCEPT / LLM approve ✅ 未引入
- Candidate geometry ✅ 未通过 UI 修正（geometry 完整性检查通过，无需修正）
- React 重构 / 新数据库 / 新 schema / 新 LLM pipeline ✅ 未引入

### 透明说明

- Case 5-7（麦克风录音 / 降级 / 刷新恢复）通过 HTML/JS 结构分析验证，未在真实浏览器中运行
- 建议后续在 Chrome/Edge 浏览器中进行真实人工终端验证（打开 `http://127.0.0.1:5072/`）
- 语音识别依赖 Web Speech API（Chrome/Edge 支持，Firefox 可能不支持 → 降级为文字输入）

---

## 13. 是否建议进入下一阶段

**建议**：本阶段 UI 简化改造完成，Gate 通过。

**不建议立即进入 P7.3**。建议下一步：
1. 在真实浏览器中进行人工终端验证（验证 Case 5-7 的麦克风/降级/刷新恢复）
2. 完成一次完整的人工终端 33 条审阅（产出真实人类 wall-clock 时长）
3. 然后等待批准决定下一阶段方向

**STOP。未进入 P7.3 / Visual Object / Table Cell / Formula / Agent / QA。等待下一步批准。**
