.PHONY: setup lint graph test wh-load wh-catalogue wh-offers wh-build wh-classify wh-images wh-export wh-snapshot intel pipeline

setup:
	python3 -m pip install --upgrade pre-commit graphifyy detect-secrets -r requirements.txt
	pre-commit install --install-hooks
	graphify hook install
	graphify claude install

lint:
	pre-commit run --all-files

graph:
	graphify update .

test:
	python3 -m pytest -q

# --- DuckDB warehouse (decision 0006). Raw lake + DB live in data/private/. ---
DBT = cd warehouse && DBT_TARGET_PATH=../data/private/dbt/target DBT_LOG_PATH=../data/private/dbt/logs dbt
wh-load:        ## CJ US catalogue + categories -> lake
	python3 -m scout.ingest_cj catalogue

wh-catalogue:   ## build everything that needs only the catalogue (+ dbt tests)
	$(DBT) build --profiles-dir . --select +mart_prefilter

wh-offers:      ## detail, stock, freight for mart_prefilter -> lake
	python3 -c "import duckdb; duckdb.connect('data/private/warehouse.duckdb', read_only=True).execute(\"copy mart.mart_prefilter to 'data/private/candidates.txt' (header false)\")"
	python3 -m scout.ingest_cj offers --from-file data/private/candidates.txt

wh-build:       ## full build: rules, staging, enrich, core, marts (+ dbt tests)
	$(DBT) build --profiles-dir .

wh-classify:    ## free LLM labels for titles the rules missed (cached in a seed)
	python3 -m scout.classify

wh-images:      ## free vision screen of viable candidates' first images (cached in a seed)
	python3 -m scout.screen_images

wh-export:      ## derived marts only -> committed files
	python3 scripts/wh_export.py

wh-snapshot:    ## catalogue snapshot only; run daily to build the time series (velocity)
	python3 -m scout.ingest_cj catalogue

intel:          ## intelligence layer: evidence packs -> grounded, cached narratives -> docs/reports
	python3 -m scout.intel

pipeline:       ## the whole flow in order: pull, build, export, intelligence
	$(MAKE) wh-load wh-catalogue wh-offers wh-build wh-export intel
