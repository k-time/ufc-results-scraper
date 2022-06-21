"""Scraper to get fight results from ufcstats.com."""

from typing import Optional, List, Any, Tuple
import requests
from decimal import Decimal
from enum import Enum
from datetime import date, datetime

from bs4 import BeautifulSoup


UFC_STATS_URL: str = "http://ufcstats.com/statistics/events/completed"


class Outcome(Enum):
    """Represents the outcome of a fight."""

    WIN = "win"
    DRAW = "draw"
    NO_CONTEST = "nc"


class FightResult:
    """Info about a fight's result."""

    def __init__(
            self, fighter_1: str, fighter_2: str, winner: Optional[str], outcome: Outcome, total_rounds: Decimal
    ) -> None:
        self.fighter_1: str = fighter_1
        self.fighter_2: str = fighter_2
        self.winner: Optional[str] = winner
        self.outcome: Outcome = outcome
        self.total_rounds: Decimal = total_rounds


class UnfinishedFightException(Exception):
    """Error indicating that the fight has not occurred yet."""

    pass


def get_ufc_results() -> Tuple[Optional[date], List[FightResult]]:
    """Gets the results for the latest completed UFC event from ufcstats.com."""
    latest_event_link: Optional[str] = _get_latest_ufc_event_page()
    return _get_all_fight_results(latest_event_link) if latest_event_link is not None else (None, [])


def _get_latest_ufc_event_page() -> Optional[str]:
    response = requests.get(UFC_STATS_URL)
    if response.status_code != 200:
        raise ConnectionError(f"Could not connect to ufcstats.com; reason {response.status_code} {response.reason}")

    soup: BeautifulSoup = BeautifulSoup(response.content, "html.parser")
    event_links: List[Any] = soup.find_all("a", href=True, attrs={"class": "b-link_style_black"})

    return event_links[0]["href"] if event_links else None


def _get_all_fight_results(latest_event_link: str) -> Tuple[date, List[FightResult]]:
    response = requests.get(latest_event_link)
    if response.status_code != 200:
        raise ConnectionError(
            f"Could not fetch latest ufc event page {latest_event_link};"
            f"reason {response.status_code} {response.reason}"
        )
    soup: BeautifulSoup = BeautifulSoup(response.content, "html.parser")
    fight_rows: List[Any] = soup.find_all("tr", attrs={"class": "b-fight-details__table-row"})

    fight_results: List[FightResult] = []

    # First row is the table headers, so skip it
    for row in fight_rows[1:]:
        try:
            fight_results.append(_get_fight_result(row))
        except UnfinishedFightException:
            # (Probably) ok to swallow this error. This "error" will occur a lot when a card is in progress.
            continue

    return _get_event_date(soup), fight_results


def _get_event_date(soup: Any) -> date:
    date_string: str = soup.find("li", attrs={"class": "b-list__box-list-item"}).contents[-1].strip()
    return datetime.strptime(date_string, "%B %d, %Y").date()


def _get_fight_result(row: Any) -> FightResult:
    result_element = row.find("i", attrs={"class": "b-flag__text"})
    if result_element is None:
        # This occurs when a card is currently in progress, so some fights are not completed yet
        raise UnfinishedFightException("Could not find fight result flag")
    outcome: Outcome = Outcome(result_element.text)

    fighter_elements: List[Any] = row.find_all("a", href=True, attrs={"class": "b-link_style_black"})
    if len(fighter_elements) != 2:
        raise ValueError("Did not find 2 fighters")
    fighter_1: str = fighter_elements[0].text.strip()
    fighter_2: str = fighter_elements[1].text.strip()
    # The first fighter is always the winner, if there was a winner
    winner: Optional[str] = fighter_1 if outcome == Outcome.WIN else None

    text_cells: List[Any] = row.find_all("p", attrs={"class": "b-fight-details__table-text"})
    if len(text_cells) < 2:
        raise ValueError("Not enough text cells found")
    round_num: int = int(text_cells[-2].text.strip())
    round_time: str = text_cells[-1].text.strip()
    total_rounds: Decimal = _get_total_rounds(round_num, round_time)

    return FightResult(fighter_1, fighter_2, winner, outcome, total_rounds)


def _get_total_rounds(round_num: int, round_time: str) -> Decimal:
    # Need to subtract 1 from round_num because MMA totals are based on rounds elapsed
    total_rounds: Decimal = Decimal(round_num) - 1
    round_time_split: List[str] = round_time.split(":")
    round_minute: int = int(round_time_split[0])
    round_second: int = int(round_time_split[1])

    # Edge case: a fight ending at exactly 2:30 of a round means it counts as a half round.
    # If the round goes past the 2:30 mark, you round up to the next round.
    if round_minute == 2:
        if round_second == 30:
            total_rounds += Decimal(0.5)
        elif round_second > 30:
            total_rounds += 1
    elif round_minute > 2:
        total_rounds += 1

    return total_rounds
