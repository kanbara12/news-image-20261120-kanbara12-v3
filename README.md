# The World in One Day — Friday 20 November 2026

[![make.fun](https://img.shields.io/badge/make.fun-news--image--20261120-blue)](https://make.fun/bounty/news-image-20261120)
[![stories](https://img.shields.io/badge/stories-40-green)](https://make.fun/bounty/news-image-20261120)
[![regions](https://img.shields.io/badge/regions-7-orange)](https://make.fun/bounty/news-image-20261120)

A single 1024×1024 newspaper front page summing up Friday 20 November 2026:
**40 stories, 7 regions, 13 illustrated**, with a KPI strip, a UTC daypart
timeline, a world map with 13 numbered pins, and a date-check box.

## The day in brief

- **COP31 Antalya** — the draft text drops every fossil-fuel mention
  (144 paragraphs cut to 80); the $120bn adaptation figure is gone as
  talks run into overtime.
- **Cyclone Akvan** makes landfall — the third cyclone in a month;
  300,000+ evacuated, gusts to 90 kph, 423 rescue teams out, 69 trains
  cancelled.
- **AI selloff** — the Dow sinks below 50,000 (49,097, −2.19%) and the
  Nasdaq falls 2.25% as AI-bubble fears spread through Asia.

Ten more stories are illustrated in the middle band (Shenzhen
morning-after, Kyiv strikes, UK drones for Ukraine, the Riyadh PIF tower
attack, the Hormuz tanker fire, Gaza, Europe–Russia talks, Poland,
the Czech visit to Israel, and Tiger Woods' Northern Ireland golf course),
and 27 further briefs fill the "Also on" columns.

## Date check

Every story on this page was first reported on **Friday 20 November
2026**. Excluded as 19 November news: the ICJ Myanmar genocide ruling,
the Shenzhen summit, Anthropic's $81.3bn debut, and the US Senate
Iran war-powers vote (51–48).

## Build

```bash
python3 main.py   # writes entry.png (1024x1024, deterministic)
```

Pure Pillow, no network access at render time. All artwork is generated
procedurally in-session (sunset coast, storm spiral, falling market
chart, and ten small motif strips). Running `main.py` twice produces
byte-identical output.

Sources: Reuters, AP, WSJ, CNN, BBC, Bloomberg and wire reports — all
figures as reported 20 November 2026.

## License

MIT — see [LICENSE](LICENSE).
