# ufc-results-scraper
Retrieves UFC fight results from [ufcstats.com](http://ufcstats.com/statistics/events/completed) using the BeautifulSoup parser. Written in Python 3.9.

I use this for my website [playgambo.com](https://www.playgambo.com/) to auto-grade bets on UFC events.

## API
* `ufc_results.py` currently provides one public function `get_ufc_results()`, which returns the date and results for the latest completed UFC event from ufcstats.com.

```
>>> from pprint import pprint
>>> from ufc_results import get_ufc_results
>>> pprint(get_ufc_results())
(datetime.date(2022, 6, 18),
 [<ufc_results.FightResult object at 0x108e45fd0>,
  <ufc_results.FightResult object at 0x108f43a30>,
  <ufc_results.FightResult object at 0x108e72fd0>,
  <ufc_results.FightResult object at 0x108e0e540>,
  <ufc_results.FightResult object at 0x108e0e560>,
  <ufc_results.FightResult object at 0x108e0e500>,
  <ufc_results.FightResult object at 0x108e0e570>,
  <ufc_results.FightResult object at 0x108e0e5b0>,
  <ufc_results.FightResult object at 0x108e0e150>,
  <ufc_results.FightResult object at 0x108e0e7f0>,
  <ufc_results.FightResult object at 0x108e0e910>,
  <ufc_results.FightResult object at 0x108e0e270>,
  <ufc_results.FightResult object at 0x108e0e4f0>])
