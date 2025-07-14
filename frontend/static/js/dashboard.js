class TemperatureDashboard {
	constructor() {
		this.charts = new Map();
		this.sensors = [];
		this.currentTimeFilter = 24; // Default to 24 hours
		this.refreshInterval = null;
		this.isConnected = false;

		this.initializeEventListeners();
		this.loadSensors();
		this.startAutoRefresh();
	}

	initializeEventListeners() {
		// Time filter change
		document.getElementById("timeFilter").addEventListener("change", (e) => {
			this.currentTimeFilter = parseInt(e.target.value);
			this.refreshAllCharts();
		});

		// Manual refresh button
		document.getElementById("refreshBtn").addEventListener("click", () => {
			this.refreshAllCharts();
		});

		// Touch-friendly interactions for mobile
		this.addTouchSupport();

		// Handle window resize for responsive charts
		window.addEventListener(
			"resize",
			this.debounce(() => {
				this.resizeAllCharts();
			}, 250)
		);
	}

	addTouchSupport() {
		// Add touch feedback for buttons
		const buttons = document.querySelectorAll("button, select");
		buttons.forEach((button) => {
			button.addEventListener("touchstart", () => {
				button.style.transform = "scale(0.95)";
			});

			button.addEventListener("touchend", () => {
				button.style.transform = "";
			});
		});
	}

	debounce(func, wait) {
		let timeout;
		return function executedFunction(...args) {
			const later = () => {
				clearTimeout(timeout);
				func(...args);
			};
			clearTimeout(timeout);
			timeout = setTimeout(later, wait);
		};
	}

	async loadSensors() {
		try {
			this.updateConnectionStatus("connecting");

			const response = await fetch("/api/sensors");
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			this.sensors = data.sensors || [];

			this.updateConnectionStatus("connected");
			this.renderSensors();
		} catch (error) {
			console.error("Error loading sensors:", error);
			this.updateConnectionStatus("disconnected");
			this.showNoDataMessage();
		}
	}

	renderSensors() {
		const sensorGrid = document.getElementById("sensorGrid");
		const noDataMessage = document.getElementById("noDataMessage");

		if (this.sensors.length === 0) {
			sensorGrid.innerHTML = "";
			noDataMessage.style.display = "block";
			return;
		}

		noDataMessage.style.display = "none";
		sensorGrid.innerHTML = "";

		this.sensors.forEach((sensor) => {
			const sensorCard = this.createSensorCard(sensor);
			sensorGrid.appendChild(sensorCard);
		});

		// Load data for all sensors
		this.refreshAllCharts();
	}

	createSensorCard(sensor) {
		const card = document.createElement("div");
		card.className = "sensor-card";
		card.id = `sensor-${sensor.name}`;

		const latestTime = new Date(sensor.latest_timestamp).toLocaleString();
		const isActive = this.isSensorActive(sensor.latest_timestamp);

		card.innerHTML = `
            <div class="sensor-header">
                <div class="sensor-name">${this.escapeHtml(sensor.name)}</div>
                <div class="sensor-status">
                    <span class="sensor-status-dot ${
											isActive ? "active" : ""
										}"></span>
                    <span>${isActive ? "Active" : "Inactive"}</span>
                </div>
            </div>
            <div class="current-temp">
                <div class="temp-value">${sensor.latest_temperature.toFixed(
									1
								)}</div>
                <div class="temp-unit">°C</div>
                <div class="temp-time">${latestTime}</div>
            </div>
            <div class="chart-container">
                <canvas id="chart-${sensor.name}"></canvas>
            </div>
        `;

		return card;
	}

	isSensorActive(timestamp) {
		const lastReading = new Date(timestamp);
		const now = new Date();
		const diffHours = (now - lastReading) / (1000 * 60 * 60);
		return diffHours < 1; // Consider active if last reading was within 1 hour
	}

	async refreshAllCharts() {
		const promises = this.sensors.map((sensor) =>
			this.loadSensorData(sensor.name)
		);
		await Promise.all(promises);
		this.updateLastUpdateTime();
	}

	async loadSensorData(sensorName) {
		try {
			const response = await fetch(
				`/api/temperature/history?sensor_name=${encodeURIComponent(
					sensorName
				)}&hours=${this.currentTimeFilter}`
			);
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			this.updateChart(sensorName, data.readings);
		} catch (error) {
			console.error(`Error loading data for sensor ${sensorName}:`, error);
			this.showChartError(sensorName);
		}
	}

	updateChart(sensorName, readings) {
		const canvas = document.getElementById(`chart-${sensorName}`);
		if (!canvas) return;

		// Destroy existing chart if it exists
		if (this.charts.has(sensorName)) {
			this.charts.get(sensorName).destroy();
		}

		const ctx = canvas.getContext("2d");

		// Prepare data for Chart.js
		const chartData = {
			labels: readings.map((r) => new Date(r.timestamp)),
			datasets: [
				{
					label: "Temperature (°C)",
					data: readings.map((r) => r.temperature),
					borderColor: this.getChartColor(sensorName),
					backgroundColor: this.getChartColor(sensorName, 0.1),
					borderWidth: 2,
					fill: true,
					tension: 0.4,
					pointRadius: 3,
					pointHoverRadius: 6,
					pointBackgroundColor: this.getChartColor(sensorName),
					pointBorderColor: "#fff",
					pointBorderWidth: 2,
				},
			],
		};

		const chart = new Chart(ctx, {
			type: "line",
			data: chartData,
			options: this.getChartOptions(),
		});

		this.charts.set(sensorName, chart);
	}

	getChartColor(sensorName, alpha = 1) {
		// Generate consistent colors for each sensor
		const colors = [
			`rgba(102, 126, 234, ${alpha})`, // Blue
			`rgba(237, 100, 166, ${alpha})`, // Pink
			`rgba(34, 197, 94, ${alpha})`, // Green
			`rgba(251, 146, 60, ${alpha})`, // Orange
			`rgba(168, 85, 247, ${alpha})`, // Purple
			`rgba(239, 68, 68, ${alpha})`, // Red
			`rgba(16, 185, 129, ${alpha})`, // Emerald
			`rgba(245, 158, 11, ${alpha})`, // Yellow
		];

		const index =
			sensorName.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0) %
			colors.length;
		return colors[index];
	}

	getChartOptions() {
		const isMobile = window.innerWidth <= 768;

		return {
			responsive: true,
			maintainAspectRatio: false,
			interaction: {
				intersect: false,
				mode: "index",
			},
			plugins: {
				legend: {
					display: false,
				},
				tooltip: {
					backgroundColor: "rgba(0, 0, 0, 0.8)",
					titleColor: "#fff",
					bodyColor: "#fff",
					borderColor: "rgba(255, 255, 255, 0.2)",
					borderWidth: 1,
					cornerRadius: 8,
					displayColors: false,
					callbacks: {
						title: (context) => {
							const date = new Date(context[0].parsed.x);
							return date.toLocaleString();
						},
						label: (context) => {
							return `Temperature: ${context.parsed.y.toFixed(1)}°C`;
						},
					},
				},
			},
			scales: {
				x: {
					type: "time",
					time: {
						unit: this.getTimeUnit(),
						displayFormats: {
							hour: "HH:mm",
							day: "MMM dd",
							week: "MMM dd",
							month: "MMM yyyy",
						},
					},
					grid: {
						color: "rgba(0, 0, 0, 0.1)",
					},
					ticks: {
						maxTicksLimit: isMobile ? 5 : 10,
						color: "#718096",
					},
				},
				y: {
					beginAtZero: false,
					grid: {
						color: "rgba(0, 0, 0, 0.1)",
					},
					ticks: {
						color: "#718096",
						callback: (value) => `${value}°C`,
					},
				},
			},
			elements: {
				point: {
					hoverRadius: isMobile ? 8 : 6,
				},
			},
		};
	}

	getTimeUnit() {
		if (this.currentTimeFilter <= 24) return "hour";
		if (this.currentTimeFilter <= 168) return "day";
		if (this.currentTimeFilter <= 720) return "week";
		return "month";
	}

	showChartError(sensorName) {
		const canvas = document.getElementById(`chart-${sensorName}`);
		if (!canvas) return;

		const ctx = canvas.getContext("2d");
		ctx.clearRect(0, 0, canvas.width, canvas.height);

		ctx.fillStyle = "#718096";
		ctx.font = "14px sans-serif";
		ctx.textAlign = "center";
		ctx.fillText("Error loading data", canvas.width / 2, canvas.height / 2);
	}

	resizeAllCharts() {
		this.charts.forEach((chart) => {
			chart.resize();
		});
	}

	updateConnectionStatus(status) {
		const statusDot = document.querySelector(".status-dot");
		const statusText = document.querySelector(".status-text");

		statusDot.className = `status-dot ${status}`;

		switch (status) {
			case "connected":
				statusText.textContent = "Connected";
				this.isConnected = true;
				break;
			case "connecting":
				statusText.textContent = "Connecting...";
				this.isConnected = false;
				break;
			case "disconnected":
				statusText.textContent = "Disconnected";
				this.isConnected = false;
				break;
		}
	}

	updateLastUpdateTime() {
		const lastUpdate = document.getElementById("lastUpdate");
		const now = new Date();
		lastUpdate.textContent = `Last update: ${now.toLocaleTimeString()}`;
	}

	showNoDataMessage() {
		const sensorGrid = document.getElementById("sensorGrid");
		const noDataMessage = document.getElementById("noDataMessage");

		sensorGrid.innerHTML = "";
		noDataMessage.style.display = "block";
	}

	startAutoRefresh() {
		// Refresh every 30 seconds
		this.refreshInterval = setInterval(() => {
			if (this.isConnected) {
				this.loadSensors();
			}
		}, 30000);
	}

	stopAutoRefresh() {
		if (this.refreshInterval) {
			clearInterval(this.refreshInterval);
			this.refreshInterval = null;
		}
	}

	escapeHtml(text) {
		const div = document.createElement("div");
		div.textContent = text;
		return div.innerHTML;
	}
}

// Initialize dashboard when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
	new TemperatureDashboard();
});

// Handle page visibility changes for better mobile experience
document.addEventListener("visibilitychange", () => {
	if (document.hidden) {
		// Page is hidden, could stop auto-refresh to save resources
		console.log("Page hidden");
	} else {
		// Page is visible again, refresh data
		console.log("Page visible");
		// Trigger a refresh when page becomes visible
		setTimeout(() => {
			window.location.reload();
		}, 1000);
	}
});
