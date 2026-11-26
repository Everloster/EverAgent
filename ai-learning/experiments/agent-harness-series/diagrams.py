"""Generate engineering teaching diagrams as PNG and SVG, without a browser."""
import argparse
import html
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

parser = argparse.ArgumentParser()
parser.add_argument("--font")
args = parser.parse_args()
candidates = [args.font, "/System/Library/Fonts/STHeiti Light.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "C:/Windows/Fonts/msyh.ttc"]
font_path = next((p for p in candidates if p and Path(p).is_file()), None)
if not font_path:
    raise SystemExit("Specify a CJK font with --font")
OUT = Path(__file__).resolve().parents[2] / "reports/paper_assets/agent-yanyi"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1600, 1080
BG, INK, MUTED = "#f5f7fb", "#172a40", "#43546a"


class Diagram:
    def __init__(self, title, subtitle):
        self.im = Image.new("RGB", (W, H), BG)
        self.draw = ImageDraw.Draw(self.im)
        self.svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="1600" height="1080" fill="{BG}"/>']
        self.text(65, 45, title, 48)
        self.text(65, 110, subtitle, 27, MUTED)

    def text(self, x, y, value, size=30, color=INK):
        font = ImageFont.truetype(font_path, size)
        self.draw.text((x, y), value, font=font, fill=color)
        self.svg.append(f'<text x="{x}" y="{y+size}" fill="{color}" font-size="{size}" font-family="Noto Sans CJK SC,Heiti SC,Microsoft YaHei,sans-serif">{html.escape(value)}</text>')

    def box(self, x, y, w, h, title, lines, fill="#ffffff"):
        self.draw.rounded_rectangle((x, y, x+w, y+h), 18, fill=fill, outline="#bac8d8", width=2)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{fill}" stroke="#bac8d8" stroke-width="2"/>')
        self.text(x+22, y+16, title, 32)
        for index, line in enumerate(lines):
            self.text(x+22, y+65+index*40, line, 26, MUTED)

    def arrow(self, x1, y1, x2, y2, label=""):
        self.draw.line((x1,y1,x2,y2), fill="#3269a8", width=4)
        angle = math.atan2(y2-y1, x2-x1)
        points = [(x2,y2), (x2-17*math.cos(angle-0.45), y2-17*math.sin(angle-0.45)), (x2-17*math.cos(angle+0.45), y2-17*math.sin(angle+0.45))]
        self.draw.polygon(points, fill="#3269a8")
        self.svg.append(f'<path d="M {x1} {y1} L {x2} {y2}" fill="none" stroke="#3269a8" stroke-width="4"/><polygon points="'+" ".join(f"{x},{y}" for x,y in points)+'" fill="#3269a8"/>')
        if label:
            self.text((x1+x2)/2+18, (y1+y2)/2-18, label, 24, MUTED)

    def save(self, name, note):
        self.text(65, 990, note, 24, MUTED)
        self.im.save(OUT/(name+".png"))
        (OUT/(name+".svg")).write_text("\n".join(self.svg)+"\n</svg>\n")


d = Diagram("四层接口，四种状态归属", "同一聊天页面并不保证原生会话、模型上下文或缓存相同")
layers = [
    ("产品客户端", ["聊天、终端、模型选择、审批与 diff", "保存界面状态；向服务端提交操作"], "#e7f0ff"),
    ("Orca / T3 控制层", ["任务 / thread、事件、投递回执、历史交接", "管理工作区与 Agent 进程；不持有模型权重"], "#edf6ed"),
    ("Agent harness", ["Codex app-server / Claude SDK / ACP agent", "原生会话、工具循环、权限及运行中任务"], "#fff4dc"),
    ("模型服务", ["模型 API、推理项、prompt cache 与服务端执行", "能否复用取决于具体模型、请求和接口条件"], "#f1eafa"),
]
for i, (title, lines, fill) in enumerate(layers):
    y=180+i*185; d.box(70,y,1040,150,title,lines,fill)
    if i<3: d.arrow(1180,y+85,1180,y+185+60, ["客户端 RPC","原生控制协议","模型 API"][i])
d.save("ownership", "依据固定源码与官方接口自绘；箭头表示控制调用，不表示状态可以自由迁移。")

d = Diagram("Orca：任务派发与消息投递", "Task 表达工作；Dispatch 表达一次派发；Worker 和原生 session 承担执行")
d.box(60,190,430,165,"预建任务 DAG",["实现 → 测试 → 审查","拆解由人或 Agent 建立"])
d.box(590,190,430,165,"Coordinator",["检查依赖、并发与可用 worker","创建 Dispatch，再投递任务"])
d.box(1120,190,420,165,"Worker / Harness",["在指定工作区执行","以任务和派发身份回报"])
d.arrow(490,275,590,275);d.arrow(1020,275,1120,275)
d.box(130,510,560,220,"任务状态与回报",["worker_done / escalation","decision gate；当前派发与进程身份","一次派发结束，不等于工作区已合并"],"#edf6ed")
d.box(860,510,560,220,"消息通道",["结构化聊天：明确的 steer / queue 路径","终端：PTY 写入，行为还取决于 TUI","回执、实际消费与完成分别观察"],"#e7f0ff")
d.arrow(1310,355,1310,510);d.arrow(1050,760,1050,810)
d.text(185,850,"消息、任务、进程各有生命周期；状态不明时需要证据，不能直接重复执行。",31)
d.save("orca-flow", "本卷分析的是固定版本实现；Coordinator 的 decompose() 在该版本要求预建任务。")

d = Diagram("T3：Claude → Codex → Claude", "应用 thread 连续；原生 provider 会话各自恢复或新建")
for x,title,lines,fill in [(60,"Run 1 · Claude",["原生 A 保存自己的上下文","任务：设计搜索功能"],"#fff4dc"),(590,"Run 2 · Codex",["目标 B 接收预算内历史","任务：实现并测试"],"#e7f0ff"),(1120,"Run 3 · Claude",["A 可恢复时补入缺失历史","任务：审查改动"],"#fff4dc")]:d.box(x,190,420,175,title,lines,fill)
d.arrow(480,280,590,280);d.arrow(1010,280,1120,280)
d.box(70,485,710,210,"T3 持久化 thread",["跨 provider 的可见消息、活动与交接记录","首次目标：预算内的历史选择","返回目标：从最后已投递 run 补齐增量"],"#edf6ed")
d.box(870,485,660,210,"原生 A / B",["会话存在、身份兼容时尝试原生恢复","无法恢复时，以新会话和历史接力","历史条目不重放原生工具 / 推理状态"])
d.arrow(270,365,270,485);d.arrow(800,365,800,440);d.arrow(1320,365,1320,485)
d.text(85,825,"历史被选中 ≠ 已投递；已投递 ≠ 新模型一定遵守所有约束。",32)
d.text(85,880,"交接记录保留覆盖范围、遗漏项和实际投递状态，供恢复与检索。",29)
d.save("t3-relay", "A → B → A 是教学示意；恢复、增量、预算和失败路径须分别满足条件。")

d = Diagram("缓存判断：沿实际请求检查", "保留 session ID、进程或聊天记录，都不能单独证明缓存命中")
d.box(75,200,620,195,"先看输入",["系统与工具定义、历史内容、排序","模型与推理配置是否改变前缀","交接文本、压缩与时间戳是否插入"],"#e7f0ff")
d.box(900,200,620,195,"再看服务端条件",["符合模型支持的缓存边界","找到兼容缓存条目及可用执行节点","满足有效期、路由和账户等条件"],"#fff4dc")
d.arrow(695,295,900,295)
d.box(75,550,620,220,"本地可观察",["thread / 原生 session 身份","发给 harness 的内容和协议事件","provider 暴露的 usage 统计"],"#edf6ed")
d.box(900,550,620,220,"模型侧需测量",["缓存读、缓存写、普通输入的数量","统一口径下的实际输入费用","请求延迟与完整任务表现"],"#f1eafa")
d.arrow(1210,395,1210,550)
d.text(90,855,"离线探针可以解释请求为什么变化；真实命中、费用与延迟需要实际调用。",30)
d.save("cache-boundary", "本卷没有真实模型调用；图不表示某个切换操作一定命中或一定失效。")
