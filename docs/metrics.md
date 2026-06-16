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
