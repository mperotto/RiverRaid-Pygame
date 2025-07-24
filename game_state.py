class GameState:
    """Shared game settings and player stats."""
    # screen dimensions
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    PANEL_HEIGHT = 80
    # Gameplay
    speed = 0.3
    WATER_COLOR = (45, 50, 184)
    player_score = 0

    @classmethod
    def game_height(cls):
        return cls.SCREEN_HEIGHT - cls.PANEL_HEIGHT

    @classmethod
    def add_score(cls, value):
        cls.player_score += value

    @classmethod
    def reset(cls):
        cls.speed = 0.3
        cls.player_score = 0
