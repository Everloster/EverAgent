# 精选播客清单

> 58 档精选播客（56 档附公开 RSS）。近期更新看[历史速看表](../PODCAST_UPDATES.md)；更早的单集见 [show-indexes/](./show-indexes/)，按下面的更新规则刷新。
> 源文件：[curated-podcasts.opml](./curated-podcasts.opml)（OPML 2.0，可导入任意播客客户端）。
> 中英文 SOTA AI 技术节目使用独立的 [`ai-tech-podcast-radar`](../skills/ai-tech-podcast-radar/SKILL.md)；它按技术相关性与已学习状态筛选，不改变这份个人综合精选。
> 收录：2026-08-23 首批 51 档（小宇宙 OPML 导出）；2026-09-25 增补 7 档——小宇宙 OPML 导出对分享合集中部分节目会丢档（本次丢 7 档），经「我也在听的品质播客」collection 链接 API 补齐，其中 5 档 RSS 由 Apple iTunes 反查，2 档（窦文涛的聊客、职场有话说）小宇宙独播未暴露公开 feed、待补。

## 查看近期更新

固定阅读入口是 [小宇宙精选播客历史速看表](../PODCAST_UPDATES.md)。每次查询更新这份文件，再向用户汇报新增内容；不另建按天重复的清单。

- 先读上次检查日期、已收录条目和获取缺口。默认查最近一周；间隔超过一周时，从上次检查前两天补查。用户指定时间范围时按该范围获取，短时间刷新仍保留旧条目。
- 联网遵守根协议的 Token Plan-first：先用 eacli 读取公开订阅或节目页。XML 丢失、截断或读取失败时才降级到公开 RSS，并记录原因；已有 `fetch_show_indexes.py` 的直接 HTTP 获取只用于这种降级。临时 RSS、shownotes 和调用结果放 `/tmp`。
- 节目来源沿用本页与 OPML，已有详细单集索引继续复用；无公开 RSS 的节目查公开节目页，用绝对日期核对更新。只查某一期时仅刷新目标节目；用户查“精选最近更新”时检查整份清单，不套用 SOTA 技术播客雷达的主题过滤或精选数量上限。
- 按单集 URL 合并历史，可用时参考稳定 GUID；同一节目单集的跨平台入口核对后合并。同场串台在不同节目发布的版本可分别列出并互相注明，学习选题合并处理。订阅只保留近期内容时，不删除旧清单；拿不到新数据时保留旧记录并标明本轮获取失败。
- 速看表按节目分组、单集日期倒序，给出简短中文主题、发布日期、时长、原节目链接和学习报告链接。简介依据标题和官方 shownotes，不把尚未收听的内容写成已验证结论；缺少日期或时长就标待补，不用报告日期或转写长度猜测。
- 学习状态以 `reports/*.md` 的 `source_url/source_urls` 与完成状态为准。`completed/archived` 且确实对应本期才标“已学习”；草稿标“进行中”，仅主题相关时标“相关报告”。已有索引中的人工完成标记也须核对报告是否存在，已转写、已排队与日报提及不等于完成学习。
- 更新检查日期、覆盖范围、数量与获取情况；“未获取到近期条目”不写成“没有更新”。新完成或修订的报告补回原条目，不重复添加同一期。
- 对话中简述新增内容并附固定入口。默认只维护速看表，用户选定后再启动转写与深度学习。

## AI / 科技

