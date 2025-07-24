📡 SpotWave Backend (Python Package)

A modular Python backend for a Raspberry Pi to interacting with SpotWave sensors (active or passive), including data acquisition, configuration, and analysis tools.


🧭 Project Goal

This package provides the backend infrastructure for a RaspPI to:

    Read data from SpotWave sensors,
    Perform signal analysis and data processing,
    Configure sensor behavior using Python interfaces.


🔧 Installation

Clone the repository and install it in editable mode:

git clone https://github.com/J-Kol/rasppi-spotwave.git
cd rasppi-spotwave
pip install -e .

For development tools:

pip install -e .[dev]

📦 Dependencies

The following core packages are required to run the backend:
    FastAPI – High-performance web framework for building the API.
    Uvicorn – ASGI server used to serve the FastAPI application.
    Fastapi and pydantic - for docs
Optional (for development)
    Ruff – Lightning-fast Python linter (used in development).

    All dependencies are defined in pyproject.toml.


🧩 Module Overview (planned)

Module  Description:

sensor.py	measure with two sensors(active)
one_sensor.py measure with one sensor(passive)
analyzer.py	Signal processing and data analysis
config.py	Load, store, and apply configuration presets


🗺️ Example Usage (to be implemented)

(recommended in virtual environment)
start the backend with:
    uvicorn main:app --reload
and the frontend with python gui.py

🧪 Testing

Tests will be located under the tests/ directory, compatible with pytest.


🔧 Development Tools

    Ruff for code linting
    Hot-reload via uvicorn --reload


📄 License

MIT License


🛠 Project Status

done, but changes are likely
