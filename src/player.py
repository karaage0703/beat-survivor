"""プレイヤー関連のクラスを定義するモジュール."""

import math
import pyxel
from typing import Dict, List, Tuple
from .weapon import Weapon, Attack


class PassiveSkill:
    """パッシブスキルクラス."""

    def __init__(self, skill_type: str):
        """パッシブスキルの初期化.

        Args:
            skill_type (str): スキルの種類
        """
        self.type = skill_type
        self.level = 1
        self.update_stats()

    def update_stats(self) -> None:
        """スキルの効果を更新."""
        if self.type == "speed_up":
            self.bonus = 0.2 * self.level  # レベルごとに移動速度+0.2
        elif self.type == "attack_speed":
            self.bonus = 0.1 * self.level  # レベルごとに攻撃速度+10%
        elif self.type == "hp_regen":
            self.bonus = 0.1 * self.level  # レベルごとにHPが毎秒0.1回復

    def level_up(self) -> None:
        """スキルをレベルアップ."""
        self.level += 1
        self.update_stats()


class Player:
    """プレイヤークラス."""

    def __init__(self, x: int, y: int):
        """プレイヤーの初期化.

        Args:
            x (int): X座標
            y (int): Y座標
        """
        self.x = x
        self.y = y
        self.hp = 100
        self.max_hp = 100
        self.base_speed = 2
        self.exp = 0
        self.level = 1
        self.exp_to_next_level = 10
        # 武器の初期化
        self.weapons = [Weapon("knife")]
        self.attacks: List[Attack] = []
        # 向きの初期化（右向き）
        self.direction = (1.0, 0.0)
        self.last_move_x = 0
        self.last_move_y = 0
        # パッシブスキルの初期化
        self.passive_skills: Dict[str, PassiveSkill] = {}

    @property
    def speed(self) -> float:
        """現在の移動速度を取得."""
        speed = self.base_speed
        if "speed_up" in self.passive_skills:
            speed += self.passive_skills["speed_up"].bonus
        return min(speed, 4.0)  # 最大速度は4.0

    def add_passive_skill(self, skill_type: str) -> None:
        """パッシブスキルを追加.

        Args:
            skill_type (str): 追加するスキルの種類
        """
        if skill_type not in self.passive_skills:
            self.passive_skills[skill_type] = PassiveSkill(skill_type)
        else:
            self.passive_skills[skill_type].level_up()

    def gain_exp(self, amount: int) -> bool:
        """経験値を獲得.

        Args:
            amount (int): 獲得する経験値量

        Returns:
            bool: レベルアップした場合はTrue
        """
        self.exp += amount
        if self.exp >= self.exp_to_next_level:
            self.level_up()
            return True
        return False

    def level_up(self) -> None:
        """レベルアップ処理."""
        self.level += 1
        self.exp -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        # ステータス強化
        self.hp = min(200, self.hp + 10)
        self.base_speed = min(4, self.base_speed + 0.2)

    def add_weapon(self, weapon_type: str) -> None:
        """武器を追加.

        Args:
            weapon_type (str): 追加する武器の種類
        """
        self.weapons.append(Weapon(weapon_type))

    def update_direction(self) -> None:
        """プレイヤーの向きを更新."""
        # 移動入力から向きを計算
        dx = 0
        dy = 0
        if pyxel.btn(pyxel.KEY_LEFT):
            dx -= 1
        if pyxel.btn(pyxel.KEY_RIGHT):
            dx += 1
        if pyxel.btn(pyxel.KEY_UP):
            dy -= 1
        if pyxel.btn(pyxel.KEY_DOWN):
            dy += 1

        # 移動入力があった場合のみ向きを更新
        if dx != 0 or dy != 0:
            # ベクトルを正規化
            length = math.sqrt(dx * dx + dy * dy)
            self.direction = (dx / length, dy / length)
            self.last_move_x = dx
            self.last_move_y = dy

    def update(self) -> None:
        """プレイヤーの状態を更新."""
        # 移動処理と向きの更新
        self.update_direction()
        # キー入力に応じて移動
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x = max(0, self.x - self.speed)
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x = min(pyxel.width - 8, self.x + self.speed)
        if pyxel.btn(pyxel.KEY_UP):
            self.y = max(0, self.y - self.speed)
        if pyxel.btn(pyxel.KEY_DOWN):
            self.y = min(pyxel.height - 8, self.y + self.speed)

        # HP自然回復
        if "hp_regen" in self.passive_skills:
            self.hp = min(self.max_hp, self.hp + self.passive_skills["hp_regen"].bonus)

        # 武器の更新と攻撃
        for weapon in self.weapons:
            weapon.update()
            if weapon.can_attack():
                cooldown_reduction = 1.0
                if "attack_speed" in self.passive_skills:
                    cooldown_reduction = 1.0 - self.passive_skills["attack_speed"].bonus
                self.attacks.append(Attack(self.x, self.y, weapon, self.direction))
                weapon.cooldown = int(weapon.max_cooldown * cooldown_reduction)

        # 攻撃の更新
        self.attacks = [attack for attack in self.attacks if attack.is_alive()]
        for attack in self.attacks:
            attack.update()

    def draw(self) -> None:
        """プレイヤーを描画."""
        # プレイヤーを白色(7)の8x8の四角形で描画
        pyxel.rect(self.x, self.y, 8, 8, 7)
        # 向きを示す線を描画
        end_x = self.x + 4 + self.direction[0] * 8
        end_y = self.y + 4 + self.direction[1] * 8
        pyxel.line(self.x + 4, self.y + 4, end_x, end_y, 8)
        # 攻撃の描画
        for attack in self.attacks:
            attack.draw()
