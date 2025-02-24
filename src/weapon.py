"""武器関連のクラスを定義するモジュール."""

import pyxel
from typing import Tuple


class Weapon:
    """武器クラス."""

    # 武器の進化条件と結果
    EVOLUTION_MAP = {
        "knife": {
            "level": 5,  # レベル5で進化可能
            "evolve_to": "magic_blade",  # 魔法の剣に進化
            "description": "ナイフが魔法の剣に進化！攻撃範囲が大幅に増加",
        },
        "holy_water": {
            "level": 5,  # レベル5で進化可能
            "evolve_to": "sacred_flame",  # 聖なる炎に進化
            "description": "聖水が聖なる炎に進化！継続的にダメージを与える",
        },
    }

    def __init__(self, weapon_type: str = "knife"):
        """武器の初期化.

        Args:
            weapon_type (str, optional): 武器の種類. デフォルトは"knife"
        """
        self.type = weapon_type
        self.level = 1
        self.cooldown = 0
        self.max_cooldown = 30  # 30フレームごとに攻撃
        self.can_evolve = weapon_type in self.EVOLUTION_MAP
        self.update_stats()

    def update_stats(self) -> None:
        """武器のステータスを更新."""
        # 武器の種類とレベルに応じてステータスを設定
        if self.type == "knife":
            self.damage = 5 + (self.level - 1) * 2
            self.range = 12 + (self.level - 1) * 2
            self.max_cooldown = max(10, 30 - (self.level - 1) * 2)
        elif self.type == "magic_blade":
            self.damage = 15 + (self.level - 1) * 3
            self.range = 24 + (self.level - 1) * 3
            self.max_cooldown = max(8, 30 - (self.level - 1) * 2)
        elif self.type == "holy_water":
            self.damage = 10 + (self.level - 1) * 3
            self.range = 16 + (self.level - 1) * 2
            self.max_cooldown = max(15, 30 - (self.level - 1) * 1)
        else:  # sacred_flame
            self.damage = 20 + (self.level - 1) * 4
            self.range = 24 + (self.level - 1) * 2
            self.max_cooldown = max(12, 30 - (self.level - 1) * 1)
            self.dot_damage = 5  # 継続ダメージ

    def level_up(self) -> None:
        """武器をレベルアップ."""
        self.level += 1
        self.update_stats()

    def update(self) -> None:
        """武器の状態を更新."""
        if self.cooldown > 0:
            self.cooldown -= 1

    def can_attack(self) -> bool:
        """攻撃可能かどうかを判定.

        Returns:
            bool: 攻撃可能な場合はTrue
        """
        return self.cooldown <= 0


class Attack:
    """攻撃クラス."""

    def __init__(self, x: float, y: float, weapon: Weapon, direction: Tuple[float, float]):
        """攻撃の初期化.

        Args:
            x (float): 攻撃の開始X座標
            y (float): 攻撃の開始Y座標
            weapon (Weapon): 使用する武器
            direction (Tuple[float, float]): 攻撃の方向（正規化されたベクトル）
        """
        self.x = x
        self.y = y
        self.weapon = weapon
        # 武器の種類に応じて攻撃の挙動を設定
        if weapon.type == "knife":
            self.lifetime = 30
            self.dx = direction[0] * 2
            self.dy = direction[1] * 2
        elif weapon.type == "magic_blade":
            self.lifetime = 45  # 持続時間が長い
            self.dx = direction[0] * 3  # 移動速度が速い
            self.dy = direction[1] * 3
        elif weapon.type == "holy_water":
            self.lifetime = 30
            self.dx = 0
            self.dy = 0
        else:  # sacred_flame
            self.lifetime = 90  # 長時間持続
            self.dx = 0
            self.dy = 0
            self.dot_timer = 0  # 継続ダメージのタイマー

    def update(self) -> bool:
        """攻撃の状態を更新.

        Returns:
            bool: 継続ダメージのタイミングの場合はTrue
        """
        self.lifetime -= 1
        if self.weapon.type in ["knife", "magic_blade"]:
            self.x += self.dx
            self.y += self.dy
        elif self.weapon.type == "sacred_flame":
            # 継続ダメージの処理
            self.dot_timer += 1
            if self.dot_timer >= 15:  # 15フレームごとにダメージ
                self.dot_timer = 0
                return True  # 継続ダメージのタイミング
        return False

    def is_alive(self) -> bool:
        """攻撃が有効かどうかを判定.

        Returns:
            bool: 攻撃が有効な場合はTrue
        """
        return self.lifetime > 0

    def draw(self) -> None:
        """攻撃を描画."""
        if self.weapon.type == "knife":
            # ナイフを青色(12)の小さな四角形で描画
            pyxel.rect(self.x, self.y, 4, 4, 12)
        elif self.weapon.type == "magic_blade":
            # 魔法の剣を水色(6)の大きな四角形で描画
            pyxel.rect(self.x, self.y, 6, 6, 6)
            # 軌跡エフェクト
            for i in range(3):
                offset = (i + 1) * 2
                pyxel.rect(self.x - self.dx * offset, self.y - self.dy * offset, 4, 4, 6)
        elif self.weapon.type == "holy_water":
            # 聖水を水色(6)の大きな円で描画
            radius = self.weapon.range // 2
            pyxel.circb(self.x, self.y, radius, 6)
        else:  # sacred_flame
            # 聖なる炎を赤色(8)の円で描画
            radius = self.weapon.range // 2
            pyxel.circb(self.x, self.y, radius, 8)
            # 炎エフェクト
            inner_radius = radius * 2 // 3
            pyxel.circb(self.x, self.y, inner_radius, 8)
            if self.lifetime % 4 < 2:  # 点滅効果
                pyxel.circb(self.x, self.y, radius - 2, 8)
