# Historical Traffic Dataset Utilities

## Why historical data is required
The current system stores mostly live traffic snapshots from uploaded video analysis. That is useful for immediate monitoring, but it is too sparse for meaningful weekly and monthly analytics and for training a long-term prediction model.

Historical traffic records make the following possible:
- richer weekly and monthly analytics
- clearer trend reporting over time
- more stable LSTM training data
- better long-term planning for signal control

## How the dataset is generated
The generator script in this folder creates realistic traffic patterns for 90 days across 4 roads. It uses a simple but realistic schedule:
- Morning peak: 7 AM – 10 AM
- Lunch: 12 PM – 2 PM
- Evening peak: 5 PM – 8 PM
- Night: 9 PM – 6 AM

Weekdays and weekends follow slightly different patterns and the values include small variations so the data is not repetitive.

## How to generate the dataset
From the backend folder run:

```bash
python -m tools.generate_historical_dataset
```

This creates a CSV file at:
- backend/uploads/historical_traffic_dataset.csv

## How to import it into MongoDB
From the backend folder run:

```bash
python -m tools.import_historical_dataset
```

The import utility reads the CSV, validates the rows, converts timestamps into real DateTime values, and inserts the records into the existing traffic_logs collection while skipping duplicates on re-import.

## How to regenerate it
You can change the days, interval, or roads by editing the generator script or by importing it as a module and calling the function directly.

## Benefits for analytics and prediction
Once imported, the historical dataset improves:
- today's report accuracy
- weekly and monthly analytics quality
- chart trends over time
- LSTM training coverage

This remains isolated from the current upload, YOLO, dashboard, analytics, and prediction modules.
