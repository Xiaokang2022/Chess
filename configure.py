"""
配置设定
"""

from json import dump, load

with open('config.json', 'r', encoding='utf-8') as config:
    config: dict = load(config)


def configure(**kw) -> None:
    """ 修改配置文件 """
    config.update(**kw)
    with open('config.json', 'w', encoding='utf-8') as file:
        dump(config, file, indent=4)


def statistic(**kw) -> None:
    """ 修改统计数据 """
    with open('statistic.json', 'r', encoding='utf-8') as file:
        data = load(file)
    for key, value in kw.items():
        data[key] += value
    with open('statistic.json', 'w', encoding='utf-8') as file:
        dump(data, file, indent=4)
