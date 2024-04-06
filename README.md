## 中国象棋

version: 1.6

### 开发环境

UI 底层是 [tkintertools](https://github.com/Xiaokang2022/tkintertools)，但此处使用的测试版本的 tkintertools，已在项目中，无需通过 pip 再次安装（即使安装，版本也不对）

Python 版本：3.12（低一点的版本，如 3.10 应该也可以运行）

### 基本功能

1. 双人对弈
2. 人机对战
3. 残局挑战
4. 局域网联机

对战均可以让子，残局挑战的棋局来自互联网，被我转换成 FEN 格式后保存在 data 文件夹中。

音频文件也来自互联网，侵权请联系我后删除。

### 关于 AI

AI 有 3 个，可在源代码中进行替换：

* 极小极大搜索算法（Python 实现）
* alpha-beta 剪枝（Python 实现）
* alpha-beta 剪枝（C++ 实现）

C++ 实现的，已编译成名为 PyDLL 的 DLL 文件，通过 Python 的 ctypes 模块调用
