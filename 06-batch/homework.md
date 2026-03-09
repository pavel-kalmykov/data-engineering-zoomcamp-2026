# Module 6 Homework

In this homework we'll put what we learned about Spark in practice.

For this homework we will be using the Yellow 2025-11 data from the official website:

```bash
wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-11.parquet
```


## Question 1: Install Spark and PySpark

- Install Spark
- Run PySpark
- Create a local spark session
- Execute spark.version.

What's the output?

> [!NOTE]
> To install PySpark follow this [guide](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/06-batch/setup/)

### Solution

Using `mise` for Java 17 (Temurin) and `uv` for PySpark, no system-level installation needed.

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.master("local[*]").appName("homework").getOrCreate()
spark.version
```

Output: `'4.1.1'`

**Answer: `4.1.1`**


## Question 2: Yellow November 2025

Read the November 2025 Yellow into a Spark Dataframe.

Repartition the Dataframe to 4 partitions and save it to parquet.

What is the average size of the Parquet (ending with .parquet extension) Files that were created (in MB)? Select the answer which most closely matches.

- 6MB
- **25MB**
- 75MB
- 100MB

### Solution

```python
df = spark.read.parquet("yellow_tripdata_2025-11.parquet")
df.repartition(4).write.mode("overwrite").parquet("output/")

from pathlib import Path

files = list(Path("output").glob("*.parquet"))
sizes = [f.stat().st_size for f in files]
print(f"{sum(sizes) / len(sizes) / 1024 / 1024:.1f} MB")
```

Output: `24.4 MB`

**Answer: 25MB**


## Question 3: Count records

How many taxi trips were there on the 15th of November?

Consider only trips that started on the 15th of November.

- 62,610
- 102,340
- **162,604**
- 225,768

### Solution

```python
df.createOrReplaceTempView("trips")

spark.sql("""
    SELECT COUNT(*)
    FROM trips
    WHERE tpep_pickup_datetime >= '2025-11-15'
      AND tpep_pickup_datetime < '2025-11-16'
""").show()
```

Output: `162604`

**Answer: 162,604**


## Question 4: Longest trip

What is the length of the longest trip in the dataset in hours?

- 22.7
- 58.2
- **90.6**
- 134.5

### Solution

```python
spark.sql("""
    SELECT MAX(
        ROUND(
            (UNIX_TIMESTAMP(tpep_dropoff_datetime) - UNIX_TIMESTAMP(tpep_pickup_datetime)) / 3600,
            2
        )
    ) AS max_hours
    FROM trips
""").show()
```

Output: `90.65`

**Answer: 90.6**


## Question 5: User Interface

Spark's User Interface which shows the application's dashboard runs on which local port?

- 80
- 443
- **4040**
- 8080

### Solution

The Spark UI is available at `http://localhost:4040` while a SparkSession is active.

**Answer: 4040**


## Question 6: Least frequent pickup location zone

Load the zone lookup data into a temp view in Spark:

```bash
wget https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
```

Using the zone lookup data and the Yellow November 2025 data, what is the name of the LEAST frequent pickup location Zone?

- **Governor's Island/Ellis Island/Liberty Island**
- **Arden Heights**
- Rikers Island
- Jamaica Bay

If multiple answers are correct, select any

### Solution

```python
zones = spark.read.option("header", "true").csv("taxi_zone_lookup.csv")
zones.createOrReplaceTempView("zones")

spark.sql("""
    SELECT z.Zone, COUNT(*) AS cnt
    FROM trips t
    JOIN zones z ON t.PULocationID = z.LocationID
    GROUP BY z.Zone
    ORDER BY cnt ASC
""").show(5, truncate=False)
```

Output:

```
+---------------------------------------------+---+
|Zone                                         |cnt|
+---------------------------------------------+---+
|Governor's Island/Ellis Island/Liberty Island|1  |
|Eltingville/Annadale/Prince's Bay            |1  |
|Arden Heights                                |1  |
|Port Richmond                                |3  |
|Rikers Island                                |4  |
+---------------------------------------------+---+
only showing top 5 rows
```

Two zones are tied with 1 trip each. Selected: **Governor's Island/Ellis Island/Liberty Island**

## Submitting the solutions

- Form for submitting: https://courses.datatalks.club/de-zoomcamp-2026/homework/hw6
- Deadline: See the website


## Learning in Public

We encourage everyone to share what they learned. This is called "learning in public".

Read more about the benefits [here](https://alexeyondata.substack.com/p/benefits-of-learning-in-public-and).

### Example post for LinkedIn

```
🚀 Week 6 of Data Engineering Zoomcamp by @DataTalksClub complete!

Just finished Module 6 - Batch Processing with Spark. Learned how to:

✅ Set up PySpark and create Spark sessions
✅ Read and process Parquet files at scale
✅ Repartition data for optimal performance
✅ Analyze millions of taxi trips with DataFrames
✅ Use Spark UI for monitoring jobs

Processing 4M+ taxi trips with Spark - distributed computing is powerful! 💪

Here's my homework solution: <LINK>

Following along with this amazing free course - who else is learning data engineering?

You can sign up here: https://github.com/DataTalksClub/data-engineering-zoomcamp/
```

### Example post for Twitter/X

```
⚡ Module 6 of Data Engineering Zoomcamp done!

- Batch processing with Spark 🔥
- PySpark & DataFrames
- Parquet file optimization
- Spark UI on port 4040

My solution: <LINK>

Free course by @DataTalksClub: https://github.com/DataTalksClub/data-engineering-zoomcamp/
```
