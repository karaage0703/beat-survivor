"""音楽生成関連のクラスを定義するモジュール."""

from typing import List, Set
import pyxel


class Music:
    """音楽生成クラス."""

    def __init__(self):
        """音楽システムの初期化."""
        self.base_bpm = 120  # 基本テンポ
        self.current_bpm = self.base_bpm
        self.base_volume = 7  # 基本音量（0-7）

        # メロディとリズムのパターン定義
        self.melody_patterns = {
            "normal": [0, 4, 7, 4],  # 基本メロディ
            "knife": [0, 4, 7, 11],  # ナイフ用メロディ
            "holy_water": [0, 3, 7, 10],  # 聖水用メロディ
            "magic_blade": [0, 4, 8, 11],  # 魔法の剣用メロディ
            "sacred_flame": [0, 3, 6, 9],  # 聖なる炎用メロディ
        }

        self.rhythm_patterns = {
            "normal": [0, 2],  # 基本リズム
            "intense": [0, 1, 2, 3],  # 敵が多い時のリズム
            "boss": [0, 1, 1, 2, 2, 3],  # ボス戦用リズム
        }

        # 楽器の音色定義
        self.instruments = {
            "zombie": 0,  # 基本音色
            "bat": 1,  # 高音系
            "ghost": 2,  # 環境音系
            "skeleton": 3,  # 打楽器系
        }

        # 現在のパターン
        self.current_melody = "normal"
        self.current_rhythm = "normal"
        self.active_instruments: Set[int] = set()

        # 音楽更新用タイマー
        self.melody_timer = 0
        self.rhythm_timer = 0
        self.note_index = 0

        # 音声データの初期化
        self._init_sound()

    def _init_sound(self) -> None:
        """音声データを初期化."""
        # メロディ用の音声データ（より豊かなメロディパターン）
        pyxel.sounds[0].set("c2e2g2c3e3g3", "t", "7", "n", 20)  # 基本メロディ（上昇）
        pyxel.sounds[1].set("a2c3e3a3c4e4", "t", "7", "n", 20)  # ナイフ用メロディ（高音）
        pyxel.sounds[2].set("g2a2c3e3g3a3", "t", "7", "n", 20)  # 聖水用メロディ（神秘的）
        pyxel.sounds[3].set("e2g2b2e3g3b3", "t", "7", "n", 20)  # 魔法の剣用メロディ（力強い）
        pyxel.sounds[4].set("d2f2a2d3f3a3", "t", "7", "n", 20)  # 聖なる炎用メロディ（荘厳）

        # リズム用の音声データ（より多様なリズムパターン）
        pyxel.sounds[5].set("c2c2", "n", "7", "n", 10)  # 基本リズム（低音）
        pyxel.sounds[6].set("c3c3c3", "n", "7", "f", 10)  # 強調リズム（中音）
        pyxel.sounds[7].set("c3c3c3c3", "n", "7", "f", 10)  # ボスリズム（高音）

        # アンビエント用の音声データ
        pyxel.sounds[8].set("c2e2g2c3", "s", "3", "f", 40)  # 環境音（低音）
        pyxel.sounds[9].set("g2b2d3g3", "s", "3", "f", 40)  # 環境音（中音）
        pyxel.sounds[10].set("c3e3g3c4", "s", "3", "f", 40)  # 環境音（高音）

    def update_music(self, player_speed: float, enemy_count: int, enemy_types: List[str], elapsed_minutes: int) -> None:
        """音楽の状態を更新.

        Args:
            player_speed (float): プレイヤーの移動速度
            enemy_count (int): 画面上の敵の数
            enemy_types (List[str]): 画面上の敵の種類リスト
            elapsed_minutes (int): 経過時間（分）
        """
        # テンポの更新（プレイヤーの速度に応じて、より大きな変化）
        speed_factor = player_speed / 2.0  # 基準速度で割る
        self.current_bpm = int(self.base_bpm * (1.0 + speed_factor * 0.5))  # 最大50%増加

        # リズムパターンの更新（敵の数に応じて、より細かい段階）
        if enemy_count > 30:
            self.current_rhythm = "boss"  # 大量の敵
        elif enemy_count > 15:
            self.current_rhythm = "intense"  # 中程度の敵
        else:
            self.current_rhythm = "normal"  # 少数の敵

        # メロディの選択（敵の種類に応じて）
        if "ghost" in enemy_types:
            self.current_melody = "holy_water"  # 幽霊には聖水のメロディ
        elif "skeleton" in enemy_types:
            self.current_melody = "sacred_flame"  # スケルトンには聖なる炎のメロディ
        elif "bat" in enemy_types:
            self.current_melody = "magic_blade"  # コウモリには魔法の剣のメロディ
        elif "zombie" in enemy_types:
            self.current_melody = "knife"  # ゾンビにはナイフのメロディ
        else:
            self.current_melody = "normal"  # 通常のメロディ

        # 楽器の更新（敵の種類に応じて）
        self.active_instruments = set()
        for enemy_type in enemy_types:
            if enemy_type in self.instruments:
                self.active_instruments.add(self.instruments[enemy_type])

        # 時間経過による変化（アンビエント音の追加）
        if elapsed_minutes > 0 and self.melody_timer % (60 * 2) == 0:  # 2秒ごと
            ambient_sound = (elapsed_minutes % 3) + 8  # 8, 9, 10の音声を循環
            pyxel.play(2, ambient_sound)  # チャンネル2でアンビエント音を再生

        # 音楽の再生
        self.play_music()

    def play_music(self) -> None:
        """音楽を再生."""
        # フレーム数から音符のタイミングを計算
        beat_frames = 30 * 60 / self.current_bpm  # 1拍あたりのフレーム数

        # メロディの再生
        self.melody_timer += 1
        if self.melody_timer >= beat_frames:
            self.melody_timer = 0
            # メロディパターンから音符を取得して再生
            note = self.melody_patterns[self.current_melody][self.note_index]
            pyxel.play(0, note)  # チャンネル0でメロディを再生
            self.note_index = (self.note_index + 1) % len(self.melody_patterns[self.current_melody])

        # リズムの再生（より複雑なパターン）
        self.rhythm_timer += 1
        if self.rhythm_timer >= beat_frames / 2:  # リズムは2倍の速さ
            self.rhythm_timer = 0
            # アクティブな楽器ごとにリズムパターンを再生
            for instrument in self.active_instruments:
                rhythm_note = self.rhythm_patterns[self.current_rhythm][
                    self.note_index % len(self.rhythm_patterns[self.current_rhythm])
                ]
                pyxel.play(1, rhythm_note + 5)  # チャンネル1でリズムを再生（音声データは5-7を使用）
