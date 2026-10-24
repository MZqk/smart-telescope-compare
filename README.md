# smart-telescope-compare · 智能望远镜参数对比

DWARFLAB 与 ZWO Seestar 共 **7 款智能望远镜**、**65 项参数**的横向对比。主体是一张单文件 HTML 表格，并可导出 PDF / DOCX 两个分发版本。

| 品牌 | 机型 |
| --- | --- |
| DWARFLAB | DWARF 3 · DWARF mini · DWARF Draco |
| ZWO | Seestar S30 · Seestar S30 Pro · Seestar S50 · Seestar S50 Pro |

对比维度覆盖光学（口径、焦距、焦比、镜片结构）、传感器（型号、尺寸、像素、读噪、满阱、QE）、机械与跟踪、成像模式、存储与连接、供电与重量等。存在差异的参数会被高亮，同值参数折叠为一行，方便快速定位选型差异点。

## 文件说明

| 文件 | 说明 |
| --- | --- |
| `telescope_compare.html` | **数据源头兼主交付**。单文件表格，数据内嵌在最后一个 `<script>` 块中，双击即可在浏览器打开 |
| `data.json` | 从 HTML 抽取出的结构化数据（`DATA.headers` / `DATA.rows` / 若干校订常量），供脚本消费 |
| `7 款智能望远镜参数对比表.pdf` | A4 横向打印版，按差异度分节排版 |
| `telescope_compare.docx` | Word 版，便于二次编辑 |
| `sensor_comparison.html` | 传感器规格专项对比页 |
| `build_docs.py` | 由 `data.json` 生成 PDF + DOCX |
| `extract.js` | 由 HTML 抽取 `data.json` |
| `dom.html` | 早期抓取的页面 DOM，保留作数据溯源参考 |
| `starun.css` / `geist_check.css` | 版式基础样式 |

## 查看

直接用浏览器打开 `telescope_compare.html`，无需构建、无需服务端。

## 重新生成

数据流向是 **HTML → data.json → PDF/DOCX**，HTML 是唯一数据源头：

```bash
# 1. 从 HTML 抽取结构化数据
node extract.js            # 输出 data.json

# 2. 由 data.json 生成分发文档
pip install reportlab python-docx
python build_docs.py       # 输出 PDF 与 DOCX
```

两个脚本都使用相对路径，可在任意目录克隆后直接运行。

## 数据说明

原始数据由 **Linea松果** 提供。Seestar S50 Pro、S30 Pro 与 S50 的参数依据 ZWO / Seestar、Sony 官方资料复核（2026-08-27），S50 Pro 于 2026-09-10 二次复核（长焦 OmniVision OS08B10、广角 Sony IMX586；读噪 / 满阱 / QE 官方未公开，依芯片规格标注）。DWARFLAB Draco 依据 DWARFLAB 官方产品页规格表录入（2026-09-10）。

表中标注「芯片规格 / 官方规格」者来自传感器或厂商公开资料；标注「几何换算」者为口径焦距推算值；「—（官方未公开）」表示厂商未披露。参数以厂商标称为准，实测值可能存在偏差，选型前建议以最新官方页面为准。

## 许可

仓库尚未附带许可证文件。在对外分发或引用前请先补充 LICENSE，并确认原始数据提供方的授权范围。
