# NetWatch Metrics

This document defines the metrics used by NetWatch. Clear metric definitions matter because different teams can interpret the same phrase differently.

## Reading-Level Metrics

### download_utilization_pct

Downstream utilization percentage for a node at a specific timestamp.

In a residential network, downstream traffic is often heavily influenced by streaming, downloads, gaming, and general internet usage.

Expected range:

```text
0 <= download_utilization_pct <= 100
```

### upload_utilization_pct

Upstream utilization percentage for a node at a specific timestamp.

Upload utilization may be influenced by video calls, cloud backups, livestreaming, file uploads, and work-from-home behavior.

Expected range:

```text
0 <= upload_utilization_pct <= 100
```

### status

Reading-level status derived from `download_utilization_pct`.

Rules:

```text
critical: download_utilization_pct >= 85
warning:  70 <= download_utilization_pct < 85
normal:   download_utilization_pct < 70
```

Important distinction:

```text
A critical reading is one timestamped event.
A critical node is a node with repeated or severe concerning readings.
```

## Node-Level Metrics

### avg_download_utilization

Average downstream utilization for a node across the reporting window.

Use this to understand typical load.

### max_download_utilization

Maximum downstream utilization observed for a node across the reporting window.

Use this to identify severe spikes.

### avg_upload_utilization

Average upstream utilization for a node across the reporting window.

Use this to understand typical upstream load.

### max_upload_utilization

Maximum upstream utilization observed for a node across the reporting window.

Use this to identify severe upstream spikes.

### total_reading_count

Number of raw readings available for a node.

In the current mock dataset, each node is expected to have:

```text
7 days x 24 hours = 168 readings
```

If this value is lower or higher than expected, it may indicate missing or duplicate telemetry.

### critical_reading_count

Number of readings where:

```text
download_utilization_pct >= 85
```

This measures how often a node crossed the critical downstream threshold.

### critical_reading_pct

Percentage of readings that were critical.

Formula:

```text
critical_reading_count / total_reading_count * 100
```

This normalizes critical events by total available readings.

### peak_hour_avg_download_utilization

Average downstream utilization during peak hours only.

Current peak-hour definition:

```text
18:00 through 22:00
```

This helps distinguish general utilization from evening-window demand.

### peak_hour_max_download_utilization

Maximum downstream utilization observed during peak hours only.

Use this to identify severe evening-window congestion.

### peak_hour_total_reading_count

Number of readings available during the peak-hour window.

In the current mock dataset, each node is expected to have:

```text
7 days x 5 peak hours = 35 peak-hour readings
```

### peak_hour_critical_reading_count

Number of peak-hour readings where:

```text
download_utilization_pct >= 85
```

This is especially useful for capacity planning because repeated evening critical events may indicate predictable customer-demand pressure.

### first_day_avg_download_utilization

Average downstream utilization for the node on the first day in the reporting window.

This is used as the starting point for the simple trend calculation.

### last_day_avg_download_utilization

Average downstream utilization for the node on the last day in the reporting window.

This is used as the ending point for the simple trend calculation.

### download_utilization_change

Difference between last-day average downstream utilization and first-day average downstream utilization.

Formula:

```text
last_day_avg_download_utilization - first_day_avg_download_utilization
```

Unit:

```text
percentage points
```

Example:

```text
first day average = 50%
last day average = 62%
download_utilization_change = +12 percentage points
```

This is not a forecast. It is a simple directional signal showing whether utilization increased or decreased across the reporting window.

## Anomaly Detection

NetWatch currently uses a simple node-specific standard deviation rule.

For each node:

```text
anomaly_threshold = node_avg_download_utilization + (2 * node_std_download_utilization)
```

A reading is flagged as an anomaly when:

```text
download_utilization_pct > anomaly_threshold
```

### anomaly_score

Measures how many standard deviations the reading is above the node's average.

Formula:

```text
(download_utilization_pct - node_avg_download_utilization) / node_std_download_utilization
```

Important production note:

```text
An anomaly is not automatically a network fault.
```

It means the reading is unusual compared with that node's normal behavior and should be investigated. Possible causes include real congestion, local events, rerouted traffic, telemetry issues, or one-off customer behavior.

## Risk Level

`risk_level` is a node-level label used to make the summary easier to interpret.

Rules:

```text
high_risk:
    critical_reading_count >= 5
    OR max_download_utilization >= 90

watch:
    critical_reading_count >= 2
    OR avg_download_utilization >= 65

normal:
    everything else
```

## Business Meaning

`normal`:

The node does not currently show repeated or severe downstream utilization risk based on the mock rules.

`watch`:

The node has some concerning activity and should be monitored.

`high_risk`:

The node has repeated critical readings or a severe utilization spike and should be prioritized for review.

## Production Notes

These thresholds are simplified for learning.

In a real capacity management environment, thresholds might depend on:

```text
technology type
region
service group size
customer count
peak-hour behavior
historical trend
forecasted growth
planned upgrades
known outages or maintenance
```

Real systems may also calculate risk using rolling windows, percentile metrics, trend slopes, anomaly detection, or ML forecasting.
