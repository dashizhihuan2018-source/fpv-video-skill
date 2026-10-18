# GitHub 运镜研究与可迁移方法

研究日期：2026-10-19。以下 commit 是本次核验快照，不代表最新版本或已在目标 DCC 中运行。按问题选方法，不按 star 排名，不为一次镜头任务引入整个飞控或稳定软件。

## 先证明来源，再提炼方法

1. 搜索只用于发现候选；回到原作者/组织仓核对 owner、默认分支、README、实际源码和根 LICENSE。固定完整 commit，记录源码路径、函数及其实际解决的问题。
2. API 自动 license 字段可能为 `NOASSERTION`，应检查固定 commit 的根许可；不能据此断言无许可。归档标志也不能代替 README 中的迁移/冻结维护声明。
3. 收到原始字节才记录内容 SHA256；终端超时、API 限流与浏览器文本核验分别记录，不能把可读网页冒充本地原字节哈希。搜索片段和 404 旧链接不是实现证据。
4. 分清原理借鉴、代码移植、目标引擎构建、原生运行与画面验收。检查具体文件、附加许可和依赖；自有文档 MIT 不覆盖复制的 GPL 源码。

## 本次核验的上游快照

| 官方仓与固定 commit | 许可快照 | 有用的源码与边界 |
| --- | --- | --- |
| [microsoft/AirSim](https://github.com/microsoft/AirSim/tree/1ca93f6f77e4e8a39b2b241c1fe2764da4d7dd41) | 根 MIT | `RecordingFile.cpp`：记录行与图像绑定；`RecordInterval`、`RecordOnMove`；NED/SI 转换。记录系统不是电影运镜优化器。 |
| [uzh-rpg/flightmare](https://github.com/uzh-rpg/flightmare/tree/d4218aedac18cbe9364a0a0df10ab992c4b65e4f) | 根 MIT | `QuadrotorDynamics`、`UnityBridge`：位置、姿态、角速度和渲染分层；`positionRos2Unity`/`quaternionRos2Unity`。物理姿态不等于导演视线。 |
| [ethz-asl/mav_trajectory_generation](https://github.com/ethz-asl/mav_trajectory_generation/tree/7aeebd9f819217502fd1c5489da49efadf90d411) | Apache-2.0 | minimum-snap、导数连续、时间分配、导数约束；snap 常用 N≥10 个系数，不是 10 阶多项式。不自动解决碰撞或构图。 |
| [gyroflow/gyroflow](https://github.com/gyroflow/gyroflow/tree/5fa0309a17ecd682d87746cf37d8dde333915f1a) | 根 GPL-3.0 及特定附加许可；`plain.rs` SPDX GPL-3.0-or-later | `plain.rs` 按采样率计算时间常数、前后向 SLERP。只平滑方向，不修位置穿模；双向是离线方法。不能拖偏门洞对准锚点或消掉有意侧倾。 |
| [betaflight/blackbox-log-viewer](https://github.com/betaflight/blackbox-log-viewer/tree/a84755c5e897c1a3a580424b64c0df066c12c6b4) | GPL-3.0 | 时间戳 parser、IMU gyro/acc/dt 融合；不是无漂移 XYZ 重建。README 说明 standalone 冻结、维护转入 Betaflight App。 |
| [alzin/SkyPath](https://github.com/alzin/SkyPath/tree/a6e74036fc684ee5f15a171ac2b3a198657dcfd9) | MIT | `PATTERNS`、`lookAt(headPos)` 是主体跟踪教学参考；固定每帧 lerp 不具帧率无关性，也不保证净空或电影效果。 |

`globglob3D/DroneCam` 官方页/API 本次返回 404，不作为可用仓推荐。以上只是方法研究，没有运行上游框架或测试目标引擎兼容性。

## 迁移到镜头设计

- 分离空间路径 `p(s)`、速度包络 `s(t)`、视线/倾斜 `q(t)` 和真实输出 clock。弧长映射避免参数速度假象，不要求全片恒速。关注 C2、jerk/snap；不要默认每段端点速度归零。
- 核对长度预算：4 秒、平均 11 m/s 需要约 44 m 可行走廊。空间不足就调整时长/速度/形状，不移动受限资产或缩安全量。
- 协调转弯粗略量级 `R=v²/(g*tan(bank))`：20 m/s、30° 约需 70.6 m 半径。若 bank 只是虚拟镜头参数应明确，不伪称完整飞行动力学。
- 入弯预看、开口前稳定视线是导演约束。目标用连续权重过渡；门洞对准和水平穿越锚点不能被全局平滑拖偏。短回望后平滑回接，不突然 180° 掉头。
- 定向平滑需要四元数连续半球；按真实 `dt` 使用 `alpha=1-exp(-dt/tau)`。固定每帧系数随帧率改变响应。平滑后复验角速度、锚点和实际引擎插值，不只检查输入键。
- 世界 Z 不等于 AGL，后者需要连续地面支撑/高度证据；开放车棚结构通道不等于封闭主楼室内。

完整方法仍需获准几何/元数据、项目尺度、原生观测及正常速度人工观看；源码已读不代表依赖、性能、兼容性或成片已验收。
