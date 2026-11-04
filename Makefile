.PHONY: niches stores-sanity stores-scan stores-meta stores-deep stores-ranks stores-build stores-report stores setup lint graph test wh-load wh-catalogue wh-offers wh-build wh-classify wh-images wh-export wh-snapshot intel pipeline

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

# --- Step 1: best online stores (decision 0009). Raw results stay in data/private/. ---
stores-scan:    ## Tranco top 1M, apex DNS, Shopify hits only; resumable tranches (~3 h)
	python3 -m scout.webmeta scan --top 1000000 --tranche 50000 --qps 100

stores-meta:    ## /meta.json for Shopify hits, best rank first (robots.txt respected)
	python3 -m scout.stores meta --max-stores 6000 --workers 6

stores-deep:    ## feed aggregates, homepage tags, DNS for the top US stores
	python3 -m scout.stores deep --max-stores 600 --workers 6 --pages 4

stores-ranks:   ## earlier Tranco ranks (rank growth)
	python3 -m scout.stores ranks --days-back 90 365

stores-build:   ## store models only (+ dbt tests)
	$(DBT) build --profiles-dir . --select stg_web_scan+ stg_web_scan_tranches stg_web_meta+ stg_web_store_deep+ stg_web_store_light+ stg_web_ranks+ mart_store_universe+ mart_niche_copyable mart_candidate_pool

stores-report:  ## private store stories + committed aggregate report
	python3 -m scout.store_intel --top 40
	python3 scripts/store_export.py

stores: stores-scan stores-meta stores-deep stores-ranks stores-build stores-report

stores-sanity:  ## quick CJ supply check for the latest niche shortlist (no cost)
	python3 scripts/supply_sanity.py

niches: stores stores-sanity   ## R1: the whole niche-finding run (docs/plan/phase-niche-finder-r1.md)
