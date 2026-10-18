# GitHub 方法研究

核验日期：2026-10-19。以下通过上游 GitHub 仓库、固定 commit、许可证元数据与相应源码阅读核验；没有安装或运行这些上游系统，没有拷贝其实现到本技能。它们解决不同问题，不是可以一键生成电影镜头的同类软件。

| 项目与固定版本 | 阅读位置、许可 | 可借鉴的方法 | 迁移边界 |
| --- | --- | --- | --- |
| [ETH-ASL mav_trajectory_generation](https://github.com/ethz-asl/mav_trajectory_generation/tree/7aeebd9f819217502fd1c5489da49efadf90d411) | README 与 `polynomial_optimization_nonlinear.h`；Apache-2.0 | 将位置及其导数约束交给多项式优化，分配段落时间，显式限制运动幅值 | 规划优化与电影构图不同；不能因路径光滑就默认可穿真实建筑。此仓基于 ROS，不是本技能内置依赖 |
| [Gyroflow](https://github.com/gyroflow/gyroflow/tree/5fa0309a17ecd682d87746cf37d8dde333915f1a) | `src/core/smoothing/default_algo.rs`；仓库标 GPL-3.0，所读文件 SPDX 为 GPL-3.0-or-later | 根据角速度调整平滑程度，使用四元数球面插值及双向处理，允许分轴/关键帧控制 | 是陀螺数据视频稳定器，不是生成航线；虚拟相机可独立设计平滑逻辑，不能直接吞掉有意的银行角或机械套用裁切补偿 |
| [BlenderPad](https://github.com/Zouares/blenderpad/tree/d0d074325e5ed8988c446776a6dbe46a1d652dd3) | `blenderpad/modes/drone.py`；GPL-3.0 | 手柄输入目标速度，经惯性状态滤波后移动，支持高度保持和相机自动插关键帧 | 适合手动表演/快速预演。所读 tick 实现是每次调用累加，不应误称严格按秒积分；离线制作需重新按实际时间重采样、检查碰撞与镜头节奏 |

## 在制作中如何用

1. 先制定主体、开口、遮挡揭示和加减速节奏，再求平滑轨迹。导数连续性是一项工程约束，不是审美目标本身。
2. 将路线位置、机体银行角、视线预看量分层调节。借鉴自适应姿态平滑，但保留设计过的转弯力度。
3. 可手柄录制意图，再拟合和校验。不能把原始 tick 数当视频时间，也不能在未经审核的项目上安装插件或控制相机。
4. 所有参考方法都需在当前 DCC 版本和获准素材上做独立小样。引用方法不等于取得其代码、素材或第三方依赖的重新许可。

本技能的 `synthetic_route.py` 为独立解析示例，未实现或复制上述上游求解器/稳定器；示例测试不证明这些外部项目已安装可用。
