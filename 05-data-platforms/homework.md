# Module 5 Homework: Data Platforms with Bruin

In this homework, we'll use Bruin to build a complete data pipeline, from ingestion to reporting.

## Setup

1. Install Bruin CLI: `curl -LsSf https://getbruin.com/install/cli | sh`
2. Initialize the zoomcamp template: `bruin init zoomcamp my-pipeline`
3. Configure your `.bruin.yml` with a DuckDB connection
4. Follow the tutorial in the [main module README](../../../05-data-platforms/)

After completing the setup, you should have a working NYC taxi data pipeline.

---

### Question 1. Bruin Pipeline Structure

In a Bruin project, what are the required files/directories?

- `bruin.yml` and `assets/`
- `.bruin.yml` and `pipeline.yml` (assets can be anywhere)
- **`.bruin.yml` and `pipeline/` with `pipeline.yml` and `assets/`**
- `pipeline.yml` and `assets/` only

### Solution

`.bruin.yml` at the root, `pipeline.yml` inside `pipeline/`, and `assets/` next to it. Worth noting: Bruin looks for `.bruin.yml` at the git root, not wherever you run the command from. If your project is nested inside a larger repo, Bruin will find (or create) the wrong config. We ran into exactly this.

---

### Question 2. Materialization Strategies

You're building a pipeline that processes NYC taxi data organized by month based on `pickup_datetime`. Which incremental strategy is best for processing a specific interval period by deleting and inserting data for that time period?

- `append` - always add new rows
- `replace` - truncate and rebuild entirely
- **`time_interval` - incremental based on a time column**
- `view` - create a virtual table only

### Solution

`time_interval` does exactly what the question describes: for each run it deletes rows where `incremental_key` falls within the given window, then re-inserts the query results. You can reprocess any specific month without touching the rest of the table, which is useful when upstream data arrives late or you need to fix a bug in a past window.

---

### Question 3. Pipeline Variables

You have the following variable defined in `pipeline.yml`:

```yaml
variables:
  taxi_types:
    type: array
    items:
      type: string
    default: ["yellow", "green"]
```

How do you override this when running the pipeline to only process yellow taxis?

- `bruin run --taxi-types yellow`
- `bruin run --var taxi_types=yellow`
- **`bruin run --var 'taxi_types=["yellow"]'`**
- `bruin run --set taxi_types=["yellow"]`

### Solution

`--var` takes `key=value` pairs, and since `taxi_types` is an array, the value needs to be valid JSON. The single quotes around the whole thing are just shell quoting to stop the shell from interpreting the brackets and double quotes before Bruin sees them.

---

### Question 4. Running with Dependencies

You've modified the `ingestion/trips.py` asset and want to run it plus all downstream assets. Which command should you use?

- `bruin run ingestion.trips --all`
- **`bruin run ingestion/trips.py --downstream`**
- `bruin run pipeline/trips.py --recursive`
- `bruin run --select ingestion.trips+`

### Solution

`--downstream` runs the asset plus anything that depends on it. You reference assets by file path, not by their logical name, so `ingestion/trips.py` is the right form. We used this exact pattern when testing: `bruin run ./pipeline/assets/staging/trips.sql --downstream` to run staging and the report in one go.

---

### Question 5. Quality Checks

You want to ensure the `pickup_datetime` column in your trips table never has NULL values. Which quality check should you add to your asset definition?

- `name: unique`
- **`name: not_null`**
- `name: positive`
- `name: accepted_values, value: [not_null]`

### Solution

`not_null` fails if any row has a NULL in that column. We added it to `pickup_datetime` in `staging.trips` and Bruin ran it automatically after every execution.

---

### Question 6. Lineage and Dependencies

After building your pipeline, you want to visualize the dependency graph between assets. Which Bruin command should you use?

- `bruin graph`
- `bruin dependencies`
- **`bruin lineage`**
- `bruin show`

### Solution

`bruin lineage <path/to/asset>` shows what a given asset depends on and what depends on it. Useful before making changes: you can see what will break downstream before touching anything.

---

### Question 7. First-Time Run

You're running a Bruin pipeline for the first time on a new DuckDB database. What flag should you use to ensure tables are created from scratch?

- `--create`
- `--init`
- **`--full-refresh`**
- `--truncate`

### Solution

`--full-refresh` drops and recreates tables from scratch, bypassing the incremental logic. On a fresh database, `time_interval` fails because it tries to `DELETE FROM` a table that doesn't exist yet. `--full-refresh` skips that and just creates the table. We hit this on the first run of `staging.trips`.

---

## Submitting the solutions

- Form for submitting: <https://courses.datatalks.club/de-zoomcamp-2026/homework/hw5>

=======

## Learning in Public

We encourage everyone to share what they learned. This is called "learning in public".

Read more about the benefits [here](https://alexeyondata.substack.com/p/benefits-of-learning-in-public-and).

### Example post for LinkedIn

```
🚀 Week 5 of Data Engineering Zoomcamp by @DataTalksClub complete!

Just finished Module 5 - Data Platforms with Bruin. Learned how to:

✅ Build end-to-end ELT pipelines with Bruin
✅ Configure environments and connections
✅ Use materialization strategies for incremental processing
✅ Add data quality checks to ensure data integrity
✅ Deploy pipelines from local to cloud (BigQuery)

Modern data platforms in a single CLI tool - no vendor lock-in!

Here's my homework solution: <LINK>

Following along with this amazing free course - who else is learning data engineering?

You can sign up here: https://github.com/DataTalksClub/data-engineering-zoomcamp/
```

### Example post for Twitter/X

```
📊 Module 5 of Data Engineering Zoomcamp done!

- Data Platforms with Bruin
- End-to-end ELT pipelines
- Data quality & lineage
- Deployment to BigQuery

My solution: <LINK>

Free course by @DataTalksClub: https://github.com/DataTalksClub/data-engineering-zoomcamp/
```
