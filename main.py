"""
* main.py:            程序入口

### 源代码文件

1. AI.py:              电脑算法
2. configure.py:       配置设定
3. constants.py:       所有常量
4. GUI.py:             图形界面
5. LAN.py:             局域网功能
6. rule.py:            游戏规则控制
7. tkintertools.py:    图形界面辅助模块
8. tools.py:           工具函数

### 资源文件

1. config.json:    配置信息
2. help.md:        帮助文本
3. statistic.json: 统计数据
4. audio/*.wav:    音效文件
5. data            棋局库
"""

# 版本号
__version__ = '1.7'
# 作者
__author__ = '小康2022'
# 更新日期
__update__ = '2024/04/22'

if __name__ == '__main__':
    from winsound import Beep

    from configure import statistic
    from GUI import Window

    # 更新统计数据
    statistic(Launch=1)
    # 启动一下winsound模块
    Beep(37, 0)
    # 启动主窗口
    Window()
