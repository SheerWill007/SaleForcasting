#!/usr/bin/env python3
"""
Verification script for upload limit changes.
Run this to verify all changes were applied correctly.

Usage:
    python verify_changes.py
"""
from pathlib import Path
import sys


def check_file_contains(filepath: Path, expected_content: str, description: str) -> bool:
    """Check if a file contains expected content."""
    if not filepath.exists():
        print(f"❌ {description}: File not found: {filepath}")
        return False
    
    content = filepath.read_text(encoding='utf-8')
    if expected_content in content:
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description}: Expected content not found")
        return False


def main():
    """Run all verification checks."""
    print("=== Verifying Upload Limit Changes ===\n")
    
    root = Path(__file__).parent
    checks = []
    
    # Check 1: Backend config
    checks.append(check_file_contains(
        root / "backend" / "app" / "config.py",
        'MAX_UPLOAD_MB = int(os.getenv("SF_MAX_UPLOAD_MB", "350"))',
        "Backend config uses environment variable with 350 MB default"
    ))
    
    # Check 2: Backend upload handler streaming
    checks.append(check_file_contains(
        root / "backend" / "app" / "main.py",
        "while chunk := await file.read(8192)",
        "Backend uses streaming upload (8KB chunks)"
    ))
    
    # Check 3: Backend temp file cleanup
    checks.append(check_file_contains(
        root / "backend" / "app" / "main.py",
        "tempfile.mkstemp",
        "Backend uses temporary file for upload"
    ))
    
    # Check 4: Backend extension validation
    checks.append(check_file_contains(
        root / "backend" / "app" / "main.py",
        'if ext not in (".csv", ".xlsx", ".xls"):',
        "Backend validates file extensions"
    ))
    
    # Check 5: Frontend display
    checks.append(check_file_contains(
        root / "frontend" / "src" / "app" / "dashboard" / "data" / "page.tsx",
        "up to 350 MB",
        "Frontend displays 350 MB limit"
    ))
    
    # Check 6: .env.example
    checks.append(check_file_contains(
        root / "backend" / ".env.example",
        "SF_MAX_UPLOAD_MB=350",
        ".env.example includes SF_MAX_UPLOAD_MB"
    ))
    
    # Check 7: render.yaml
    checks.append(check_file_contains(
        root / "render.yaml",
        "SF_MAX_UPLOAD_MB",
        "render.yaml includes SF_MAX_UPLOAD_MB environment variable"
    ))
    
    # Check 8: Tests
    checks.append(check_file_contains(
        root / "backend" / "tests" / "test_api.py",
        "test_upload_size_limit",
        "test_api.py includes size limit test"
    ))
    
    # Check 9: New test file
    test_file = root / "backend" / "tests" / "test_large_upload.py"
    if test_file.exists():
        print(f"✅ Comprehensive upload test file created: {test_file.name}")
        checks.append(True)
    else:
        print(f"❌ Upload test file not found: {test_file}")
        checks.append(False)
    
    # Check 10: Documentation
    doc_file = root / "UPLOAD_LIMIT_CHANGES.md"
    if doc_file.exists():
        print(f"✅ Documentation created: {doc_file.name}")
        checks.append(True)
    else:
        print(f"❌ Documentation not found: {doc_file}")
        checks.append(False)
    
    # Check 11: README updated
    checks.append(check_file_contains(
        root / "README.md",
        "SF_MAX_UPLOAD_MB",
        "README.md includes SF_MAX_UPLOAD_MB configuration"
    ))
    
    # Check 12: Dropdown z-index fix
    checks.append(check_file_contains(
        root / "frontend" / "src" / "app" / "globals.css",
        "z-index: 200",
        "Dropdown z-index increased to 200 (CSS fix)"
    ))
    
    # Summary
    print(f"\n{'='*50}")
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"✅ All {total} checks passed!")
        print("\n🎉 Upload limit changes verified successfully!")
        print("\nNext steps:")
        print("1. Run tests: cd backend && pytest tests/test_large_upload.py -v")
        print("2. Test manually with the web interface")
        print("3. Deploy to production and monitor memory usage")
        return 0
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print(f"❌ {total - passed} checks failed")
        print("\nPlease review the failed checks above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
