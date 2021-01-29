
class ELO:
    """
    https://en.wikipedia.org/wiki/Elo_rating_system#Mathematical_details
    """
    @staticmethod
    def expected_result(elo_a, elo_b):
        expect_a = 1.0 / (1 + 10 ** ((elo_b - elo_a) / 400))
        return expect_a

    @staticmethod
    def update_elo(winner_elo, loser_elo):
        mean_elo = (winner_elo + loser_elo) / 2
        k_factor = 16
        if mean_elo < 2100:
            k_factor = 32
        elif 2100 >= mean_elo >= 2400:
            k_factor = 24

        expected_win = ELO.expected_result(winner_elo, loser_elo)
        change_in_elo = round(k_factor * (1 - expected_win))
        winner_elo += change_in_elo
        loser_elo -= change_in_elo
        return winner_elo, loser_elo

    @staticmethod
    def probabilities_elo(player0_elo, player1_elo):
        elo_sum = player0_elo + player1_elo
        return player0_elo * 100 / elo_sum, player1_elo * 100 / elo_sum