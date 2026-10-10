"""
Test script for verifying large file upload support.
Run manually to test with actual large files.

Usage:
    python -m pytest tests/test_large_upload.py -v -s
"""
from __future__ import annotations

import io
import tempfile
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    """Set up test client with isolated storage."""
    from app import config
    
    tmp = tmp_path_factory.mktemp("sf_large")
    config.UPLOAD_DIR = tmp / "uploads"
    config.MODEL_DIR = tmp / "models"
    config.MODEL_PATH = config.MODEL_DIR / "model.joblib"
    
    import app.state as state_mod
    state_mod.ACTIVE_META = config.UPLOAD_DIR / "active.json"
    
    from app.main import app
    with TestClient(app) as c:
        yield c


def test_file_extension_validation(client):
    """Verify that invalid file extensions are rejected."""
    bad_ext = io.BytesIO(b"some data")
    
    # Test .txt file (should fail)
    r = client.post("/api/dataset/upload", files={"file": ("bad.txt", bad_ext, "text/plain")})
    assert r.status_code == 400
    assert "Invalid file type" in r.json()["detail"]
    
    # Test .pdf file (should fail)
    r = client.post("/api/dataset/upload", files={"file": ("doc.pdf", bad_ext, "application/pdf")})
    assert r.status_code == 400
    assert "Invalid file type" in r.json()["detail"]


def test_small_csv_upload(client):
    """Verify that small valid CSV files are accepted."""
    from app import config
    
    df = pd.read_csv(config.SAMPLE_DATASET).head(100)
    csv_content = df.to_csv(index=False).encode()
    
    # Verify it's small
    assert len(csv_content) < 1_000_000  # < 1 MB
    
    # Upload should succeed
    r = client.post("/api/dataset/upload", files={
        "file": ("small.csv", io.BytesIO(csv_content), "text/csv")
    })
    assert r.status_code == 200, f"Upload failed: {r.text}"
    
    data = r.json()
    assert "dataset" in data
    assert "metrics" in data


def test_medium_csv_upload(client):
    """Test with a medium-sized file (simulated by repeating rows)."""
    from app import config
    
    df = pd.read_csv(config.SAMPLE_DATASET)
    
    # Repeat the dataset to create a larger file (still under limit)
    # Target: ~10 MB
    original_size = len(df.to_csv(index=False).encode())
    repetitions = max(1, (10 * 1024 * 1024) // original_size)
    
    large_df = pd.concat([df] * repetitions, ignore_index=True)
    csv_content = large_df.to_csv(index=False).encode()
    
    size_mb = len(csv_content) / (1024 * 1024)
    print(f"\nTest file size: {size_mb:.2f} MB")
    
    # Should be under the 350 MB limit
    assert size_mb < config.MAX_UPLOAD_MB
    
    # Upload should succeed
    r = client.post("/api/dataset/upload", files={
        "file": ("medium.csv", io.BytesIO(csv_content), "text/csv")
    })
    
    if r.status_code != 200:
        print(f"Error: {r.text}")
    
    assert r.status_code == 200, f"Upload failed for {size_mb:.2f} MB file"


def test_size_limit_configuration(client):
    """Verify the size limit is configured correctly."""
    from app import config
    
    # Should be 350 MB by default (or from environment)
    assert config.MAX_UPLOAD_MB > 0
    print(f"\nConfigured MAX_UPLOAD_MB: {config.MAX_UPLOAD_MB} MB")
    print(f"Max bytes: {config.MAX_UPLOAD_MB * 1024 * 1024:,}")


def test_xlsx_upload(client):
    """Test Excel file upload support."""
    from app import config
    
    df = pd.read_csv(config.SAMPLE_DATASET).head(100)
    
    # Create an Excel file in memory
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_content = excel_buffer.getvalue()
    
    print(f"\nExcel file size: {len(excel_content) / 1024:.2f} KB")
    
    # Upload should succeed
    r = client.post("/api/dataset/upload", files={
        "file": ("test.xlsx", io.BytesIO(excel_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    })
    assert r.status_code == 200, f"Excel upload failed: {r.text}"


@pytest.mark.skip(reason="Manual test - requires creating a very large file")
def test_oversized_file_rejection(client):
    """
    Test that files over the size limit are rejected.
    
    This test is skipped by default because it requires creating a >350 MB file.
    To run it manually, create a large CSV and update the path below.
    """
    from app import config
    
    # Create a file that exceeds the limit
    # This would need to be a real large file or simulated with a very large dataset
    limit_bytes = config.MAX_UPLOAD_MB * 1024 * 1024
    
    # For manual testing, replace with path to actual large file:
    # large_file_path = Path("/path/to/large_file.csv")
    # if large_file_path.exists():
    #     with open(large_file_path, "rb") as f:
    #         r = client.post("/api/dataset/upload", files={
    #             "file": ("huge.csv", f, "text/csv")
    #         })
    #         assert r.status_code == 413
    #         assert "too large" in r.json()["detail"].lower()
    
    pytest.skip("Manual test - create a >350 MB file to test")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "-s"])
