# 穿越机视频skill

让建筑、园区与场景漫游具有穿越机的目标、节奏与空间关系，同时保留可检查的运动、渲染和交付证据。

- 显示名称：**穿越机视频skill**。
- 技能目录与调用名：`skills/fpv-video`、`$fpv-video`。
- 核心入口：[SKILL.md](skills/fpv-video/SKILL.md)。
- 公开过程案例：[长丰案例](examples/changfeng/case.md)，包含失败与未验收边界，不是已获用户认可的作品展示。

本次更新纳入长丰R5的原站材质核验、全场景非树审计、局部地面/法线修复、诊断阴影缓存及新增林带的全镜头原生重渲染方法。R5仅完成本地技术交付，正常速度音画与外观仍待人工验收；仓库不提供工程、图片或视频。详见[原生场景修复](skills/fpv-video/references/native-scene-repair.md)。另同步[视觉包装](skills/fpv-video/references/editorial-design.md)与[视频生视频研究](skills/fpv-video/references/video-to-video-consistency.md)，后者是固定版本的静态研究，不是已实跑执行器。

## 使用

将 `skills/fpv-video` 文件夹安装到所用助手支持的技能目录，然后调用：

> 使用 $fpv-video，为我的园区规划一条具有目标与节奏的穿越机航线。先提供新方案供确认，不继承已被否决的旧运镜，不启动正式渲染。

技能不依赖特定 DCC，也不自动安装、启动或接管 Unreal Engine、Blender。原生 API 与版本行为须在实际环境核验。公开分享授权不等于允许上传私有工程或第三方资产。

## 独立合成示例

只需 Python 3 标准库；没有模型、纹理、树、视频、音频或原工程数据。生成器以解析曲线与抽象门洞演示弧长重采样、姿态与边界检查，不会连接 DCC 或网络。

```bash
python3 skills/fpv-video/scripts/synthetic_route.py --output abstract-route.json
python3 -m unittest discover -s skills/fpv-video/scripts -p 'test_*.py' -v
```

输出为独立 JSON 数据，不是 UE/Blender 可直接交付的相机工程。几何数值检查不证明镜头好看、素材可发布或真实场景安全；门洞检查也只针对示例中的直线段与轴对齐开口。

## 发布与授权范围

MIT 仅适用于本仓库新编写的文档与代码。原长丰场景、源模型、NoAI 树、贴图、音乐、视频、原生工程与内部日志均未包含，不因本仓库授权而获得任何使用权。实际制作请使用自有或明确获授权素材，逐项记录来源和许可证；标为 CC0 的素材也需核对具体来源与许可范围。

已阅读并记录 ETH-ASL、Gyroflow、BlenderPad 的固定版本与源码方法，见[GitHub 方法研究](skills/fpv-video/references/github-methods.md)。仅做方法学习，未安装运行或复制第三方实现，不能称这些外部系统已经在本地调试可用。

© 2026 Nankong 版权所有。本仓库既有原创文档和代码继续按MIT授权，不能将“仅供技术交流”的项目素材边界写成收回MIT商用权。未随包的项目与第三方素材不获新增许可；需要另行核实权利及用途。公开同步前应审核文件白名单、隐私模式、提交元数据和将推送的历史，不能只凭 `.gitignore` 判断安全。
