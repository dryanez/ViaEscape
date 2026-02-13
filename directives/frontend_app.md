# Directive: Frontend Application

## Goal
Create a user-friendly web interface that requests the user's location and displays safety information.

## Technology
- **HTML/CSS**: Simple, responsive design (Mobile First).
- **JS**: Vanilla JS for Geolocation API and `fetch` calls.

## Features
1.  **Landing Screen**:
    - "Check My Safety" button.
    - Permission request explanation.
2.  **Loading State**:
    - "Acquiring location..."
    - "Analyzing hazards..."
3.  **Result Screen**:
    - **Safe**: Green background, "You are in a safe zone."
    - **Danger**: Red/Orange background, "Warning: Hazard Detected", map to meeting point.
    - **Route Info**: Display nearest evacuation route distance and name.

## API Integration
- **Endpoint**: `POST /api/check-hazard`
- **Body**: `{ "lat": ..., "lon": ... }`
- **Response Handling**:
    - Parse JSON.
    - Update DOM elements with `message`, `nearest_route`.

## Implementation
- `index.html`: Main entry point.
- `static/style.css`: Styling.
- `static/script.js`: Logic.
