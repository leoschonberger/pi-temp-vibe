// MongoDB initialization script
db = db.getSiblingDB("temperature_db");

// Create temperature_readings collection
db.createCollection("temperature_readings");

// Create indexes for better query performance
db.temperature_readings.createIndex({ sensor_name: 1, timestamp: -1 });
db.temperature_readings.createIndex({ timestamp: -1 });

print("Temperature monitoring database initialized successfully");
