"""ゲーム関連のクラスを定義するモジュール."""

import random
from typing import List, Optional
import pyxel

from .player import Player
from .enemy import Enemy
from .music import Music


class BaseGame:
    """ゲームの基本クラス."""

    # ゲームの難易度設定
    DIFFICULTY_SCALING = {
        "spawn_rate": {
            "initial": 30,  # 初期スポーン間隔（フレーム）
            "min": 10,  # 最小スポーン間隔
            "reduction_per_minute": 2,  # 1分ごとの間隔減少
        },
        "enemy_stats": {
            "hp_increase": 0.1,  # 1分ごとのHP増加率
            "speed_increase": 0.05,  # 1分ごとの速度増加率
            "exp_increase": 0.2,  # 1分ごとの経験値増加率
        },
    }

    # レベルアップ時の選択肢
    LEVEL_UP_OPTIONS = {
        "knife_level_up": "ナイフの強化",
        "holy_water_add": "聖水の追加",
        "holy_water_level_up": "聖水の強化",
        "hp_up": "HPの回復",
        "speed_up": "移動速度アップ",
        "attack_speed": "攻撃速度アップ",
        "hp_regen": "HP自然回復",
    }

    def __init__(self, width: int = 160, height: int = 120):
        """ゲームの初期化.

        Args:
            width (int, optional): 画面の幅. デフォルトは160
            height (int, optional): 画面の高さ. デフォルトは120
        """
        self.width = width
        self.height = height
        # プレイヤーを画面中央に配置
        self.player = Player(width // 2, height // 2)
        # 敵リストの初期化
        self.enemies: List[Enemy] = []
        # 敵の出現タイマー
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = self.DIFFICULTY_SCALING["spawn_rate"]["initial"]
        # スコアの初期化
        self.score = 0
        self.high_score = 0
        # レベルアップ選択肢
        self.level_up_options: Optional[List[str]] = None
        self.selected_option = 0
        # 経過時間の管理
        self.elapsed_frames = 0
        self.elapsed_minutes = 0
        # 音楽システムの初期化
        self.music = Music()

    def check_collision(self, x1: float, y1: float, w1: int, h1: int, x2: float, y2: float, w2: int, h2: int) -> bool:
        """矩形の衝突判定.

        Args:
            x1 (float): 矩形1のX座標
            y1 (float): 矩形1のY座標
            w1 (int): 矩形1の幅
            h1 (int): 矩形1の高さ
            x2 (float): 矩形2のX座標
            y2 (float): 矩形2のY座標
            w2 (int): 矩形2の幅
            h2 (int): 矩形2の高さ

        Returns:
            bool: 衝突している場合はTrue
        """
        return x1 <= x2 + w2 and x1 + w1 >= x2 and y1 <= y2 + h2 and y1 + h1 >= y2

    def get_level_up_options(self) -> List[str]:
        """レベルアップ時の選択肢を取得.

        Returns:
            List[str]: 選択肢のリスト
        """
        options = []
        # ナイフの強化は常に選択肢に入れる
        options.append("knife_level_up")
        # 聖水を持っていない場合は追加を選択肢に入れる
        if not any(w.type == "holy_water" for w in self.player.weapons):
            options.append("holy_water_add")
        # 聖水を持っている場合は強化を選択肢に入れる
        elif any(w.type == "holy_water" for w in self.player.weapons):
            options.append("holy_water_level_up")
        # HPが最大値未満なら回復を選択肢に入れる
        if self.player.hp < 200:
            options.append("hp_up")
        # 移動速度が最大値未満なら速度アップを選択肢に入れる
        if self.player.speed < 4:
            options.append("speed_up")
        # 攻撃速度アップを選択肢に入れる
        if "attack_speed" not in self.player.passive_skills or self.player.passive_skills["attack_speed"].level < 5:
            options.append("attack_speed")
        # HP自然回復を選択肢に入れる
        if "hp_regen" not in self.player.passive_skills or self.player.passive_skills["hp_regen"].level < 5:
            options.append("hp_regen")
        return options[:3]  # 最大3つまで

    def apply_level_up_option(self, option: str) -> None:
        """レベルアップ時の選択肢を適用.

        Args:
            option (str): 選択された選択肢
        """
        if option == "knife_level_up":
            # ナイフを強化
            for weapon in self.player.weapons:
                if weapon.type == "knife":
                    weapon.level_up()
                    break
        elif option == "holy_water_add":
            # 聖水を追加
            self.player.add_weapon("holy_water")
        elif option == "holy_water_level_up":
            # 聖水を強化
            for weapon in self.player.weapons:
                if weapon.type == "holy_water":
                    weapon.level_up()
                    break
        elif option == "hp_up":
            # HPを回復
            self.player.hp = min(200, self.player.hp + 50)
        elif option == "speed_up":
            # 移動速度アップ
            self.player.add_passive_skill("speed_up")
        elif option == "attack_speed":
            # 攻撃速度アップ
            self.player.add_passive_skill("attack_speed")
        elif option == "hp_regen":
            # HP自然回復
            self.player.add_passive_skill("hp_regen")

    def spawn_enemy(self) -> None:
        """敵をランダムな位置に出現させる."""
        # 画面外のランダムな位置を選択
        side = random.randint(0, 3)  # 0: 上, 1: 右, 2: 下, 3: 左
        if side == 0:  # 上
            x = random.randint(0, self.width - 8)
            y = -8
        elif side == 1:  # 右
            x = self.width
            y = random.randint(0, self.height - 8)
        elif side == 2:  # 下
            x = random.randint(0, self.width - 8)
            y = self.height
        else:  # 左
            x = -8
            y = random.randint(0, self.height - 8)

        # ランダムな敵の種類を選択
        r = random.random()
        if r < 0.5:  # 50%
            enemy_type = "zombie"
        elif r < 0.7:  # 20%
            enemy_type = "bat"
        elif r < 0.85:  # 15%
            enemy_type = "skeleton"
        else:  # 15%
            enemy_type = "ghost"
        self.enemies.append(Enemy(x, y, enemy_type))

    def update(self) -> None:
        """ゲームの状態を更新."""
        # 経過時間の更新
        self.elapsed_frames += 1
        if self.elapsed_frames % (60 * 60) == 0:  # 60秒（60FPS × 60）
            self.elapsed_minutes += 1

        # 音楽の更新
        if self.player and self.enemies is not None:
            self.music.update_music(
                player_speed=self.player.speed,
                enemy_count=len(self.enemies),
                enemy_types=[enemy.type for enemy in self.enemies],
                elapsed_minutes=self.elapsed_minutes,
            )

    def draw(self) -> None:
        """ゲーム画面を描画."""
        pass


class Game(BaseGame):
    """実際のゲームクラス."""

    def __init__(self):
        """ゲームの初期化."""
        # Pyxelの初期化（画面サイズ: 160x120）
        pyxel.init(160, 120, title="Beat Survivor")
        super().__init__(pyxel.width, pyxel.height)

    def run(self) -> None:
        """ゲームを実行."""
        pyxel.run(self.update, self.draw)

    def update(self) -> None:
        """ゲームの状態を更新."""
        # ESCキーでゲーム終了
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
            return

        # レベルアップ選択中の場合
        if self.level_up_options is not None:
            if pyxel.btnp(pyxel.KEY_UP):
                self.selected_option = (self.selected_option - 1) % len(self.level_up_options)
            elif pyxel.btnp(pyxel.KEY_DOWN):
                self.selected_option = (self.selected_option + 1) % len(self.level_up_options)
            elif pyxel.btnp(pyxel.KEY_SPACE):
                # 選択肢を適用
                self.apply_level_up_option(self.level_up_options[self.selected_option])
                self.level_up_options = None
                self.selected_option = 0
            return

        # プレイヤーの更新
        self.player.update()

        # 敵の出現（30フレームごとに1体）
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= 30:
            self.spawn_enemy()
            self.enemy_spawn_timer = 0

        # 敵の更新と衝突判定
        for enemy in self.enemies:
            enemy.update(self.player.x, self.player.y)

            # プレイヤーとの衝突判定
            if self.check_collision(self.player.x, self.player.y, 8, 8, enemy.x, enemy.y, 8, 8):
                self.player.hp -= 1

        # 攻撃と敵の衝突判定
        for attack in self.player.attacks:
            for enemy in self.enemies:
                if self.check_collision(attack.x, attack.y, attack.weapon.range, attack.weapon.range, enemy.x, enemy.y, 8, 8):
                    enemy.take_damage(attack.weapon.damage)

        # 死亡した敵の処理
        for enemy in self.enemies[:]:
            if not enemy.is_alive():
                self.enemies.remove(enemy)
                self.score += enemy.exp
                # 経験値獲得とレベルアップ判定
                if self.player.gain_exp(enemy.exp):
                    # レベルアップ時の選択肢を設定
                    self.level_up_options = self.get_level_up_options()
                    self.selected_option = 0

        # 基底クラスの更新処理
        super().update()

    def draw(self) -> None:
        """ゲーム画面を描画."""
        # 画面をクリア（背景色: 0）
        pyxel.cls(0)

        # プレイヤーの描画
        self.player.draw()

        # 敵の描画
        for enemy in self.enemies:
            enemy.draw()

        # レベルアップ選択中の場合
        if self.level_up_options is not None:
            # 背景を暗く
            pyxel.rect(0, 0, pyxel.width, pyxel.height, 1)
            # 選択肢の表示
            for i, option in enumerate(self.level_up_options):
                color = 7 if i == self.selected_option else 13
                text = self.LEVEL_UP_OPTIONS[option]
                x = pyxel.width // 2 - len(text) * 2
                y = pyxel.height // 2 - len(self.level_up_options) * 4 + i * 8
                pyxel.text(x, y, text, color)

        # デバッグ情報の表示
        pyxel.text(4, 4, f"HP: {self.player.hp}", 7)
        pyxel.text(4, 12, f"Level: {self.player.level}", 7)
        pyxel.text(4, 20, f"Exp: {self.player.exp}/{self.player.exp_to_next_level}", 7)
        pyxel.text(4, 28, f"Score: {self.score}", 7)
        pyxel.text(4, 36, f"Enemies: {len(self.enemies)}", 7)
