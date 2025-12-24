# Power Suggestion Integration

Analyze power usage patterns of your home appliances and get AI-powered suggestions on the best time to run them based on solar forecasts.

## Features

- **Power Analysis**: Parses historical power data (up to 30 days) to identify usage cycles.
- **Solar Optimization**: Suggests start times aligned with your solar production and forecast.
- **AI Integration**: Offloads analysis data to an AI Task entity.
- **Cycle Management**: View and name detected cycles.
- **Lovelace Card**: Dedicated card for easy interaction.

## Installation

1. Install via HACS (Custom Repository).
2. Restart Home Assistant.
3. Go to **Settings > Devices & Services > Add Integration**.
4. Search for **Power Suggestion**.

## Configuration

When adding a device, provide:

- **Device Name**: Friendly name (e.g., Washing Machine).
- **Power Entity**: The sensor measuring the appliance's power usage (W).
- **AI Task Entity**: Entity ID of your AI agent/task handler.
- **Smart Meter Entity**: Grid import/export sensor.
- **Solar Power Entity**: Current solar production sensor.
- **Solar Forecast Entity**: Forecast entity (e.g., from `forecast_solar`).

## Usage

Once configured, the integration will start analyzing data. You can inspect the device page to see detected cycles and current status.
