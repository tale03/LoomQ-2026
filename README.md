# Qat / 喵子 🐾

> 薛定谔打开了盒子，我们打开了门。
> 好奇心不该被代码挡住——无论你是人还是猫。

**Qat（喵子）** 是一个量子计算翻译平台，让零量子背景的用户也能使用量子计算机。

用户用中文或英文描述实验 → 喵子写好 QASM 代码 → 自动翻译到不同量子计算机 → 运行 → 用薛定谔的猫告诉你结果。

不需要学编程。不需要懂物理。说人话就行。

**LoomQ · SheNicest 2026 参赛作品** by [tale03](https://github.com/tale03)

---

## 快速启动

```bash
# 1. 安装依赖
pip install -r starter_kit/requirements.txt

# 2. 设置 LLM 环境变量（组委会评测时统一注入）
export LOOMQ_LLM_BASE_URL=https://api.deepseek.com
export LOOMQ_LLM_API_KEY=<your-key>
export LOOMQ_LLM_MODEL=deepseek-chat

# 3. 启动
cd starter_kit
python app.py

# 4. 打开浏览器
# http://localhost:5000
```

## 功能概览

### L1 — 量子通用中间层（Transpiler）

将标准 OpenQASM 2.0 电路转译为三个后端的原生格式：

| 后端 | 格式 | 模拟器 | 真机 |
|---|---|---|---|
| 量旋 SpinQ | OpenQASM 2.0 | Taurus 本地模拟器 | Gemini NMR ✅ |
| 本源 OriginQ | OriginIR | CPUQVM 本地模拟器 | 悟空 180 超导 ✅ |
| AWS Braket | OpenQASM 3.0 | LocalSimulator | — |

支持全部 12 个白名单门（h, x, s, sdg, t, tdg, rz, ry, cx, cu1, swap, ccx），不支持的门自动等价分解。

### L2 — 智能体（Agent）

基于 DeepSeek LLM 的量子助手，三大能力：

1. **生成代码** — 用自然语言描述实验，自动生成正确的 QASM 代码
2. **修复代码** — 识别语法/语义错误，保持用户意图修复电路
3. **选择平台** — 根据比特数、排队、费用约束推荐最优后端

内置 retry loop：生成 → transpile 验证 → 有错自动修复 → 再验证。

### L3 — 混合编译（Hybrid Compiler）

将 Hybrid-QASM 编译为量子操作序列 + RISC-V 汇编，支持经典控制流（if/else、赋值、算术运算）。

### RISC-V 量子扩展（Bonus）

自定义 RISC-V 指令集扩展，将量子门编码为原生 RISC-V 指令（opcode `0001011`，custom-0 空间），实现量子-经典统一指令流。包含：
- 指令编码规格文档（`quantum_riscv_spec.md`）
- 扩展模拟器（`riscv_emulator.py`），支持 8 条量子指令
- 端到端测试：`python starter_kit/riscv_emulator.py`

### 前端界面（Qat / 喵子）

**首页（量子坍缩动画）**
- 全屏 Canvas 波纹动画，使用 value noise 生成物理随机噪音
- 鼠标移动时波纹「坍缩」出猫头轮廓，隐喻量子测量导致波函数坍缩——未观测时是均匀波纹（叠加态），观测后坍缩为确定形态（猫）
- 猫头轮廓区域有形状跟随的光晕效果（非简单圆形），轮廓边缘最亮，内部次亮，向外渐变消失
- 四边渐变边框（亮色模式白色，暗色模式黑色）
- 「Qat」标题（Bodoni Moda）+「喵 子」副标题（猫啃珠圆体）+ 标语
- 「点击任意位置以观测 / click anywhere to observe」提示
- 点击时播放猫叫音效，过渡到聊天界面

**欢迎卡（零基础引导）**
- 从「比特」概念讲起，逐步介绍量子比特、叠加、QASM、翻译的必要性
- 三大功能明确展示，每个配有可点击的试试看按钮：
  - ① 生成代码 →「抛一枚量子硬币」「创造纠缠粒子」
  - ② 修复代码 →「修复一段错误代码」
  - ③ 选择平台 →「帮我选一个量子平台」
- 提醒用户点击「运行」按钮查看结果（黑色加强显示）
- 首次发送消息后欢迎卡折叠，飞向标题栏的 ? 按钮；点击 ? 可重新打开

**薛定谔盒子（结果可视化）**
- 点击代码下方「运行」→ 盒子摇晃（循环播放摇晃音效）+ 进度条填充
- 结果返回 → 音效渐弱停止 → 盖子打开（95°弹簧动画）→ 猫从盒子里出现
- 猫的状态取决于结果：醒着（有明确结构的分布）或睡着（均匀叠加分布）
- 盒子正面有黑色实心 ? 号，结果出来后消失
- 底部 QUANTUM 标签
- 动画结果直方图条形图 + 百分比
- 通俗文字解释（如「2个量子比特发生了纠缠——它们的状态完全关联」）

**聊天界面**
- 消息气泡：用户黑底白字，AI 浅灰底
- 代码块：自动识别 QASM，提供「选择」「复制」「运行」三个按钮
- 重试/编辑按钮
- Markdown 渲染（加粗、列表）
- 旋转加载短语（「喵子正在计算中...」等）
- 错误温馨提示（「喵...出了点问题」+ 重试按钮）

**侧边栏**
- 左侧「了解概念」：7 个按钮（量子比特、叠加态、测量与坍缩、量子纠缠、概率与确定性、量子优势、薛定谔的猫），点击后智能体用通俗语言解释
- 左侧「试一试」：量子硬币、贝尔态、量子随机数、修复代码
- 右侧「工具手册」：H 门、X 门、CNOT 门、量子电路、QASM 语言、Shots 采样
- 右侧「快速实验」：GHZ 态、确定结果、量子隐形传态、选择后端
- 标题框带猫耳装饰（圆角 + clip-path 三角形）
- 点击按钮时显示 🐾 猫爪印闪烁动画

**设计细节**
- 字体：Bodoni Moda（标题）、Comfortaa（英文正文）、猫啃珠圆体（中文正文）、IBM Plex Mono（代码）
- 完整亮色/暗色主题切换
- 中英文完整国际化（翻译系统 + 双语占位提示）
- 猫叫音效（发送消息、首页点击、打开介绍卡时）+ 摇晃音效（运行时循环，结果返回渐弱）
- 音效开关按钮（♪）
- 自定义猫形鼠标光标
- 猫爪按钮（🐾）→ 弹出项目介绍卡片

## 项目结构

```
starter_kit/
├── adapter.py           # 核心：transpile(), run(), agent_chat(), compile_hybrid()
├── llm_client.py        # LLM API 封装（读取 LOOMQ_LLM_* 环境变量）
├── app.py               # Flask 服务器（/chat, /run）
├── templates/
│   └── index.html       # 前端界面（Qat/喵子）
├── static/
│   ├── meow.mp3         # 猫叫音效
│   └── shake.mp3        # 摇晃音效
├── riscv_emulator.py    # 量子扩展 RISC-V 模拟器
├── quantum_riscv_spec.md # 量子 RISC-V 指令编码规格
├── requirements.txt     # 依赖（精确版本）
├── evidence/
│   ├── README.md        # 人工评分证据
│   └── files/           # 真机结果、电路文件
└── ...
```

## 真机运行证据

| 平台 | Job ID | 时间 | 主导态 |
|---|---|---|---|
| SpinQ Gemini NMR | G-260818-0009 | 2026-08-18 08:49 UTC | 00 (44%), 11 (43%) |
| OriginQ 悟空 180 | EC100A9E1CCE2596F25F7293995FF104 | 2026-08-18 21:53 +08:00 | 00 (47%), 11 (48%) |

两台真机均成功运行 Bell state 电路，主峰命中 00 和 11，符合纠缠态理想分布。

## 运行测试

```bash
# L1 转译器自测
python3 evaluator.py --level l1 --target spinq,originq,braket

# L2 智能体自测
python3 evaluator.py --level l2

# L3 混合编译自测
python3 evaluator.py --level l3

# RISC-V 量子扩展测试
python riscv_emulator.py
```

## AI 辅助声明

本项目在开发过程中使用了 AI 辅助编程（Claude）协助完成前端界面开发和代码调试。核心逻辑（transpiler、agent、compiler）由参赛者设计和实现。

---

# LoomQ · 量子接入平权计划：赛题发布包

> SheNicest 2026 夏季千人烈变黑客松 · 正式赛题（选手分发版）

## 包内容

| 文件 / 目录 | 说明 |
|---|---|
| `LoomQ-赛题手册.pdf` | 正式题面，用于官网发布与选手下载 |
| `LoomQ-赛题.html` | 题面网页版（零依赖单文件：无 CDN、无外部字体、无框架），可直接作为活动官网赛题页部署 |
| `problem_statement.md` | 题面 Markdown 源，与 PDF 内容一致，便于线上阅读与检索 |
| `LoomQ-赛题.docx` | 题面 Word 版（由 Markdown 源生成，公式为 Word 原生对象），供组委会流转编辑 |
| `LoomQ-选手提交流程图.png` | 最终提交流程信息图，适合单独转发给选手 |
| `starter_kit/` | 选手工具包 v1.1.0：提交清单、人工评分证据模板、L2 环境协议、公开自测、容器基线、RISC-V 模拟器、公开电路与上手资料 |

## 最终提交流程图

![LoomQ 最终提交流程](LoomQ-选手提交流程图.png)

## 人工评分需要提交什么

自动评分会直接运行 `starter_kit/` 中的程序。若要申报人工评分或 Bonus，只需填写 [`starter_kit/evidence/README.md`](starter_kit/evidence/README.md)。截图、原始结果或图表可以统一放入 `starter_kit/evidence/files/`。

| 评分项 | 选手需要说明什么 | 可附材料 |
|---|---|---|
| L1 真机，最高 10 分 | 平台、job ID、运行时间、shots、实际执行的 QASM 和原始结果路径 | 任务页截图 |
| L2 交互体验，最高 10 分 | 界面或 CLI 的启动方法，以及 3 个用户体验任务 | 关键流程截图或演示视频 |
| 工程与产品复核，人工部分最高 5 分 | 构建和启动方法、主要模块、目标用户和完整使用流程 | 架构图、产品截图或已有项目文档 |
| 自定义量子 RISC-V，最高加 8 分 | 指令编码规格、模拟器实现位置和端到端测试命令 | 无需额外材料，三项齐全且测试通过即可 |
| 新手引导与视觉叙事，最高加 4 分 | 首次运行、概念解释、结果可视化、错误恢复或无障碍引导的位置 | 对应截图 |

已有项目 README 或文档可以直接引用，不必为了评分重复写一份。工作人员只核验截止时归档的 commit，不接受截止后补交。截图不能代替可追溯的 job ID、原始结果或可运行代码。不要提交 API Key、Token、Cookie 或个人隐私。完整归档不得超过 100 MiB，大视频请使用稳定只读链接。

## 常见问题

### 需要参加线下答辩吗？

不需要。这是线上比赛，不设置线下答辩、现场演示或到场环节。选手只需按提交流程在截止时间前完成线上提交；组委会将依据归档代码、自动评测结果和已提交的证据材料进行评分与复核。

### 需要提前登记队伍名单吗？

不需要。每队指定一个 GitHub 提交账号，该账号的用户名就是本次比赛的 Team ID。fork 必须归该账号所有，最终提交 Issue 也必须由同一账号创建。

### 多人团队如何协作？

其他成员可以作为 fork 仓库的 collaborator、通过分支或 Pull Request 参与开发。只有最终提交动作需要由指定的 GitHub 提交账号完成。

### 正式提交的内容放在哪里？

统一放在 fork 的 `starter_kit/` 中。组委会只把该目录提取为正式评测根目录。

### 人工评分证据必须提交吗？

证据包本身是可选的。若要申报 L1 真机、L2 交互体验、工程与产品化或 Bonus，直接填写 [`starter_kit/evidence/README.md`](starter_kit/evidence/README.md) 即可。需要的附件统一放进 `starter_kit/evidence/files/`。未申报某项或未提交对应证据，只影响该项人工分，不影响自动评分。

### 提交前要运行什么？

在 fork 根目录运行：

```bash
python3 starter_kit/prepare_submission.py --team-id <GITHUB_USERNAME>
```

预检会确认工作区干净、HEAD 已推送、fork 所有者与 Team ID 一致，并输出可填写到 Issue Form 的仓库地址和 40 位 commit SHA。

### 如何确认提交成功？

最终提交 Issue 获得 `submission:accepted` 标签，并出现包含 commit、归档 SHA-256 和 Artifact ID 的自动回执，才算有效提交。仅创建 Issue 或通过本地预检不代表提交成功。

### 提交后还能更新吗？

可以。修改代码并 push 后重新创建一个最终提交 Issue，不要编辑旧 Issue。截止前最后一次通过校验的提交生效。

### 截止时间如何判定？

截止时间是 **2026-08-25 12:00 UTC+8**，以 GitHub 服务器记录的 Issue `created_at` 为准，不看 commit 时间或本地电脑时间。

### L2 会提前提供组委会 API 或 Key 吗？

不会。赛前可使用自己的 DeepSeek Key 或其他 OpenAI-compatible 服务调试，但代码必须读取 `LOOMQ_LLM_*` 环境变量。正式评测由组委会统一注入 DeepSeek 模型服务和调用预算。

### 可以依赖其他外部 API 吗？

不建议。正式评测环境不保证能够访问模型服务以外的外部网络地址。

### fork 或分支在截止后被删除怎么办？

每次有效提交都会即时归档为 GitHub Actions Artifact。组委会截止后从归档收集，不依赖 fork 在评分时仍然存在；选手仍应保留 fork 便于复核。
