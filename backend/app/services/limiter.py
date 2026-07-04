from slowapi import Limiter
from slowapi.util import get_remote_address

# 🔒 Memory-backed rate limiter tracking client remote IP addresses
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)