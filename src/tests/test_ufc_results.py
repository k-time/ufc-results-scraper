import unittest

import ufc_results


class TestUFCResults(unittest.TestCase):
    def test_get_latest_ufc_results(self) -> None:
        date, fight_results = ufc_results.get_ufc_results()
        assert date, "Could not find latest UFC event page"
        assert fight_results, "Could not find latest UFC event page"

        for result in fight_results:
            assert result.fighter_1, "Could not find fighter 1 in result"
            assert result.fighter_2, "Could not find fighter 2 in result"
            assert result.winner in (
                result.fighter_1,
                result.fighter_2,
            ), f"Fight winner {result.winner} was not fighter 1 or fighter 2"
            assert result.outcome.value in ("win", "draw", "nc"), f"Invalid fight outcome {result.outcome.value}"
            assert 0 <= result.total_rounds <= 5, f"Invalid number of rounds {result.total_rounds}"
