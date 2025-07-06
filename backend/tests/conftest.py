import os
os.environ["TESTING"] = "1"  # Phải nằm TRƯỚC mọi import khác

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from main import app
except ImportError:
    from app import app

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
