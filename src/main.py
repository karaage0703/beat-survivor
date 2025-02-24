"""Beat Survivor - Pyxel製ローグライトアクションゲーム."""

from .game import Game


def main() -> None:
    """ゲームのメインエントリーポイント."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
