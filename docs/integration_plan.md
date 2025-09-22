Integration plan: JSON instruction style template for wildfire responses in the fire-behavior project

Overview
- Objective: Integrate the existing wildfire_prompt_template.json (which defines a data_contract for wildfire, weather, and road information) into both the backend (API that produces responses) and the frontend (React UI in fire-behavior) so that responses conform to a single, well-defined JSON schema.

Proposed architecture
- Backend API (Python)
  - Framework: FastAPI (recommended for its simplicity and built-in validation with Pydantic)
  - Endpoints:
    - POST /brief
      - Request: { "location": string, "as_of": string (ISO 8601, optional), "data_sources": [ { "name": string, "type": string } ] (optional) }
      - Response: JSON payload conforming to the template’s response_schema defined in wildfire_prompt_template.json
  - Core steps:
    - Load the wildfire_prompt_template.json to understand the required response_schema and llm_instruction
    - Gather data from data_sources (weather, wildfire status, road conditions) using modular fetchers
    - Populate a response payload that matches the template_schema
    - Validate the payload against the schema before sending
  - Data fetchers (placeholders initially, to be expanded):
    - fetch_weather(location)
    - fetch_wildfire_status(location)
    - fetch_road_conditions(location)
  - Validation:
    - Use Pydantic models derived from the template_schema for runtime validation
  - Security & quality:
    - CORS, rate limiting, input validation, and error handling
    - Simple unit tests for each fetcher and for the payload builder

- Frontend UI (React)
  - Components:
    - WildfireBriefPanel.jsx (new or integrated into App.jsx)
      - Calls the backend API: POST /brief with location data
      - Renders sections:
        - Wildfire Status
        - Weather Risks (including probability of rain, red flag warnings, extreme changes)
        - Road Conditions
        - Notes / Data Sources
      - Error handling and loading states
  - Data contract:
    - Consume the same JSON structure produced by the backend
    - Use a single Source-of-Truth JSON to render UI sections

- Data contract alignment
  - Reuse the wildfire_prompt_template.json as the canonical source for:
    - response_schema
    - llm_instruction
  - Ensure the backend fills fields that match this schema exactly
  - The frontend should not expect any additional fields beyond those defined in the template

Implementation plan (phases)
Phase 1: Prepare backend skeleton
- [ ] Create a FastAPI app under fire-behavior/server
- [ ] Implement POST /brief endpoint
- [ ] Load and parse wildfire_prompt_template.json
- [ ] Create Pydantic models that reflect response_schema
- [ ] Implement stub data fetchers returning sample data
- [ ] Validate responses against the schema

Phase 2: Implement data fetchers
- [ ] Implement fetch_weather(location) returning sample probability_of_rain, temperature, humidity, wind
- [ ] Implement fetch_wildfire_status(location) returning sample incident_id, name, status, acres, containment
- [ ] Implement fetch_road_conditions(location) returning sample closures, delays, visibility
- [ ] Wire fetchers into the /brief flow and handle missing data gracefully

Phase 3: Frontend integration
- [ ] Add a WildfireBriefPanel component in fire-behavior/src/App.jsx or as a new component
- [ ] Implement API call to /brief and handle responses
- [ ] Render the sections with proper labeling and formatting
- [ ] Add basic error/loading UI

Phase 4: Validation, tests, and docs
- [ ] Add unit tests for backend: schema validation, fetcher outputs
- [ ] Add end-to-end tests (mock backend)
- [ ] Update README with integration steps and API contract
- [ ] Add CI workflow to validate JSON structure and tests

Sample API contract (pseudo)
- Backend (Python FastAPI)
  - POST /brief
    - Request body: { "location": "City, State" }
    - Response body: conforms to wildfire_prompt_template.json response_schema
  - Data flow:
    - Template loaded from wildfire_prompt_template.json
    - Data fetchers populate fields:
      - wildfire_status
      - weather_risks
      - road_conditions
    - Validation against response_schema
    - Return payload

Frontend usage sketch (React)
- Fetch example (pseudo)
  - fetch("/brief", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ location: "Sample City" }) })
  - On success, render sections:
    - Wildfire Status: name, status, acres, containment
    - Weather Risks: probability_of_rain, red_flag_warnings, extreme_changes
    - Road Conditions: closures, delays, visibility
  - Show data_sources and notes as supplemental information

Notes and considerations
- Start with a minimal viable integration: a backend that returns a static payload matching the template, then progressively replace static payloads with real fetchers.
- Ensure that the template’s response_schema is treated as a strict contract; any change in the template should propagate to both backend validation and frontend rendering.
- Consider versioning the template file; store a version field in the payload or in the API response headers to aid forward compatibility.
- If you plan to run the backend locally alongside the existing Python scripts, consider organizing as a small API module (fire-behavior/server) to keep responsibilities clear.

Commands you might run
- Implementing a minimal backend skeleton (after you approve):
  - Create server structure, then run a local server, e.g., uvicorn or a small Flask app
- Frontend fetch integration will use standard fetch and React state to render

Next steps
- Confirm you’d like me to generate a concrete code scaffold (filesystem changes with boilerplate for fire-behavior/server and a basic React integration) or provide a more detailed step-by-step with code templates for each file.
