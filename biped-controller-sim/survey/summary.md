# 이족보행 로봇 제어기 시뮬레이션 GitHub 저장소 요약 (2026-11-20)

전체 목록은 [biped_controller_sim_repos.xlsx](biped_controller_sim_repos.xlsx)에 있습니다 (본 목록 1269개, 이 중 ★ 우선 372개). 아래는 스타 수 기준 상위 일부입니다.

- 시뮬레이터와 제어 방식은 README와 설명에 해당 단어가 실제로 나오는지 확인한 결과입니다. 코드를 직접 읽어 판정한 것은 아닙니다.
- 검색 범위: GitHub 검색어 116개(스타순 상위 최대 300건씩) + 웹 검색 5회. 검색어 전체는 xlsx의 '안내' 시트에 있습니다.

## 1. PyBullet 기반 (상위 25)
| 저장소 | 시뮬레이터 | 제어 방식 (README 키워드) | 언어 | ★ | 갱신 | 설명(원문) |
|---|---|---|---|---|---|---|
| [upkie/upkie](https://github.com/upkie/upkie) | PyBullet, MuJoCo | MPC, Inverted pendulum, RL | Python | 465 | 2026-11-03 | Open-source wheeled biped robots |
| [isri-aist/CentroidalControlCollection](https://github.com/isri-aist/CentroidalControlCollection) | PyBullet, ROS | MPC, ZMP, Preview control, DCM | C++ | 91 | 2025-10-23 | Collection of centroidal control for legged robots |
| [Einsbon/bipedal-robot-walking-simulation](https://github.com/Einsbon/bipedal-robot-walking-simulation) | PyBullet | Inverse kinematics | Python | 90 | 2019-06-01 | bipedal robot walking simulation using pybullet. |
| [haruki1526/LeggedRobotsForBullet](https://github.com/haruki1526/LeggedRobotsForBullet) | PyBullet | Preview control, Inverse kinematics | Python | 70 | 2021-01-17 | Bipedal and Quadrupedal Walking Robot in PyBullet |
| [DarrenLevine/TipTap](https://github.com/DarrenLevine/TipTap) | PyBullet |  | Python | 65 | 2020-10-05 | A 3d-printed bipedal robot. A low-cost desktop option for semi-direct drive walking resear |
| [junhyeokahn/PyPnC](https://github.com/junhyeokahn/PyPnC) | PyBullet | DCM | C++ | 60 | 2024-02-27 | Python Implementation of Planning and Control |
| [Simple-Robotics/simple-mpc](https://github.com/Simple-Robotics/simple-mpc) | PyBullet | MPC, TSID | C++ | 48 | 2026-10-06 | C++ implementation of multiple predictive control schemes for locomotion based on the Alig |
| [moribots/plen_ml_walk](https://github.com/moribots/plen_ml_walk) | PyBullet, Gazebo, ROS | ZMP, Inverse kinematics, RL | Python | 37 | 2020-03-21 | A PLEN2 Robot learns to walk using Twin-Delayed Deep Deterministic Policy Gradient in Gaze |
| [TheMarex/libbipedal](https://github.com/TheMarex/libbipedal) | PyBullet | ZMP, LIPM, Preview control, Capture point | C++ | 30 | 2014-12-25 | Library for bipedal walking algorithms for pattern generation and stabilization |
| [gokulp01/meta-qlearning-humanoid](https://github.com/gokulp01/meta-qlearning-humanoid) | PyBullet, MuJoCo | RL | Python | 28 | 2024-08-21 | Meta QLearning experiments to optimize robot walking patterns  |
| [rdesarz/biped-walking-controller](https://github.com/rdesarz/biped-walking-controller) | PyBullet | MPC, ZMP, LIPM, Inverted pendulum, Preview control, Trajectory optimization, Inverse kinematics | Python | 23 | 2026-04-23 | A Python implementation of a walking controller using ZMP preview control for humanoid rob |
| [Anthony-ZC/Robotic_Studio_Bipedal_Robot](https://github.com/Anthony-ZC/Robotic_Studio_Bipedal_Robot) | PyBullet |  | Python | 22 | 2025-09-29 | Columbia Robot Studio Project Implementation: Code, CAD,  3mf, etc |
| [limxdynamics/tron1-robot-description](https://github.com/limxdynamics/tron1-robot-description) | PyBullet, MuJoCo, Gazebo, Isaac Gym, Isaac Sim/Lab, ROS |  | CMake | 21 | 2026-11-05 | URDF/Xacro robot models for TRON1 — ROS 1/2, MuJoCo & simulation ready |
| [UBCMOCCA/mocca_envs](https://github.com/UBCMOCCA/mocca_envs) | PyBullet |  | Python | 18 | 2020-12-03 |  |
| [citbrains/GankenKun_webots](https://github.com/citbrains/GankenKun_webots) | PyBullet, Webots | Preview control | C | 18 | 2024-05-30 | Control of humanoid robots on webots, walking, deep-learning, Bayesian-optimization |
| [nopaddleboat/generate-humanoid-walking-gaits](https://github.com/nopaddleboat/generate-humanoid-walking-gaits) | PyBullet, Drake |  | Python | 15 | 2023-08-31 | This repository shows how to follow the guidelines from Pinocchio to generate walking gait |
| [tayalmanan28/Biped-Pybullet](https://github.com/tayalmanan28/Biped-Pybullet) | PyBullet |  | Python | 13 | 2022-06-23 | This is a Biped simulated on pybullet physics engine, walking |
| [citbrains/GankenKun_pybullet](https://github.com/citbrains/GankenKun_pybullet) | PyBullet | Preview control, Inverse kinematics | Python | 13 | 2021-10-31 | Walking Pattern Generator |
| [lok-i/BlackBird-gym](https://github.com/lok-i/BlackBird-gym) | PyBullet | RL | Python | 12 | 2020-01-05 | Reinforcement Learning framework for Bipedal robots using the OpenAI Gym environment and P |
| [haritsahm/sepakbola-humanoid-learning-path](https://github.com/haritsahm/sepakbola-humanoid-learning-path) | PyBullet, ROS | ZMP, Preview control |  | 11 | 2024-07-13 | A curated list of references for Indonesian students interested in the Humanoid Soccer Rob |
| [mominalix/Humanoid-Robot-Reinforcement-Learning-PPO](https://github.com/mominalix/Humanoid-Robot-Reinforcement-Learning-PPO) | PyBullet | RL | Python | 11 | 2024-06-24 | This repository contains a project that leverages reinforcement learning to make a humanoi |
| [CAST-Robotics/Trajectory-Optimization](https://github.com/CAST-Robotics/Trajectory-Optimization) | PyBullet, ROS | ZMP, LIPM, DCM, Trajectory optimization, Inverse kinematics | C++ | 10 | 2021-11-29 | DCM based walking trajectory optimization of SurenaV |
| [ashutoshtiwari13/Simple-Random-Search](https://github.com/ashutoshtiwari13/Simple-Random-Search) | PyBullet, MuJoCo | RL | Python | 10 | 2022-06-21 | A simple random searching technique which provides a competitive approach to Reinforcement |
| [Jeremy26/bipedal-walker](https://github.com/Jeremy26/bipedal-walker) | PyBullet | RL | Jupyter Notebook | 9 | 2018-10-18 | Train a Bipedal Robot to walk using Reinforcement Learning |
| [TTimelord/rl_course_project](https://github.com/TTimelord/rl_course_project) | PyBullet | RL | Python | 8 | 2023-06-19 | Learning to Kick for a Bipedal Robot with Deep Reinforcement Learning |

## 2. PID / LQR / MPC 언급 (PyBullet 외, 상위 25)
| 저장소 | 시뮬레이터 | 제어 방식 (README 키워드) | 언어 | ★ | 갱신 | 설명(원문) |
|---|---|---|---|---|---|---|
| [google-deepmind/mujoco_mpc](https://github.com/google-deepmind/mujoco_mpc) | MuJoCo | MPC | C++ | 1769 | 2026-11-05 | Real-time behaviour synthesis with MuJoCo, using Predictive Control |
| [LeCAR-Lab/dial-mpc](https://github.com/LeCAR-Lab/dial-mpc) | MuJoCo, Brax, ROS | MPC | Python | 1016 | 2025-05-28 | Official implementation for the paper "Full-Order Sampling-Based MPC for Torque-Level Loco |
| [RealXiaoze/humanoid-motion-intelligence](https://github.com/RealXiaoze/humanoid-motion-intelligence) | Isaac Sim/Lab | MPC, Whole-body control, TSID, DDP/iLQR, Imitation/motion tracking |  | 715 | 2026-11-19 | 人形机器人运动智能论文、开源项目、产业与求职知识库 |
| [bridgedp/hunter_bipedal_control](https://github.com/bridgedp/hunter_bipedal_control) | MuJoCo, Gazebo, ROS | MPC, Whole-body control | C++ | 595 | 2024-05-20 | An open source bipedal robot control framework, based on non-linear MPC and WBC, tailered  |
| [DRCL-USC/Hector_Simulation](https://github.com/DRCL-USC/Hector_Simulation) | Gazebo, MATLAB/Simulink, ROS | MPC | C++ | 536 | 2025-01-13 | Simulation Software (ROS/MATLAB) for HECTOR Humanoid Robot Locomotion Control/Bipedal Loco |
| [pocketxjl/humanoid-control](https://github.com/pocketxjl/humanoid-control) | MuJoCo, ROS | PD control, MPC, Whole-body control, QP | C++ | 423 | 2025-01-05 | A humanoid bipedal walking control repo using NMPC and WBC, and simulation with mujoco. Co |
| [manumerous/wb_humanoid_mpc](https://github.com/manumerous/wb_humanoid_mpc) | ROS | MPC | C++ | 390 | 2026-10-18 | Whole-Body Nonlinear MPC for Realtime Humanoid Loco-Manipulation Planning and Control |
| [iit-DLSLab/mpx](https://github.com/iit-DLSLab/mpx) | MuJoCo, ROS | MPC, Trajectory optimization, DDP/iLQR | Python | 283 | 2026-09-02 | Model Predictive Control in JAX |
| [stephane-caron/lipm_walking_controller](https://github.com/stephane-caron/lipm_walking_controller) | Choreonoid, ROS | MPC, ZMP, LIPM, DCM, QP, Inverse kinematics | C++ | 269 | 2023-08-11 | Stair-climbing controller for HRP-4 humanoid robots |
| [stephane-caron/pymanoid](https://github.com/stephane-caron/pymanoid) |  | MPC, ZMP, Inverted pendulum, Whole-body control, QP, Inverse kinematics | Python | 235 | 2024-02-19 | Humanoid robotics prototyping environment based on OpenRAVE |
| [isri-aist/BaselineWalkingController](https://github.com/isri-aist/BaselineWalkingController) | MuJoCo, Choreonoid | MPC, ZMP, LIPM, DCM | C++ | 170 | 2026-03-25 | Humanoid walking controller with various baseline methods |
| [gbionics/walking-controllers](https://github.com/gbionics/walking-controllers) | Gazebo | MPC, ZMP, DCM, QP, Inverse kinematics, Imitation/motion tracking | C++ | 163 | 2026-02-24 | Bipedal locomotion software for the humanoid robot platform iCub. |
| [junhengl/mpc-rl](https://github.com/junhengl/mpc-rl) | MuJoCo | MPC, QP, RL | Python | 118 | 2026-06-10 | MPC-guided RL for Humanoid Locomotion and Manipulation |
| [UMich-BipedLab/cassie_alip_mpc](https://github.com/UMich-BipedLab/cassie_alip_mpc) | MATLAB/Simulink | MPC, LIPM, Inverse kinematics | C | 98 | 2023-03-27 | This repository provides an implementation of a bipedal locomotion controller, described i |
| [LiuDingchuan/Graduate_Project](https://github.com/LiuDingchuan/Graduate_Project) | Webots, MATLAB/Simulink | LQR | C++ | 93 | 2024-07-25 | Webots Simulation of Wheeled Bipedal Robot Using Model Based LQR (from an undergraduate gr |
| [tryingfly/nabo](https://github.com/tryingfly/nabo) | MuJoCo, Gazebo, Webots, CoppeliaSim/V-REP | MPC | C | 90 | 2024-04-18 | Open project for biped robot with c++. Cross OS, cross simulation platform or even real ro |
| [ekorudiawan/ZMP-Preview-Control-WPG](https://github.com/ekorudiawan/ZMP-Preview-Control-WPG) | MATLAB/Simulink | LQR, ZMP, LIPM, Preview control | Python | 51 | 2026-06-26 | ZMP Preview Control Walking Pattern Generation for Biped Humanoid Robot |
| [botianhao/humanoid_control](https://github.com/botianhao/humanoid_control) | MuJoCo, ROS | PD control, MPC, Whole-body control, QP | C++ | 42 | 2025-03-02 | A humanoid bipedal walking control repo using NMPC and WBC on ROS2, and simulation with mu |
| [MarcDcls/mjlab_upkie](https://github.com/MarcDcls/mjlab_upkie) | MuJoCo | MPC, RL | Python | 41 | 2026-05-26 | This repository contains Reinforcement Learning (RL) environments for the Upkie robot. |
| [1moule/bipedal_wheel](https://github.com/1moule/bipedal_wheel) | Gazebo, ROS | PID, LQR, Trajectory optimization | C++ | 39 | 2026-05-23 |  |
| [syw-robotics/Nabo_Pointfoot_Bipedal_Robot](https://github.com/syw-robotics/Nabo_Pointfoot_Bipedal_Robot) | MuJoCo | MPC, QP | C | 34 | 2025-04-07 | Open-Sourecd project for pointfoot bipedal robot walking control in MuJoCo simulation. Bui |
| [ansh1113/humanoid-motion-planning](https://github.com/ansh1113/humanoid-motion-planning) | MuJoCo, Isaac Sim/Lab | MPC, ZMP, LIPM, Preview control, Trajectory optimization | Python | 30 | 2026-07-30 | Whole-body motion planning for Unitree G1 humanoid in MuJoCo - ZMP preview control, A* foo |
| [clearlab-sustech/Bipedal_MPC](https://github.com/clearlab-sustech/Bipedal_MPC) | MuJoCo, ROS | MPC | C++ | 30 | 2024-12-30 |  |
| [CurryDreamer/Wheel_Bipedal_Robot](https://github.com/CurryDreamer/Wheel_Bipedal_Robot) | MuJoCo, MATLAB/Simulink | PID, LQR | Python | 26 | 2026-09-02 |  |
| [pal-robotics/talos_robot](https://github.com/pal-robotics/talos_robot) | ROS | MPC | Python | 26 | 2026-02-20 |  |

## 3. ZMP / LIPM / Preview control 언급 (위 두 표 제외, 상위 15)
| 저장소 | 시뮬레이터 | 제어 방식 (README 키워드) | 언어 | ★ | 갱신 | 설명(원문) |
|---|---|---|---|---|---|---|
| [leggedrobotics/xpp](https://github.com/leggedrobotics/xpp) | ROS | ZMP | C++ | 334 | 2021-12-09 |  Visualization of Motions for Legged Robots in ros-rviz |
| [gbionics/bipedal-locomotion-framework](https://github.com/gbionics/bipedal-locomotion-framework) | ROS | LIPM, TSID, Inverse kinematics | C++ | 240 | 2026-11-04 | Suite of libraries for achieving bipedal locomotion on humanoid robots |
| [chauby/BipedalWalkingRobots](https://github.com/chauby/BipedalWalkingRobots) | CoppeliaSim/V-REP | ZMP, LIPM, Preview control, Inverse kinematics | Python | 212 | 2025-09-07 | Linear Inverted Pendulum Model based bipedal walking |
| [mrsp/serow](https://github.com/mrsp/serow) | Gazebo, ROS | ZMP | C++ | 96 | 2026-11-10 | SEROW Framework for N Legged Robot Walking Estimation |
| [Argo-Robot/footsteps_planning](https://github.com/Argo-Robot/footsteps_planning) |  | ZMP, LIPM | MATLAB | 49 | 2025-01-26 | Learn how to design a footstep planner for humanoid robots, breaking down the entire proce |
| [zanppa/WPG](https://github.com/zanppa/WPG) |  | ZMP, Inverted pendulum, Preview control | Python | 34 | 2020-10-01 | Walking pattern generation examples using zero moment point method |
| [ekorudiawan/Omnidirectional-Walking-ZMP-Preview-Control](https://github.com/ekorudiawan/Omnidirectional-Walking-ZMP-Preview-Control) |  | ZMP, Preview control, Inverse kinematics | Python | 14 | 2019-12-31 | Omnidirectional Walking Pattern Generation for Humanoid Robot using ZMP Preview Control |
| [stephane-caron/vhip_walking_controller](https://github.com/stephane-caron/vhip_walking_controller) |  | LIPM, Inverted pendulum | C++ | 11 | 2022-11-23 | Walking controller based on variable-height inverted pendulum tracking |
| [Raghav-Soni/Inverted-Pendulum-Model-Trajectory-For-Biped](https://github.com/Raghav-Soni/Inverted-Pendulum-Model-Trajectory-For-Biped) |  | LIPM | Python | 11 | 2025-01-28 | A Linear Inverted Pendulum (LIP) model based framework for generating walking trajectories |
| [briankim13/CapturePointWalkingRobot](https://github.com/briankim13/CapturePointWalkingRobot) | MATLAB/Simulink | ZMP, LIPM, Inverted pendulum, Capture point | MATLAB | 11 | 2021-09-16 |  |
| [sunilgora/SIP2HumnWalking](https://github.com/sunilgora/SIP2HumnWalking) | MuJoCo | PD control, LIPM, Inverted pendulum | Python | 10 | 2026-04-14 | Spherical Inverted Pendulum Based Walking Simulation of Kondo KHR3HV Humanoid Robot in MuJ |
| [neka-nat/humanoid_robot](https://github.com/neka-nat/humanoid_robot) |  | ZMP, LIPM | Python | 10 | 2018-01-08 | Read "humanoid robot" and implement some algorithms |
| [rohanpsingh/grasp-fsm-sample-controller](https://github.com/rohanpsingh/grasp-fsm-sample-controller) | MuJoCo | LIPM | C++ | 10 | 2026-07-12 | mc-rtc FSM controller to demonstrate biped walking and object grasping |
| [AhmedFahmySoliman/RobustExoControl](https://github.com/AhmedFahmySoliman/RobustExoControl) | MATLAB/Simulink | ZMP | MATLAB | 9 | 2024-11-13 | In this research, we aim for robust locomotion control of an underactuated bipedal exoskel |
| [ADVRHumanoids/limit_cycle_walking](https://github.com/ADVRHumanoids/limit_cycle_walking) | Gazebo | Preview control | C++ | 7 | 2021-04-12 | Hybrid Walking Pattern Generator for bipedal robots, merging the Virtual Constraints and t |
