# 🧪 photoFilter

> ⚠️ **这个 README 是 AI 写的，可能有幻觉**。具体行为请以代码为准，描述跟实际对不上的地方欢迎提 issue / 直接改。
>
> *This README is AI-generated and may hallucinate. Code is the source of truth — open an issue or fix directly when descriptions diverge from reality.*

选择一个文件夹，自动识别相似图片，批量删除重复帧。完全在浏览器里跑 — 文件不上传、不联网。

> *Pick a folder, find near-duplicate images, delete them in bulk. Runs entirely in your browser — no upload, no server.*

---

## 💡 为什么做这个

视频抽帧动辄上千张，重复帧占磁盘又难挑；手动翻 = 噩梦。

> *Video frame extraction often produces thousands of frames, many of them near-duplicates. Manual review is a nightmare.*

PhotoFilter 用 dHash 感知哈希 + 可调阈值，在浏览器内本地比对，几次点击就能挑出重复帧、批量删除。整个过程文件不出本机。

> *PhotoFilter uses dHash perceptual hashing with an adjustable threshold to compare frames locally in your browser. A few clicks reveal duplicates and bulk-delete them. Files never leave your machine.*

---

## 🚀 快速开始

### 📥 下载到本地

```bash
git clone https://github.com/woohahahaaa/photoFilter.git
cd photoFilter
```

> *Clone the repo and enter the directory.*

### 🤖 让 Agent 帮你跑（推荐）

把项目路径丢给 OpenCode / Claude Code / Cursor，然后对它说：

> **帮我跑 photoFilter**

agent 会自动装依赖、启动 Flask 服务、提示你选目录。

> *Hand the project directory to OpenCode / Claude Code / Cursor and say "Start photoFilter for me". The agent will install deps, start Flask, and prompt you to choose a folder.*

### 🌍 打开浏览器

服务起来后，浏览器自动打开 `http://127.0.0.1:5000`，点 **Choose Photo Folder** 选一个 jpg 帧目录。

> *Once the server is up, the browser opens `http://127.0.0.1:5000`. Click **Choose Photo Folder** and pick a directory of jpg frames.*

> ⚠️ **仅支持 Chrome / Edge**（依赖 File System Access API），Safari 和 Firefox 不行。

> *Chrome / Edge only — depends on the File System Access API. Safari and Firefox are unsupported.*

### 🛟 兜底：手动启动

```bash
pip install flask pillow
python app.py
```

环境变量指定帧目录：

```bash
FRAMES_DIR=/path/to/frames python app.py
```

> *Manual fallback: install Flask and Pillow, then run `app.py`. Override the frames directory with `FRAMES_DIR`.*

---

## 📁 项目结构

```
photoFilter/
├── app.py                       # Flask 后端：缩略图 + API 兜底
├── templates/
│   └── index.html               # 前端 SPA，单文件零依赖
├── .gitignore
└── README.md
```

> *Flask backend plus a single-file HTML/CSS/JS frontend with zero build deps.*

---

## ✨ 功能一览

| 功能 | 操作 |
|------|------|
| 打开文件夹 | 点 **Choose Photo Folder**（Chrome / Edge） |
| 浏览画廊 | 按源视频分组，按 score 排序 |
| 筛选 | 最低分数 / 最小宽高 / 缩略图大小 |
| 多选 | 单击 / Shift 范围选 / Ctrl 反选 / 拖拽框选 |
| 预览 | 双击大图，← → 翻页，Esc 关闭 |
| 自动去重 | 一键 dHash 检测，Sim 滑块实时调阈值 |
| 删除 | 选中后 `confirm()` 二次确认，**真实删除**本地文件（不可恢复） |

> *Click **Choose Photo Folder** (Chrome/Edge); browse grouped by source video, sorted by score; filter by min score / min resolution / thumbnail size; multi-select via click / Shift+click / Ctrl+click / drag-box; preview with double-click and arrow keys; one-click dHash dedup with live threshold retuning; deletes local files after `confirm()` — **deletion is real and irreversible**.*

---

## 🧠 核心原理

去重引擎走 **dHash（差值感知哈希）**：

> *The dedup engine uses **dHash (difference hash)**.*

1. 把图片缩放到 17×16 灰度图。
   > *Resize the image to a 17×16 grayscale canvas.*
2. 同一行内对相邻像素比较亮度，生成 16×16 = **256 位**二进制哈希。
   > *Compare horizontally adjacent pixels per row to produce a 16×16 = **256-bit** binary hash.*
3. 同视频分组内按 score 降序遍历，当前哈希与已保留哈希的**汉明距离 ≤ 阈值**则判定重复。
   > *Within each video group, walk frames in descending score order. If the Hamming distance to any kept hash is ≤ threshold, mark as duplicate.*
4. 阈值越小越严格（10 ≈ 几乎相同；60 = 默认；256 ≈ 全部相似）。
   > *Lower threshold = stricter matching (10 ≈ near-identical; 60 = default; 256 ≈ all similar).*

### 文件名约定

去重按以下格式解析帧文件名，未匹配的归到 `unknown` 分组：

> *Frames are parsed by the following filename pattern; unmatched frames fall into `unknown`.*

```
{video}_ts{timestamp}s_score{score}.{jpg|png}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `video` | string | 源视频名（用于分组） |
| `timestamp` | float | 抽帧时间（秒） |
| `score` | float | 质量分（0~1） |

---

## 📦 依赖

| 组件 | 需要的包 |
|------|----------|
| 前端（核心） | 无，纯浏览器 API |
| `app.py`（可选 Flask 后端） | `flask`, `pillow` |

> *Frontend: zero deps, pure browser API. Flask backend: `flask`, `pillow`.*

---

## 📜 License

未声明 License，仅供学习与个人使用。

> *No license declared; for learning and personal use only.*
