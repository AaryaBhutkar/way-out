# api/hazard/ — fire model (Yash, D2-07)

- `firms.py`: NASA FIRMS VIIRS NRT for the bbox, or replay `data/scenario.json`
- `spread.py`: elliptical (Huygens) spread → `fireArrivalAt` per home → `deadlineAt = arrival − 10 min`
- Front within 100 m of a road → `POST /roads/closures` with `source: hazard`
- Console label: "scenario input, not a forecast"
