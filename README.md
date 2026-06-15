# PhotoFilter

> 选择一个文件夹，自动识别相似图片，一键批量删除重复帧。
> 全部在你的浏览器里完成 — 文件不上传、不联网。

Pick a folder, find near-duplicate images, delete them in bulk. **Runs entirely in your browser** — no upload, no server.

---

## ✨ 特性

- 🖼️ **画廊浏览** — 按源视频分组，按帧分数排序展示
- 🎯 **多维筛选** — 最低分数 / 最小宽高 / 缩略图大小，实时过滤
- ☑️ **多种选择** — 单击、Shift 范围选、Ctrl/Cmd 反选、拖拽框选
- 🔍 **大图预览** — 双击放大、左右键翻页、Esc 关闭
- 🧬 **dHash 智能去重** — 浏览器内计算 256 位感知哈希，毫秒级比对
- 🎚️ **阈值实时调参** — 拖动「Sim」滑块即可重新聚类，无需重算哈希
- 🗑️ **真删除** — 通过 `FileSystemFileHandle.remove()` 真实删除本地文件
- 💾 **状态记忆** — 选中的文件夹句柄持久化在 IndexedDB，下次打开自动恢复
- ⌨️ **键盘友好** — 快捷键覆盖选择 / 预览 / 删除全流程
- 🎨 **暗色主题** — 现代深色 UI，长时间整理不刺眼

---

## 🚀 快速开始

### 方式 1：纯浏览器（最简单）

需要一个静态文件服务器把 `templates/index.html` 跑起来即可（浏览器不允许 `file://` 直接调用 File System Access API）。

```bash
# 任选其一
python -m http.server 8000
# 或
npx serve .
# 或直接用 Flask（见方式 3）
```

打开 `http://localhost:8000/templates/index.html`，点 **Choose Photo Folder**，授权一个本地目录。

> **首选浏览器**：Chrome / Edge / 其他基于 Chromium 的浏览器。
> Safari / Firefox 不支持 File System Access API。

### 方式 2：让 AI Agent 帮你跑

直接把项目路径丢给 OpenCode / Claude / Cursor：

> "帮我跑 photoFilter，启动 Flask 服务"

Agent 会自动安装依赖、启动后端、打开浏览器。

### 方式 3：Flask 后端（可选）

```bash
pip install flask pillow
python app.py                 # → http://127.0.0.1:5000
```

环境变量指定帧目录：

```bash
FRAMES_DIR=/path/to/frames python app.py
```

> `app.py` 提供 `/api/thumbnail` 服务和 `/api/dedup` 兜底接口。**主流程（选择、浏览、去重、删除）仍然完全在浏览器内完成** —— 后端只是用来在着陆页展示已配置目录的提示，不参与核心计算。

---

## 📐 文件名约定

去重引擎会解析文件名为以下格式，未匹配的会归到 `unknown` 分组：

```
{video_name}_ts{timestamp}s_score{score}.{jpg|png}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `video_name` | string | 源视频名（用于分组） |
| `timestamp` | float | 抽帧时间（秒） |
| `score` | float | 质量分（0~1，用于排序与去重保留优先级） |

示例：`myvideo_ts12.34s_score0.872.jpg`

---

## 🧬 去重原理

使用 **dHash（差值感知哈希）**：

1. 将图片缩放到 **17×16 灰度图**（canvas）
2. 对每一行的相邻像素比较亮度，生成 16×16 = **256 位**二进制哈希
3. 同一视频分组内，按 score 降序遍历
4. 当前图与任一已保留图的 **汉明距离 ≤ 阈值** → 标记为重复
5. 阈值越小越严格（10 ≈ 几乎相同；60 = 默认；256 ≈ 全部相似）

**实现位置**：完全在浏览器内（`computeDhash` / `localDedup`），无需服务端计算。

---

## ⌨️ 快捷键

| 按键 | 行为 |
|------|------|
| `Esc` | 关闭预览 / 清除选择 |
| `←` / `→` | 预览中切换上一张 / 下一张 |
| `Delete` | 删除当前选中（等同点 Delete 按钮） |
| `Click` | 单选 |
| `Shift + Click` | 范围选（从上次点击处到当前） |
| `Ctrl/Cmd + Click` | 反选单个 |
| 拖拽空白处 | 框选（按住 `Shift` / `Ctrl` 叠加反选） |

---

## 🗂️ 项目结构

```
photoFilter/
├── app.py                       # Flask 后端（可选）
├── templates/
│   └── index.html               # 前端 SPA（HTML + CSS + JS，单文件）
├── .gitignore
└── README.md
```

整个前端是一个 **零依赖单文件**（`index.html`），没有构建步骤，没有 node_modules。

---

## 🔌 Flask API 一览

后端只是辅助接口，前端主流程不会阻塞依赖它们。

| Method | Path | 说明 |
|--------|------|------|
| `GET` | `/` | 渲染 `index.html` |
| `GET` | `/api/info` | 返回已配置的 `FRAMES_DIR` 与图片数 |
| `GET` | `/api/images` | 列出目录内所有 `.jpg` 的元信息 |
| `GET` | `/api/thumbnail/<path>` | 生成 320×180 JPEG 缩略图 |
| `GET` | `/api/image/<path>` | 返回原图 |
| `POST` | `/api/dedup` | 兜底的服务器端去重接口（前端一般用本地版） |

所有 `<path>` 都做了 `FRAMES_DIR` 路径前缀校验，防止越权访问。

---

## 📦 依赖

| 组件 | 依赖 |
|------|------|
| 前端（核心） | **无** —— 纯浏览器 API |
| `app.py`（可选） | `flask`, `pillow` |

---

## ⚠️ 删除是真实的，不可恢复

> 选择 → 删除会直接调用 `FileSystemFileHandle.remove()`，**文件进入系统回收站/永久删除**。
>
> 建议先去重 + 预览选中结果，确认无误再点 Delete。
> 当前版本删除前会有 `confirm()` 二次确认，但仍请谨慎操作。

---

## 🧪 兼容性

| 浏览器 | File System Access | 状态 |
|--------|--------------------|------|
| Chrome 86+ | ✅ | 推荐 |
| Edge 86+ | ✅ | 推荐 |
| Opera 72+ | ✅ | 可用 |
| Safari | ❌ | 不支持 |
| Firefox | ❌ | 不支持 |

---

## 📝 备注

本项目代码与 README 均为 AI 生成，仅供学习与个人使用。删图前请自行备份。
