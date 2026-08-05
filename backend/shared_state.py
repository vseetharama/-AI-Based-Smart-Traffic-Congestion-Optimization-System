import threading

# Shared state for all road worker threads.
# Each road entry stores the latest traffic estimation data that workers update.
road_results = {
    "road1": {
        "vehicle_count": 0,
        "predicted_vehicle_count": 0,
        "density_score": 0.0,
        "density_level": "LOW",
        "prediction_status": "pending",
        "recommended_green_time": 0,
        "signal_status": "red",
        "last_updated": None,
    },
    "road2": {
        "vehicle_count": 0,
        "predicted_vehicle_count": 0,
        "density_score": 0.0,
        "density_level": "LOW",
        "prediction_status": "pending",
        "recommended_green_time": 0,
        "signal_status": "red",
        "last_updated": None,
    },
    "road3": {
        "vehicle_count": 0,
        "predicted_vehicle_count": 0,
        "density_score": 0.0,
        "density_level": "LOW",
        "prediction_status": "pending",
        "recommended_green_time": 0,
        "signal_status": "red",
        "last_updated": None,
    },
    "road4": {
        "vehicle_count": 0,
        "predicted_vehicle_count": 0,
        "density_score": 0.0,
        "density_level": "LOW",
        "prediction_status": "pending",
        "recommended_green_time": 0,
        "signal_status": "red",
        "last_updated": None,
    },
}

# Shared state for the traffic controller.
# The controller reads road_results and writes this state for the API/dashboard.
controller_state = {
    "current_green_road": None,
    "current_timer": 0,
    "road_summaries": {
        "road1": {},
        "road2": {},
        "road3": {},
        "road4": {},
    },
    "timestamp": None,
}

# Lock protecting concurrent access to road_results.
# Workers update this data, and the controller reads it.
road_results_lock = threading.Lock()

# Lock protecting concurrent access to controller_state.
# The controller updates this state, and Flask endpoints may read it.
controller_state_lock = threading.Lock()

# Lock protecting shared YOLO inference access.
# Only one thread should run YOLO inference at a time using a shared model.
yolo_inference_lock = threading.Lock()
