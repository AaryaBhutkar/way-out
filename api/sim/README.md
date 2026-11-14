# api/sim/ — stand-ins (Dev 2, D2-02 / D2-09)

- `seed.py`: `POST /sim/seed?scenario=pocket-fire` → ~200 households, 8 vehicles, 2 shelters (`simulated: true`)
- `drivers.py`: stand-in drivers accept after 6 s and drive their routes
- `compare.py`: impact comparison, 50 seeds → `data/sim-results.json`

Everything from here is labeled **SIM** in the UI.
