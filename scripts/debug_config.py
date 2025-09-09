#!/usr/bin/env python3
"""
Debug Config Parsing
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test parsing
jwt_claims = os.getenv("JWT_REQUIRE_CLAIMS")
print(f"JWT_REQUIRE_CLAIMS raw: '{jwt_claims}'")
print(f"Type: {type(jwt_claims)}")

if jwt_claims:
    parsed = [item.strip() for item in jwt_claims.split(',') if item.strip()]
    print(f"Parsed: {parsed}")
    print(f"Parsed type: {type(parsed)}")

# Test the Settings import
try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from src.core.config import Settings
    settings = Settings()
    print("✅ Settings loaded successfully!")
    print(f"JWT claims: {settings.jwt_require_claims}")
    print(f"Legendary scopes: {settings.descope_legendary_scopes}")
except Exception as e:
    print(f"❌ Settings error: {str(e)}")
    import traceback
    traceback.print_exc()