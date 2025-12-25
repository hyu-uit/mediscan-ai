# MediScan AI

AI-powered medication analysis and processing service for the MediScan application.

## Setup

### Prerequisites

- Python 3.11+
- pip or uv

### Installation

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Development

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

## Project Structure

```
mediscan-ai/
├── src/
│   └── mediscan_ai/
│       ├── __init__.py
│       └── main.py
├── tests/
│   └── __init__.py
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
└── README.md
```

## Usage

```bash
python -m mediscan_ai
```

## License

MIT

