# Turkish Address Resolution System

An AI-powered address resolution system for parsing, standardizing, and matching Turkish addresses with high accuracy.

## Overview

This project implements a comprehensive address resolution system specifically designed for Turkish addresses. It handles various challenges including:
- Address abbreviations and variations
- Turkish character normalization
- Fuzzy matching for similar addresses
- Geographic component extraction
- Address validation and correction

## Features

- **Address Parser**: Extracts structured components from raw Turkish addresses
- **Address Matcher**: Matches similar addresses using multiple algorithms
- **Address Validator**: Validates address components against a database
- **Address Corrector**: Fixes common spelling mistakes and abbreviations
- **Geocoding Engine**: Provides geographic coordinates for addresses
- **Batch Processing**: Handles large-scale address datasets efficiently

## Project Structure

```
├── src/
│   ├── core/           # Core modules (parser, matcher, validator)
│   ├── services/       # Service modules (geocoding, intelligence)
│   ├── utils/          # Utility functions (text processing, normalization)
│   └── models/         # Data models and schemas
├── tests/
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── scripts/            # Helper scripts and demos
├── data/
│   ├── csv/            # CSV data files
│   └── sql/            # SQL schema and queries
├── config/             # Configuration files
└── docs/               # Documentation
```

## Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12+ with PostGIS extension
- Git

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/turkish-address-system.git
cd turkish-address-system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
# Create PostgreSQL database
createdb address_system

# Run initialization scripts
psql -d address_system -f data/sql/01_create_extensions.sql
psql -d address_system -f data/sql/02_create_schema.sql
psql -d address_system -f data/sql/02_create_tables.sql
```

5. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

## Usage

### Basic Usage

```python
from src.core.address_parser import AddressParser
from src.core.address_matcher import AddressMatcher

# Initialize components
parser = AddressParser()
matcher = AddressMatcher()

# Parse an address
raw_address = "Kızılay Mah. Atatürk Blv. No:25 Çankaya/Ankara"
parsed = parser.parse(raw_address)
print(parsed)

# Match addresses
address1 = "Kızılay Mahallesi Atatürk Bulvarı 25"
address2 = "kizilay mah ataturk blv no 25"
similarity = matcher.calculate_similarity(address1, address2)
print(f"Similarity: {similarity}")
```

### API Usage

Start the FastAPI server:
```bash
uvicorn src.api.main:app --reload
```

API documentation will be available at `http://localhost:8000/docs`

### Batch Processing

```python
from src.services.batch_processor import BatchProcessor

processor = BatchProcessor()
results = processor.process_file("data/csv/addresses.csv")
processor.save_results(results, "output/processed_addresses.csv")
```

## Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src tests/
```

Run specific test suite:
```bash
pytest tests/unit/
pytest tests/integration/
```

## Performance

- Processing speed: ~1000 addresses/second
- Matching accuracy: >85% F1-score
- Memory usage: <2GB for 1M addresses
- API response time: <200ms per request

## Contributing

Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Documentation

Detailed documentation is available in the `docs/` directory:
- [Architecture Overview](docs/TECHNICAL_DOCUMENTATION.md)
- [API Reference](docs/API_REFERENCE.md)
- [Development Guide](docs/DEVELOPMENT_GUIDE.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Uses OpenStreetMap data for geographic validation
- Built with FastAPI, PostgreSQL, and scikit-learn

## Contact

For questions and support, please open an issue on GitHub.
