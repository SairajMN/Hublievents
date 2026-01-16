"""
Password hashing utilities for Hublievents Backend API.
Provides secure password hashing and verification.
"""

from passlib.context import CryptContext
from passlib.exc import UnknownHashError

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches hash, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except UnknownHashError:
        # Handle unknown hash formats gracefully
        return False


def is_password_compromised(password: str) -> bool:
    """
    Check if password appears in common password lists.
    Note: This is a basic check. In production, integrate with
    services like HaveIBeenPwned API.

    Args:
        password: Password to check

    Returns:
        True if password is compromised, False otherwise
    """
    # Basic check for common passwords
    common_passwords = {
        "password", "123456", "123456789", "qwerty", "abc123",
        "password123", "admin", "letmein", "welcome", "monkey",
        "1234567890", "password1", "qwerty123", "admin123"
    }

    return password.lower() in common_passwords


def validate_password_strength(password: str) -> dict:
    """
    Validate password strength and return detailed feedback.

    Args:
        password: Password to validate

    Returns:
        Dictionary with validation results and feedback
    """
    result = {
        "is_valid": True,
        "score": 0,  # 0-4 scale
        "feedback": [],
        "warnings": []
    }

    # Length check
    if len(password) < 8:
        result["feedback"].append("Password must be at least 8 characters long")
        result["is_valid"] = False
    elif len(password) >= 12:
        result["score"] += 1

    # Character variety checks
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)

    if not has_lower:
        result["feedback"].append("Password must contain at least one lowercase letter")
        result["is_valid"] = False
    else:
        result["score"] += 1

    if not has_upper:
        result["feedback"].append("Password must contain at least one uppercase letter")
        result["is_valid"] = False
    else:
        result["score"] += 1

    if not has_digit:
        result["feedback"].append("Password must contain at least one digit")
        result["is_valid"] = False
    else:
        result["score"] += 1

    if has_special:
        result["score"] += 1
    else:
        result["warnings"].append("Consider adding special characters for better security")

    # Check for compromised passwords
    if is_password_compromised(password):
        result["feedback"].append("This password is commonly used and easily guessed")
        result["is_valid"] = False
        result["score"] = 0

    # Sequential/repeated characters check
    if any(password[i:i+3].isalpha() and password[i:i+3] in 'abcdefghijklmnopqrstuvwxyz' * 3 for i in range(len(password)-2)):
        result["warnings"].append("Avoid sequential letters (e.g., 'abc', 'xyz')")

    if len(set(password)) < len(password) * 0.7:  # High repetition
        result["warnings"].append("Avoid repeated characters")

    # Common patterns
    keyboard_patterns = ['qwerty', 'asdfgh', 'zxcvbn', '123456', 'abcdef']
    if any(pattern in password.lower() for pattern in keyboard_patterns):
        result["warnings"].append("Avoid common keyboard patterns")

    return result


def generate_secure_password(length: int = 12) -> str:
    """
    Generate a secure random password.

    Args:
        length: Desired password length (minimum 8)

    Returns:
        Secure random password string
    """
    import secrets
    import string

    if length < 8:
        length = 8

    # Ensure at least one character from each required category
    password_chars = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(string.punctuation)
    ]

    # Fill remaining length with random characters
    all_chars = string.ascii_letters + string.digits + string.punctuation
    password_chars.extend(secrets.choice(all_chars) for _ in range(length - 4))

    # Shuffle to avoid predictable patterns
    secrets.SystemRandom().shuffle(password_chars)

    return ''.join(password_chars)
