def calculate_elo(elo_white: int, elo_black: int, result: str):
    """
    Standard ELO calculation.
    result: "white_wins", "black_wins", or "draw"
    """
    expected_w = 1 / (1 + 10 ** ((elo_black - elo_white) / 400))
    expected_b = 1 - expected_w

    if result == "white_wins":
        score_w, score_b = 1.0, 0.0
    elif result == "black_wins":
        score_w, score_b = 0.0, 1.0
    else:
        score_w, score_b = 0.5, 0.5

    new_white = int(elo_white + 32 * (score_w - expected_w))
    new_black = int(elo_black + 32 * (score_b - expected_b))
    return new_white, new_black
