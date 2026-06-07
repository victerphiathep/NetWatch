# NetWatch
Mock network capacity monitoring dashboard

__________________________________________

Generate mock readings
        ↓
Store in SQLite
        ↓
Use SQL to query raw data
        ↓
Use pandas to transform and summarize it
        ↓
Load summary data back into SQLite
        ↓
Visualize with Plotly
        ↓
Use RAG to ask questions about the results

___________________________________________

Node = shared network capacity point serving a group of customers
High utilization = many customers competing for finite bandwidth
Repeated high utilization = possible capacity risk
Capacity planning = deciding when and how to add relief before users suffer