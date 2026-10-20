---
name: fpv-video
description: 规划、制作或诊断建筑与场景的穿越机视频，覆盖航线叙事、连续运动、净空、原生时序、视频生视频与多镜头风格一致性。适用于 FPV 飞行镜头，不用于把普通慢速漫游直接包装成已验收穿越机成片。
---

# 穿越机视频skill

先让镜头回答“飞向什么、为什么转弯、何时揭示空间”，再解决运动与渲染。技术通过和用户喜欢运镜是两道不同的门。

## 先确认航线

读取本次任务的真实约束、素材权限和用户最近一次视觉反馈。已经否决的运镜不是可继续润色的默认基线：先给出新的目标、段落、速度变化、穿越点、转向、lead-in / lead-out 和结尾方案；获得确认后再做成本较高的正式制作。没有旧方案时，按任务风险选择轻量预览或分镜确认，不机械要求每一步都审批。

区分机体朝向与视线目标：机体沿航向并随曲率倾斜，视线可以预看转弯、追踪主体或短暂回望，随后平滑回接。不把随机抖动、恒定倾斜或全程高速等同 FPV；回望不能掩盖路线缺乏目的。

用户已选定方案并明确要求后续自行完成时，在该次任务已授权范围内继续制作与检查，不重复索要段落或渲染确认。该授权不等于扩大资产读取、上传、付费、发布或人工视觉验收权限，也不是其他任务永久免确认。

## 按工作阶段读取

- 航线、速度、姿态、净空设计：读 [references/flight-design.md](references/flight-design.md)。
- 从开源项目研究 FPV 方法、筛选实现或记录检索证据：读 [references/github-motion-research.md](references/github-motion-research.md)。
- DCC 集成、版本坑、原生观测、MRQ 与证据冻结：读 [references/native-verification.md](references/native-verification.md)。
- 成片包装、人工验收与素材公开边界：读 [references/delivery.md](references/delivery.md)。
- 海报、成果视频、链接二维码或公有Git同步：再读 [references/public-sharing.md](references/public-sharing.md)，分别核查媒体权利、脱敏范围、真实完成层级与访客可见状态。
- 封面、字幕、转场、软件调色或生成式重制：读 [references/editorial-design.md](references/editorial-design.md)，先处理最近一次视觉否决及当前参考图。
- 现有 FPV 视频转视频、跨镜头统一外观或筛选视频编辑项目：再读 [references/video-to-video-consistency.md](references/video-to-video-consistency.md)，分开验证原运动保持、段内时序和段间风格；研究候选不等于已实测执行器。
- 黑材质、暗车棚、地面缺失或重复表面：读 [references/native-verification.md](references/native-verification.md) 的“画面缺陷回归”，定位原生对象后再修复；不要把后期提亮或成功编码当作修好。
- 原站材质迁入、全场景黑面审计、局部地面恢复或新增林带：再读 [references/native-scene-repair.md](references/native-scene-repair.md)，区分加载器实际路径、源几何与渲染数据、诊断缓存和正式渲染。
- 需要学习开源轨迹、手柄预演或姿态平滑方法：读 [references/github-methods.md](references/github-methods.md)，注意固定 commit 与运行未验证边界。

需要小型可运行示例时，使用 `scripts/synthetic_route.py` 和对应测试。它只创建独立解析曲线与抽象门洞，没有原工程几何，不是完整飞控、DCC 接口或电影级镜头生成器。参数须按项目选取，不把示例时长或阈值变成通用要求。

## 不可混淆的完成层级

分别报告：方案已确认；离线运动检查；原生构建与 fresh readback；实际渲染帧；编码与完整解码；人工正常速度视听验收；发布及访客可见。一个层级的成功不能替代后续层级。失败记录和源资产应保留，新修复使用可回退候选，不覆盖已成功证据来“补齐”结果。

生成式重制还需区分单镜头改善与跨镜头一致性：全片共用认可的外观参考，各镜头保留自己的源视频与构图；同提示词、同 seed 或一段漂亮样片不能证明整片已通过。

若素材禁止 AI 查看像素、几何或纹理，只在获准的元数据范围工作；需 AI 视觉诊断时，必须先证明允许查看的诊断画面已实际排除受限内容。隐藏截图不是授权读取受限几何或打包公开。完整受限画面交给人工，无法满足时明确停止该检查。

公开参考案例位于仓库 `examples/changfeng/case.md`；它是过程与故障总结，不包含源资产或已验收视觉证明，也不是技能运行依赖。
