"""敵関連のクラスを定義するモジュール."""

import math
import random
import pyxel


class Enemy:
    """敵クラス."""

    # 敵の種類ごとのステータス
    ENEMY_STATS = {
        "zombie": {
            "hp": 10,
            "speed": 0.5,
            "exp": 1,
            "color": 11,  # 緑色
            "behavior": "chase",  # プレイヤーを追いかける
        },
        "bat": {
            "hp": 8,
            "speed": 1.0,
            "exp": 2,
            "color": 2,  # 紫色
            "behavior": "circle",  # 円を描いて移動
            "circle_radius": 20,  # 円の半径
            "circle_speed": 0.1,  # 円を描く速度
        },
        "ghost": {
            "hp": 15,
            "speed": 0.3,
            "exp": 3,
            "color": 7,  # 白色
            "behavior": "teleport",  # 瞬間移動
            "teleport_cooldown": 60,  # 瞬間移動のクールダウン
        },
        "skeleton": {
            "hp": 12,
            "speed": 0.4,
            "exp": 2,
            "color": 6,  # 水色
            "behavior": "zigzag",  # ジグザグ移動
            "zigzag_width": 30,  # ジグザグの幅
            "zigzag_speed": 0.05,  # ジグザグの速度
        },
    }

    def __init__(self, x: int, y: int, enemy_type: str = "zombie"):
        """敵の初期化.

        Args:
            x (int): X座標
            y (int): Y座標
            enemy_type (str, optional): 敵の種類. デフォルトは"zombie"
        """
        self.x = x
        self.y = y
        self.type = enemy_type
        stats = self.ENEMY_STATS[enemy_type]
        self.hp = stats["hp"]
        self.speed = stats["speed"]
        self.exp = stats["exp"]
        self.behavior = stats["behavior"]
        self.color = stats["color"]
        # 行動パターン用の変数
        self.movement_timer = 0
        if self.behavior == "circle":
            self.circle_angle = random.random() * math.pi * 2
            self.circle_radius = stats["circle_radius"]
            self.circle_speed = stats["circle_speed"]
        elif self.behavior == "teleport":
            self.teleport_cooldown = stats["teleport_cooldown"]
            self.teleport_timer = 0
        elif self.behavior == "zigzag":
            self.zigzag_offset = 0
            self.zigzag_width = stats["zigzag_width"]
            self.zigzag_speed = stats["zigzag_speed"]

    def update(self, player_x: int, player_y: int) -> None:
        """敵の状態を更新.

        Args:
            player_x (int): プレイヤーのX座標
            player_y (int): プレイヤーのY座標
        """
        self.movement_timer += 1

        # プレイヤーまでの距離と方向を計算
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if self.behavior == "chase":
            # ゾンビ: プレイヤーを追いかける
            if distance > 0:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed

        elif self.behavior == "circle":
            # コウモリ: 円を描いて移動
            self.circle_angle += self.circle_speed
            # プレイヤーを中心に円を描く
            target_x = player_x + math.cos(self.circle_angle) * self.circle_radius
            target_y = player_y + math.sin(self.circle_angle) * self.circle_radius
            # 目標位置に向かってゆっくり移動
            self.x += (target_x - self.x) * self.speed
            self.y += (target_y - self.y) * self.speed

        elif self.behavior == "teleport":
            # ゴースト: 一定時間ごとに瞬間移動
            if distance > 0:
                self.x += (dx / distance) * self.speed * 0.5
                self.y += (dy / distance) * self.speed * 0.5
            self.teleport_timer += 1
            if self.teleport_timer >= self.teleport_cooldown:
                # プレイヤーの近くにランダムにテレポート
                angle = random.random() * math.pi * 2
                teleport_distance = random.randint(20, 40)
                self.x = player_x + math.cos(angle) * teleport_distance
                self.y = player_y + math.sin(angle) * teleport_distance
                self.teleport_timer = 0

        elif self.behavior == "zigzag":
            # スケルトン: ジグザグ移動
            if distance > 0:
                # 基本的な移動
                base_dx = (dx / distance) * self.speed
                base_dy = (dy / distance) * self.speed
                # ジグザグのオフセットを更新
                self.zigzag_offset += self.zigzag_speed
                # 進行方向に対して垂直な方向にオフセット
                perpendicular_x = -base_dy
                perpendicular_y = base_dx
                # ジグザグ移動を適用
                zigzag_amount = math.sin(self.zigzag_offset) * self.zigzag_width
                self.x += base_dx + perpendicular_x * zigzag_amount
                self.y += base_dy + perpendicular_y * zigzag_amount

    def take_damage(self, damage: int) -> None:
        """ダメージを受ける.

        Args:
            damage (int): 受けるダメージ量
        """
        self.hp -= damage

    def is_alive(self) -> bool:
        """生存しているかどうかを判定.

        Returns:
            bool: 生存している場合はTrue
        """
        return self.hp > 0

    def draw(self) -> None:
        """敵を描画."""
        # 敵の種類に応じた色で描画
        pyxel.rect(self.x, self.y, 8, 8, self.color)

        # 特殊効果
        if self.behavior == "teleport" and self.teleport_timer >= self.teleport_cooldown - 10:
            # テレポート直前は点滅
            if self.movement_timer % 4 < 2:
                pyxel.rect(self.x - 1, self.y - 1, 10, 10, 7)
        elif self.behavior == "circle":
            # コウモリは軌跡を表示
            angle = self.circle_angle - self.circle_speed * 3
            for i in range(3):
                trail_x = self.x - math.cos(angle) * self.speed * 4 * (i + 1)
                trail_y = self.y - math.sin(angle) * self.speed * 4 * (i + 1)
                pyxel.rect(trail_x, trail_y, 4, 4, self.color)
                angle -= self.circle_speed
        elif self.behavior == "zigzag":
            # スケルトンは移動方向を示す線を表示
            if self.movement_timer % 8 < 4:
                pyxel.line(self.x + 4, self.y + 4, self.x + 4 + math.sin(self.zigzag_offset) * 8, self.y + 4, self.color)
