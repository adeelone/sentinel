.PHONY: install data train evaluate report serve worker test lint format typecheck migrate seed clean

install:
	cd ml && python -m pip install -e .[dev]
	cd backend && python -m pip install -e .[dev]
	cd frontend && npm install

data:
	cd ml && python -m sentinel_ml.data.download

train:
	cd ml && python -m sentinel_ml.train --dataset synthetic

evaluate:
	cd ml && python -m sentinel_ml.evaluate --dataset synthetic

report:
	cd ml && python -m sentinel_ml.report

serve:
	cd backend && uvicorn app.main:app --reload

worker:
	cd backend && python -m app.jobs.worker

test:
	cd ml && python -m pytest
	cd backend && python -m pytest
	cd frontend && npm test -- --run

lint:
	cd ml && ruff check .
	cd backend && ruff check .
	cd frontend && npm run lint

format:
	cd ml && black . && ruff check --fix .
	cd backend && black . && ruff check --fix .
	cd frontend && npm run format

typecheck:
	cd ml && mypy sentinel_ml
	cd backend && mypy app
	cd frontend && npm run typecheck

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python -m app.db.seed

clean:
	git clean -xfd reports ml/.pytest_cache backend/.pytest_cache frontend/dist frontend/coverage

