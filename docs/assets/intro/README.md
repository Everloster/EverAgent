# README 介绍动画

`../everagent-intro.webp` 是根目录 README 首屏的介绍动画：无声、循环播放，约 54 秒。开启“减少动态效果”的访客会看到静态全景图 `../everagent-horizontal.jpg`。

| 文件 | 作用 |
|---|---|
| `intro.html` | 动画源文件：画面、上屏文案和逐帧时间线都在这里，可直接用浏览器打开查看 |
| `build.mjs` | 逐帧截图 `intro.html`，合并相同帧后编码为循环 WebP |

## 修改与重新生成

在仓库根目录执行：

```bash
node docs/assets/intro/build.mjs --stills /tmp/intro-stills --preview /tmp/intro.mp4
```

依赖 Node.js 18+、Playwright（含 Chromium）和 libwebp 的 `img2webp`；`--preview` 另需 ffmpeg。字体使用 macOS 自带的 PingFang SC、Hoefler Text 和 Avenir Next，在其他系统上生成会回退字体、改变画面。

修改时注意：

- **文案**：只写仓库里能核对、不会随数量增长而过时的说法，例如 500+、300+、“自 2026 年 3 月起”。不写精确篇数或评分，证据与复核记录要带上适用范围。
- **动效**：只做局部元素入场，背景保持静止，换屏先淡出到空背景再淡入。全屏运动或照片推拉会让体积成倍增长。
- **循环**：时间线的最后一段必须回到第 0 帧的标题卡；脚本会检查这一点，并让首尾两帧完全相同。
- **体积**：当前约 2.5 MB，重新生成后不要超过 3 MB，并检查 `--stills` 输出的截图。
