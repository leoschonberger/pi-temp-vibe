#!/bin/bash

# Temperature Monitoring System - Quick Start Script

echo "🌡️  Temperature Monitoring System"
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found. Please run this script from the project root directory."
    exit 1
fi

echo "✅ Docker and Docker Compose found"
echo ""

# Get the current IP address
IP_ADDRESS=$(hostname -I | awk '{print $1}')
echo "📍 Your Raspberry Pi Zero IP address: $IP_ADDRESS"
echo ""

echo "🚀 Starting services..."
echo "   - MongoDB database"
echo "   - Backend API (port 5001)"
echo "   - Frontend dashboard (port 5000)"
echo ""

# Start the services
docker-compose up -d

# Wait a moment for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "🎉 Temperature Monitoring System is starting!"
echo ""
echo "📱 Access your dashboard at:"
echo "   http://$IP_ADDRESS:5000"
echo ""
echo "🔌 API endpoint:"
echo "   http://$IP_ADDRESS:5001"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose logs"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Update services: docker-compose pull && docker-compose up -d"
echo ""
echo "🔧 For Raspberry Pi Pico setup:"
echo "   1. Update the API_URL in micropython/pico_temp_sensor.py to:"
echo "      http://$IP_ADDRESS:5001/api/temperature"
echo "   2. Set your WiFi credentials in the same file"
echo "   3. Upload the code to your Pico"
echo ""
echo "📊 The dashboard will automatically detect new sensors and create charts!" 