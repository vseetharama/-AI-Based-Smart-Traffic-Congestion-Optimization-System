# 🚦 AI-Based Smart Traffic Congestion Optimization System
### Version 1.5.1 (Stable Release)

## Overview

AI-Based Smart Traffic Congestion Optimization System is a Final Year Engineering Project that uses Computer Vision and Artificial Intelligence to monitor traffic congestion, detect vehicles using YOLOv8, calculate road density, dynamically optimize traffic signals, and provide real-time analytics through an interactive web dashboard.

This version represents the first stable release with complete frontend-backend integration, MongoDB data storage, historical analytics, and report generation.

---

# Project Objectives

- Detect vehicles using YOLOv8
- Count vehicles on multiple roads
- Classify traffic density (LOW, MEDIUM, HIGH)
- Allocate adaptive green signal timing
- Store traffic history in MongoDB Atlas
- Display live dashboard
- Generate historical analytics
- Export PDF and CSV reports

---

# Features

## Home Page

- Modern Landing Page
- Technology Stack
- System Architecture
- Workflow Visualization
- Core Features
- Team Information

---

## Upload Module

Supports uploading traffic videos for:

- Road 1
- Road 2
- Road 3
- Road 4

Supported Formats

- MP4
- AVI
- MOV
- MKV
- WebM

---

## Vehicle Detection

Model Used

YOLOv8

Functions

- Vehicle Detection
- Vehicle Counting
- Density Classification

Density Levels

- LOW
- MEDIUM
- HIGH

---

## Adaptive Signal Control

Traffic signals are dynamically assigned based on

- Vehicle Count
- Density Level

Current Features

- Active Green Road
- Signal Timer
- Waiting Time
- Recommended Green Time

---

## Live Dashboard

Displays

- Backend Status
- Current Active Road
- Signal Timer
- Vehicle Count
- Highest Density
- Least Busy Road
- Current Green Signal
- Live Statistics

---

## Analytics

Historical analytics include

- Today's Traffic
- Weekly Analytics
- Monthly Analytics

Charts

- Vehicle Count per Road
- Density Distribution
- Live Traffic Trend
- Waiting Time Trend

---

## Report Generation

Supported Formats

- PDF
- CSV

Includes

- Vehicle Statistics
- Density Summary
- Waiting Time
- Historical Records

---

## Database

MongoDB Atlas

Stores

- Vehicle Counts
- Density
- Signal Status
- Waiting Time
- Recommended Green Time
- Prediction
- Timestamp

---

# Technology Stack

Frontend

- React.js
- Vite
- Bootstrap
- Recharts

Backend

- Python
- Flask

AI

- YOLOv8
- OpenCV

Database

- MongoDB Atlas

Reports

- ReportLab
- CSV Export

---

# Project Workflow

Upload Video

↓

YOLO Vehicle Detection

↓

Vehicle Counting

↓

Density Classification

↓

Adaptive Signal Timing

↓

MongoDB Storage

↓

Live Dashboard

↓

Historical Analytics

↓

PDF / CSV Report Generation

---

# Folder Structure

```
AI-Traffic-Control-System
│
├── backend
│   ├── app.py
│   ├── analytics.py
│   ├── reports.py
│   ├── worker.py
│   ├── traffic_controller.py
│   ├── traffic_logger.py
│   └── database.py
│
├── frontend
│   ├── src
│   ├── components
│   ├── pages
│   └── api
│
├── uploads
├── README.md
└── requirements.txt
```

---

# Current Version

Version

**v1.5.1**

Status

✅ Stable Release

---

# Known Limitations

- Uses rule-based adaptive signal optimization.
- No traffic prediction model yet.
- Emergency vehicle priority is not implemented.
- Reinforcement Learning optimization is not available.

---

# Future Improvements

- LSTM Traffic Prediction
- Hybrid Decision Score
- Emergency Vehicle Detection
- Reinforcement Learning
- Heatmap Visualization
- Admin Dashboard
- Cloud Deployment

---

# Developed By

Team 05

Department of Computer Science & Engineering

Final Year Engineering Project

2026

---

# License

Educational Project

For Academic Demonstration Only.