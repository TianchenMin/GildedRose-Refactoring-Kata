# -*- coding: utf-8 -*-
from __future__ import annotations
from abc import ABC, abstractmethod

# ---------------- Public API (保持不变) ----------------
class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)


class GildedRose(object):
    def __init__(self, items):
        # 不能改属性名
        self.items = items

    def update_quality(self):
        for it in self.items:
            _pick_strategy(it).update(it)
        return self.items


# ---------------- 常量（与仓库保持一致） ----------------
AGED_BRIE = "Aged Brie"
SULFURAS = "Sulfuras, Hand of Ragnaros"
BACKSTAGE = "Backstage passes to a TAFKAL80ETC concert"
CONJURED = "Conjured Mana Cake"  # 路线A：不做特殊处理，走普通策略

# ---------------- 工具函数：非 Sulfuras 的边界处理 ----------------
def _inc_quality(item: Item, step: int = 1) -> None:
    for _ in range(step):
        if item.quality < 50:
            item.quality += 1

def _dec_quality(item: Item, step: int = 1) -> None:
    for _ in range(step):
        if item.quality > 0:
            item.quality -= 1

# ---------------- 策略接口与实现 ----------------
class UpdateStrategy(ABC):
    @abstractmethod
    def update(self, item: Item) -> None: ...

class SulfurasStrategy(UpdateStrategy):
    # 传奇物品：sell_in 与 quality 都不变
    def update(self, item: Item) -> None:
        return

class NormalStrategy(UpdateStrategy):
    # 到期前：-1；到期后再额外 -1（共 -2），质量不低于 0
    def update(self, item: Item) -> None:
        _dec_quality(item, 1)
        item.sell_in -= 1
        if item.sell_in < 0:
            _dec_quality(item, 1)

class AgedBrieStrategy(UpdateStrategy):
    # 到期前：+1；到期后再额外 +1（共 +2），质量不高于 50
    def update(self, item: Item) -> None:
        _inc_quality(item, 1)
        item.sell_in -= 1
        if item.sell_in < 0:
            _inc_quality(item, 1)

class BackstageStrategy(UpdateStrategy):
    """
    阶梯增益在“减天数之前”判断：
      <11 天：额外 +1；<6 天：再额外 +1（最多 +3，受上限 50 约束）
    减天数后若过期（sell_in<0），质量归 0。
    """
    def update(self, item: Item) -> None:
        _inc_quality(item, 1)
        if item.sell_in < 11:
            _inc_quality(item, 1)
        if item.sell_in < 6:
            _inc_quality(item, 1)
        item.sell_in -= 1
        if item.sell_in < 0:
            item.quality = 0

# ---------------- 简易工厂/注册表 ----------------
_STRATEGIES = {
    "__normal__": NormalStrategy(),
    AGED_BRIE: AgedBrieStrategy(),
    BACKSTAGE: BackstageStrategy(),
    SULFURAS: SulfurasStrategy(),
    # 注意：路线A 不注册 CONJURED，默认走普通策略
}

def _pick_strategy(item: Item) -> UpdateStrategy:
    if item.name == SULFURAS:
        return _STRATEGIES[SULFURAS]
    if item.name == AGED_BRIE:
        return _STRATEGIES[AGED_BRIE]
    if item.name == BACKSTAGE:
        return _STRATEGIES[BACKSTAGE]
    # Conjured 以及其他未知名称 → 普通策略
    return _STRATEGIES["__normal__"]
