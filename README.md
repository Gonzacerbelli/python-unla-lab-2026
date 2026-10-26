Fastapi Python Example for UNLa SL

## Instalation

- Open Powershell/Bash/Terminal and navigate to project folder. 
- Run `python -m venv .venv` for creating venv.
- Run `.venv/Scripts/activate` for activating venv on Windows.
- Run `pip install -r requirements.txt` for installing libraries from requirements file.
- Run `fastapi run` for running app at localhost and default port (8000).
- Open browser and go to [localhost:8000/docs](localhost:8000/docs) for swagger documentation.

## Queries

- `GET /products/best-sellers` returns the 5 products with the highest quantity sold.
- `GET /sales/most-profitable` returns the 5 sales with the highest total price.
- `GET /sales?date-from=2026-10-20&date-to=2026-10-23` filters sales by an inclusive date range.