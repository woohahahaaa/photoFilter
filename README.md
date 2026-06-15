# photoFilter

选择一个文件夹，自动识别相似图片，批量删除重复帧。纯浏览器运行。

Pick a folder, find near-duplicate images, delete them in bulk. Runs entirely in your browser.

---

## 项目结构

```
photoFilter/
├── app.py                   # Flask 后端（可选，提供 API 浏览模式）
└── templates/
    └── index.html           # 前端 SPA — 画廊浏览 / 相似检测 / 批量删除
```

---

## 快速开始

### 方式一：纯本地（推荐）

直接用浏览器打开页面，通过 File System Access API 选择本地文件夹，无需后端。

### 方式二：Flask 后端

```bash
pip install flask pillow
python app.py   # → http://127.0.0.1:5000
```

环境变量指定帧目录：`FRAMES_DIR=/path/to/images python app.py`

---

## 核心流程

```
选择文件夹 → 浏览图片画廊 → 一键去重（dHash）→ 调整相似度阈值 → 选中删除
```

---

## 功能一览

| 功能 | 操作 |
|------|------|
| 打开文件夹 | 点击按钮选择本地图片目录（Chrome/Edge） |
| 浏览画廊 | 按来源分组展示，按分数排序 |
| 筛选 | 最低分数 / 最小宽高 / 缩略图大小 |
| 多选 | 点选、Shift 范围选、拖拽框选 |
| 预览 | 双击大图，左右箭头切换 |
| 自动去重 | 一键 dHash 检测相似图片，滑块实时调整阈值 |
| 删除 | 选中后直接删除本地文件（不可恢复） |

---

## 去重原理

使用 **dHash（差值感知哈希）**：

1. 将图片缩放到 17×16 灰度图
2. 比较相邻列像素差异，生成 256 位哈希
3. 两张图哈希的汉明距离 ≤ 阈值 → 判定为相似
4. 相似组内保留分数最高的，其余标记为重复

拖动「Sim」滑块可实时重算，阈值越小越严格。

---

## 依赖

| 组件 | 需要的包 |
|------|----------|
| 前端（核心） | 无，纯浏览器，推荐 Chrome / Edge |
| app.py（可选） | `flask`, `pillow` |