| 节目 | RSS | 索引 |
|---|---|---|
| 张小珺Jùn｜商业访谈录 | [rss](https://feed.xyzfm.space/dk4yh3pkpjp3) | [show-indexes/zhangxiaojun](./show-indexes/zhangxiaojun.md) |
| 十字路口Crossing | [rss](https://feed.xyzfm.space/68fyjknth9hj) | [show-indexes/crossing](./show-indexes/crossing.md) |
| 此话当真 | [rss](https://feed.xyzfm.space/kf7lym7fc4e9) | [show-indexes/cihua-dangzhen](./show-indexes/cihua-dangzhen.md) |
| 硅基立场 | [rss](https://feed.xyzfm.space/hnetc83hllku) | [show-indexes/guiji-lichang](./show-indexes/guiji-lichang.md) |
| 赛博对话 | [rss](https://feed.xyzfm.space/v99nfxe349ny) | [show-indexes/saibo-duihua](./show-indexes/saibo-duihua.md) |
| 开始连接 LinkStart | [rss](https://feed.xyzfm.space/q9a6lueucj6a) | [show-indexes/linkstart](./show-indexes/linkstart.md) |
| AI炼金术 | [rss](https://www.ximalaya.com/album/74194808.xml) | [show-indexes/ai-lianjinshu](./show-indexes/ai-lianjinshu.md) |
| 42章经 | [rss](https://feed.xyzfm.space/evgg6xle9rdc) | [show-indexes/42zhangjing](./show-indexes/42zhangjing.md) |
| 信号与噪声 | [rss](https://feed.xyzfm.space/tmaapfx9v3hl) | [show-indexes/xinhao-yuzaosheng](./show-indexes/xinhao-yuzaosheng.md) |
| 硅谷101 | [rss](https://feeds.fireside.fm/sv101/rss) | [show-indexes/guigu101](./show-indexes/guigu101.md) |
| 101 Weekly | [rss](https://feeds.fireside.fm/101weekly/rss) | [show-indexes/101-weekly](./show-indexes/101-weekly.md) |
| 老talk消息 | [rss](https://www.ximalaya.com/album/31225613.xml) | [show-indexes/laotalk-xiaoxi](./show-indexes/laotalk-xiaoxi.md) |
| 大小马聊科技 | [rss](https://feed.xyzfm.space/ura8q9jpl4xj) | [show-indexes/daxiaoma-keji](./show-indexes/daxiaoma-keji.md) |
| 大小马智驾 | [rss](https://www.ximalaya.com/album/76366265.xml) | [show-indexes/daxiaoma-zhijia](./show-indexes/daxiaoma-zhijia.md) |
| 晚点聊 LateTalk | [rss](https://podcast.latepost.com/rss) | [show-indexes/wandian-latetalk](./show-indexes/wandian-latetalk.md) |
| 罗永浩的十字路口 | [rss](https://feed.xyzfm.space/wmnkvmrpwuww) | [show-indexes/luoyonghao-crossing](./show-indexes/luoyonghao-crossing.md) |
| 高能量 | [rss](https://feed.xyzfm.space/jhfuba3dahq8) | [show-indexes/gaonengliang](./show-indexes/gaonengliang.md) |
| 课代表立正 | [rss](https://feeds.transistor.fm/kedaibiao) | [show-indexes/kedaibiao-lizheng](./show-indexes/kedaibiao-lizheng.md) |
| 卫诗婕｜漫谈Light the Star | [rss](https://feed.xyzfm.space/4jjdlpq3khc9) | [show-indexes/weishijie](./show-indexes/weishijie.md) |
| 屠龙之术 | [rss](https://feed.xyzfm.space/834hyx3v9k74) | [show-indexes/tulong-zhishu](./show-indexes/tulong-zhishu.md) |

## 商业 / 投资 / 职场

| 节目 | RSS | 索引 |
|---|---|---|
| 疯投圈 | [rss](https://crazy.capital/feed) | [show-indexes/fengtouquan](./show-indexes/fengtouquan.md) |
| 知行小酒馆 | [rss](https://feed.xyzfm.space/j8yp8gxkmgqr) | [show-indexes/zhixing-xiaojiuguan](./show-indexes/zhixing-xiaojiuguan.md) |
| 组织进化论 | [rss](https://feed.xyzfm.space/wb9n7uukpubp) | [show-indexes/zuzhi-jinhualun](./show-indexes/zuzhi-jinhualun.md) |
| 半拿铁｜商业沉浮录 | [rss](https://feed.xyzfm.space/tcettvc3x689) | [show-indexes/bannatie](./show-indexes/bannatie.md) |
| 半拿铁·周刊 | [rss](https://feed.xyzfm.space/vylham8uw3ay) | [show-indexes/bannatie-zhoukan](./show-indexes/bannatie-zhoukan.md) |
| 半拿铁·故事篇 | [rss](https://www.ximalaya.com/album/83323735.xml) | [show-indexes/bannatie-gushipian](./show-indexes/bannatie-gushipian.md) |
| 商业就是这样 | [rss](http://www.ximalaya.com/album/46587439.xml) | [show-indexes/shangye-jiushi-zheyang](./show-indexes/shangye-jiushi-zheyang.md) |
| 起朱楼宴宾客 | [rss](https://feed.xyzfm.space/ahng8d9qlywl) | [show-indexes/qizhulou](./show-indexes/qizhulou.md) |
| 成为巴菲特｜价投村 | [rss](https://feed.xyzfm.space/w67gc9bantgx) | [show-indexes/chengwei-buffett](./show-indexes/chengwei-buffett.md) |
| 投资ABC | [rss](https://feed.xyzfm.space/9bmupxfae9qd) | [show-indexes/touzi-abc](./show-indexes/touzi-abc.md) |
| 二的三次方 | [rss](https://feed.xyzfm.space/8mwdbxbr4kck) | [show-indexes/erde-sancifang](./show-indexes/erde-sancifang.md) |
| 能者多唠｜商业原声 | [rss](https://feed.xyzfm.space/qlenc4cdh48c) | [show-indexes/nengzhe-duolao](./show-indexes/nengzhe-duolao.md) |
| 听懂涨声 | [rss](https://feed.xyzfm.space/lulbgftcj6vw) | [show-indexes/tingdong-zhangsheng](./show-indexes/tingdong-zhangsheng.md) |
| 梁将军商业内参 | [rss](https://feed.xyzfm.space/xquy9a67l9vy) | [show-indexes/liangjiangjun](./show-indexes/liangjiangjun.md) |
| 无人知晓 | [rss](https://feed.xyzfm.space/ypn9dydpbxpc) | [show-indexes/wurenzhixiao](./show-indexes/wurenzhixiao.md) |
| 乱翻书 | [rss](https://feed.xyzfm.space/yxuruh3f9mc4) | [show-indexes/luanfanshu](./show-indexes/luanfanshu.md) |
| 温柔一刀 | [rss](https://feed.xyzfm.space/vmpr88xy7qqg) | [show-indexes/wenrou-yidao](./show-indexes/wenrou-yidao.md) |
| 屠龙大实话 | [rss](https://feed.xyzfm.space/fp7wecdfhgyq) | [show-indexes/tulong-dashihua](./show-indexes/tulong-dashihua.md) |
| 面基 | [rss](https://feed.xyzfm.space/6hpdgggtxpxb) | [show-indexes/mianji](./show-indexes/mianji.md) |
| 全嘻嘻 | [rss](https://feed.xyzfm.space/ptewvlwcgb8n) | [show-indexes/quanxixi](./show-indexes/quanxixi.md) |
| 职场有话说 | [公开节目页](https://www.xiaoyuzhoufm.com/podcast/6391b9f7a07c5e0cda6c6fff)（未取得公开 RSS） | — |
| 姜Dora在此 | [rss](https://feed.xyzfm.space/pjq9hb8ggrjm) | [show-indexes/jiang-dora](./show-indexes/jiang-dora.md) |
| 是宇弦啊 | [rss](https://feed.xyzfm.space/guaamk8ml3cb) | [show-indexes/yuxian](./show-indexes/yuxian.md) |
| 一苒一刻 | 订阅返回 HTTP 410（2026-11-02 复查）；近期更新待核实 | [show-indexes/yiran-yike](./show-indexes/yiran-yike.md) |

## 泛文化 / 生活 / 健康

| 节目 | RSS | 索引 |
|---|---|---|
| 三五环 | [rss](https://feed.xyzfm.space/m3dda867gh7j) | [show-indexes/sanwuhuan](./show-indexes/sanwuhuan.md) |
| 声东击西 | [rss](https://www.etw.fm/rss) | [show-indexes/shengdong-jixi](./show-indexes/shengdong-jixi.md) |
| 忽左忽右 | [rss](https://feed.xyzfm.space/cv4bkgpuglwp) | [show-indexes/huzuo-huyou](./show-indexes/huzuo-huyou.md) |
| 声动早咖啡 | [rss](https://feed.xyzfm.space/q88qwmydeuw8) | [show-indexes/shengdong-zaokafei](./show-indexes/shengdong-zaokafei.md) |
| 纵横四海 | [rss](https://feed.xyzfm.space/jl8739ky8w9j) | [show-indexes/zongheng-sihai](./show-indexes/zongheng-sihai.md) |
| 李诞 | [rss](https://feed.xyzfm.space/l3c8em3l8hfn) | [show-indexes/lidan](./show-indexes/lidan.md) |
| 窦文涛的聊客 | [公开节目页](https://www.xiaoyuzhoufm.com/podcast/6a018752bc9b8779be53038b)（未取得公开 RSS） | — |
| 无尽的谈话♾️ | [rss](https://feed.xyzfm.space/6lpf4tv9pq4y) | [show-indexes/wujin-tanhua](./show-indexes/wujin-tanhua.md) |
| 人文清华播客：对话清华学者 | [rss](https://www.ximalaya.com/album/54649472.xml) | [show-indexes/renwen-qinghua](./show-indexes/renwen-qinghua.md) |
| Ready Go | [rss](https://www.ximalaya.com/album/82119659.xml) | [show-indexes/ready-go](./show-indexes/ready-go.md) |
| 天真不天真 | [rss](https://feed.xyzfm.space/mcklbwxjdvfu) | [show-indexes/tianzhen-butianzhen](./show-indexes/tianzhen-butianzhen.md) |
| 第一推动 | [rss](https://feed.xyzfm.space/ndyjpcapc6fc) | [show-indexes/diyi-tuidong](./show-indexes/diyi-tuidong.md) |
| 菠萝健康派 | [rss](https://feed.xyzfm.space/qe8egag9eycv) | [show-indexes/boluo-jiankang](./show-indexes/boluo-jiankang.md) |
| 说医解药 | [rss](https://feed.xyzfm.space/34eqplbv6ptd) | [show-indexes/shuoyi-jieyao](./show-indexes/shuoyi-jieyao.md) |

> 分类为粗归并，可按需调整。收听历史/播放进度不在此列（服务端数据，需另行申请导出）。
