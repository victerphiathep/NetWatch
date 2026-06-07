# Pandas Reference For NetWatch

## Core Mental Model

A pandas DataFrame is a table-shaped Python object. Rows are observations, columns are fields, and pandas gives us methods for selecting, filtering, grouping, sorting, summarizing, and exporting the data.

For NetWatch:

```text
One row = one node utilization reading at one timestamp
```

## First Inspection Commands

```python
df.head()
```

Shows the first 5 rows. Use this to quickly confirm the data loaded correctly.

```python
df.shape
```

Returns `(rows, columns)`.

```python
df.columns
```

Shows column names.

```python
df.info()
```

Shows column names, non-null counts, and data types.

```python
df.describe()
```

Shows summary statistics for numeric columns.

## Selecting Data

```python
df["node_id"]
```

Selects one column. This returns a pandas Series.

```python
df[["timestamp", "node_id", "region"]]
```

Selects multiple columns. This returns a DataFrame.

## Filtering Rows

```python
critical_readings = df[df["download_utilization_pct"] >= 85]
```

Returns only rows where download utilization is at least 85%.

In NetWatch, this means:

```text
critical reading = one hourly node reading above our threshold
```

## Counting Rows

```python
len(critical_readings)
```

Counts critical readings.

```python
critical_readings["node_id"].nunique()
```

Counts unique nodes that had at least one critical reading.

## Grouping

```python
critical_counts_by_node = (
    critical_readings
    .groupby("node_id")
    .size()
    .sort_values(ascending=False)
)
```

Groups critical readings by node, counts how many critical readings each node had, and sorts the result from highest to lowest.

This is similar to SQL:

```sql
SELECT node_id, COUNT(*)
FROM readings
WHERE download_utilization_pct >= 85
GROUP BY node_id
ORDER BY COUNT(*) DESC;
```

## Real-World Capacity Meaning

A single critical reading means a node crossed a threshold at one moment.

Repeated critical readings are more important because they suggest persistent congestion risk.

Capacity teams may use this kind of summary to prioritize:

```text
monitoring
investigation
forecasting
node splits
capacity upgrades
traffic engineering
```
