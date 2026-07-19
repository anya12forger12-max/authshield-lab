# Data Security — AuthShield Lab

> Version 2.0 · Classification: INTERNAL · Last Updated: 2026-07-19

## 1. Overview

AuthShield Lab implements defense-in-depth data security for a localhost-only
educational platform. Security measures cover encryption at rest, credential
protection, key management, integrity verification, and access control.

### 1.1 Security Principles

| Principle | Description |
|---|---|
| Defense in depth | Multiple layers of security controls |
| Least privilege | Minimum necessary access for each component |
| Secure by default | Encryption enabled, strong defaults |
| Zero trust | Verify everything, trust nothing |
| Privacy by design | Data minimization, purpose limitation |

---

## 2. Encryption at Rest

### 2.1 SQLCipher Configuration

AuthShield Lab uses SQLCipher 4.x for transparent database encryption:

```python
class DatabaseEncryption:
    """SQLCipher encryption configuration."""

    SQLCIPHER_CONFIG = {
        # Encryption algorithm: AES-256-CBC
        "cipher_algorithm": "AES-256-CBC",

        # Key derivation: PBKDF2-HMAC-SHA512
        "kdf_algorithm": "PBKDF2-HMAC-SHA512",
        "kdf_iterations": 256000,
        "kdf_salt": "authshield-salt-v2",

        # Page-level encryption
        "cipher_page_size": 4096,
        "cipher_hmac_algorithm": "HMAC-SHA512",
        "cipher_kdf_algorithm": "PBKDF2-HMAC-SHA512",

        # Security settings
        "cipher_plaintext_header_size": 0,
        "cipher_use_hmac": 1,
        "cipher_plaintext_footer_size": 0,
    }

    async def configure_encryption(self, engine):
        """Configure SQLCipher encryption on engine."""
        async with engine.begin() as conn:
            for key, value in self.SQLCIPHER_CONFIG.items():
                await conn.execute(text(f"PRAGMA {key} = {value}"))

    def derive_key(self, master_password: str) -> bytes:
        """Derive encryption key from master password."""
        import hashlib
        import os

        salt = self.SQLCIPHER_CONFIG["kdf_salt"].encode()
        iterations = self.SQLCIPHER_CONFIG["kdf_iterations"]

        key = hashlib.pbkdf2_hmac(
            "sha512",
            master_password.encode(),
            salt,
            iterations,
            dklen=32,  # 256 bits
        )

        return key
```

### 2.2 Field-Level Encryption

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class FieldEncryption:
    """Encrypts sensitive fields before storage."""

    def __init__(self, key: bytes):
        self.fernet = Fernet(base64.urlsafe_b64encode(key[:32]))

    @classmethod
    def from_master_key(cls, master_key: str) -> "FieldEncryption":
        """Create from master key string."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"authshield-field-encryption-salt",
            iterations=480000,
        )
        key = kdf.derive(master_key.encode())
        return cls(key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string value."""
        return self.fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt an encrypted string value."""
        return self.fernet.decrypt(ciphertext.encode()).decode()

    def encrypt_dict(self, data: dict, fields: list[str]) -> dict:
        """Encrypt specific fields in a dictionary."""
        encrypted = data.copy()
        for field in fields:
            if field in encrypted and encrypted[field] is not None:
                encrypted[field] = self.encrypt(str(encrypted[field]))
        return encrypted

    def decrypt_dict(self, data: dict, fields: list[str]) -> dict:
        """Decrypt specific fields in a dictionary."""
        decrypted = data.copy()
        for field in fields:
            if field in decrypted and decrypted[field] is not None:
                decrypted[field] = self.decrypt(decrypted[field])
        return decrypted


# Encrypted fields per entity type
ENCRYPTED_FIELDS = {
    "users": ["password_hash", "mfa_secret", "email"],
    "configurations": ["config_value"],  # When is_sensitive = True
    "credentials": ["secret", "token"],
    "mfa_factors": ["secret_encrypted", "backup_codes_hash"],
    "backup_records": ["encryption_key_hint"],
}
```

---

## 3. Credential Protection

### 3.1 Password Hashing (Argon2id)

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

class CredentialManager:
    """Manages password hashing and verification."""

    # Argon2id parameters
    ARGON2_CONFIG = {
        "time_cost": 3,        # Number of iterations
        "memory_cost": 65536,  # 64 MB
        "parallelism": 4,      # Number of threads
        "hash_len": 32,        # Hash length in bytes
        "salt_len": 16,        # Salt length in bytes
    }

    def __init__(self):
        self.hasher = PasswordHasher(
            time_cost=self.ARGON2_CONFIG["time_cost"],
            memory_cost=self.ARGON2_CONFIG["memory_cost"],
            parallelism=self.ARGON2_CONFIG["parallelism"],
            hash_len=self.ARGON2_CONFIG["hash_len"],
            salt_len=self.ARGON2_CONFIG["salt_len"],
        )

    def hash_password(self, password: str) -> str:
        """Hash a password using Argon2id."""
        return self.hasher.hash(password)

    def verify_password(self, password: str, hash: str) -> bool:
        """Verify a password against its hash."""
        try:
            return self.hasher.verify(hash, password)
        except (VerifyMismatchError, InvalidHashError):
            return False

    def needs_rehash(self, hash: str) -> bool:
        """Check if hash needs to be updated (parameter changes)."""
        return self.hasher.check_needs_rehash(hash)

    def generate_salt(self) -> bytes:
        """Generate a cryptographically secure salt."""
        import os
        return os.urandom(self.ARGON2_CONFIG["salt_len"])
```

### 3.2 Bcrypt Fallback

```python
import bcrypt

class BcryptHasher:
    """Bcrypt password hashing (legacy compatibility)."""

    ROUNDS = 12

    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt."""
        salt = bcrypt.gensalt(rounds=self.ROUNDS)
        return bcrypt.hashpw(password.encode(), salt).decode()

    def verify_password(self, password: str, hash: str) -> bool:
        """Verify password against bcrypt hash."""
        return bcrypt.checkpw(password.encode(), hash.encode())
```

### 3.3 PBKDF2 (API Keys)

```python
import hashlib
import os

class APIKeyHasher:
    """PBKDF2-based hashing for API keys and tokens."""

    ITERATIONS = 480000
    HASH_LEN = 64

    def hash_key(self, key: str) -> str:
        """Hash an API key with PBKDF2-SHA512."""
        salt = os.urandom(32)
        dk = hashlib.pbkdf2_hmac(
            "sha512",
            key.encode(),
            salt,
            self.ITERATIONS,
            dklen=self.HASH_LEN,
        )
        return f"{salt.hex()}${dk.hex()}"

    def verify_key(self, key: str, stored_hash: str) -> bool:
        """Verify API key against stored hash."""
        salt_hex, hash_hex = stored_hash.split("$")
        salt = bytes.fromhex(salt_hex)

        dk = hashlib.pbkdf2_hmac(
            "sha512",
            key.encode(),
            salt,
            self.ITERATIONS,
            dklen=self.HASH_LEN,
        )

        return dk.hex() == hash_hex
```

### 3.4 Token Generation

```python
import secrets

class TokenGenerator:
    """Generates cryptographically secure tokens."""

    @staticmethod
    def generate_session_token(length: int = 64) -> str:
        """Generate a secure session token."""
        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_api_key(prefix: str = "ash") -> str:
        """Generate an API key with prefix."""
        key = secrets.token_urlsafe(48)
        return f"{prefix}_{key}"

    @staticmethod
    def generate_backup_code() -> str:
        """Generate a single backup code."""
        return secrets.token_hex(4).upper()

    @staticmethod
    def generate_idempotency_key() -> str:
        """Generate an idempotency key."""
        return str(uuid.uuid4())
```

---

## 4. Key Management

### 4.1 Local Key Derivation

```python
class KeyManager:
    """Manages encryption keys locally."""

    KEY_FILE = "master.key"
    KEY_DERIVATION_SALT = b"authshield-key-derivation-v2"

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.key_path = config_dir / self.KEY_FILE

    def get_or_create_master_key(self) -> bytes:
        """Get existing master key or create new one."""
        if self.key_path.exists():
            return self.key_path.read_bytes()

        # Generate new master key
        key = secrets.token_bytes(32)
        self.key_path.write_bytes(key)

        # Set restrictive permissions
        os.chmod(self.key_path, 0o600)

        return key

    def derive_database_key(self, master_key: bytes) -> bytes:
        """Derive database encryption key from master key."""
        return hashlib.pbkdf2_hmac(
            "sha512",
            master_key,
            self.KEY_DERIVATION_SALT + b"-database",
            iterations=256000,
            dklen=32,
        )

    def derive_field_key(self, master_key: bytes) -> bytes:
        """Derive field encryption key from master key."""
        return hashlib.pbkdf2_hmac(
            "sha512",
            master_key,
            self.KEY_DERIVATION_SALT + b"-fields",
            iterations=256000,
            dklen=32,
        )

    def derive_backup_key(self, master_key: bytes) -> bytes:
        """Derive backup encryption key from master key."""
        return hashlib.pbkdf2_hmac(
            "sha512",
            master_key,
            self.KEY_DERIVATION_SALT + b"-backup",
            iterations=256000,
            dklen=32,
        )
```

### 4.2 Key Rotation

```python
class KeyRotator:
    """Manages encryption key rotation."""

    async def rotate_master_key(
        self,
        old_key: bytes,
        key_manager: KeyManager,
        database_manager: DatabaseEncryption,
    ) -> bytes:
        """Rotate the master encryption key."""
        # 1. Generate new master key
        new_key = secrets.token_bytes(32)

        # 2. Re-derive all sub-keys
        new_db_key = key_manager.derive_database_key(new_key)
        new_field_key = key_manager.derive_field_key(new_key)

        # 3. Re-encrypt database with new key
        await database_manager.re_encrypt_database(old_key, new_db_key)

        # 4. Re-encrypt sensitive fields
        await self._re_encrypt_fields(old_key, new_field_key)

        # 5. Save new master key
        key_manager.key_path.write_bytes(new_key)
        os.chmod(key_manager.key_path, 0o600)

        # 6. Archive old key (encrypted with new key)
        await self._archive_old_key(old_key, new_key)

        # 7. Audit the rotation
        await self._audit_key_rotation()

        return new_key

    async def _archive_old_key(self, old_key: bytes, new_key: bytes):
        """Archive old key encrypted with new key."""
        key_manager = KeyManager(self.config_dir)
        field_encryption = FieldEncryption.from_master_key(
            new_key.hex()
        )

        encrypted_old = field_encryption.encrypt(old_key.hex())
        archive_path = self.config_dir / f"key_archive_{datetime.utcnow().strftime('%Y%m%d')}.enc"
        archive_path.write_text(encrypted_old)
        os.chmod(archive_path, 0o600)
```

---

## 5. Sensitive Field Protection

### 5.1 Field Classification

```python
class SensitiveFieldClassifier:
    """Classifies fields by sensitivity level."""

    CLASSIFICATIONS = {
        "SECRET": [
            "password_hash", "mfa_secret", "encryption_key",
            "api_key", "token", "backup_codes",
        ],
        "RESTRICTED": [
            "email", "display_name", "ip_address",
            "student_id", "grades", "scores",
        ],
        "CONFIDENTIAL": [
            "config_value", "settings", "metadata",
            "user_agent", "session_token",
        ],
        "INTERNAL": [
            "description", "notes", "tags",
            "locale", "timezone", "status",
        ],
    }

    @classmethod
    def classify(cls, field_name: str) -> str:
        """Get classification for a field."""
        for level, fields in cls.CLASSIFICATIONS.items():
            if field_name in fields:
                return level
        return "INTERNAL"

    @classmethod
    def get_encrypted_fields(cls) -> list[str]:
        """Get all fields that require encryption."""
        return cls.CLASSIFICATIONS["SECRET"] + cls.CLASSIFICATIONS["RESTRICTED"]
```

### 5.2 Encryption Rules

```python
ENCRYPTION_RULES = {
    "users": {
        "encrypt": ["password_hash", "mfa_secret"],
        "hash": ["email"],  # Hashed for search, encrypted for storage
    },
    "configurations": {
        "encrypt_if": {"column": "is_sensitive", "value": True},
        "encrypt": ["config_value"],
    },
    "credentials": {
        "encrypt": ["secret", "token", "refresh_token"],
    },
    "mfa_factors": {
        "encrypt": ["secret_encrypted", "backup_codes_hash"],
    },
    "audit_entries": {
        "no_encrypt": True,  # Audit entries are stored separately
    },
}
```

---

## 6. Integrity Checks

### 6.1 Checksum Computation

```python
import hashlib

class IntegrityManager:
    """Manages data integrity checks."""

    @staticmethod
    def compute_row_checksum(row: dict) -> str:
        """Compute SHA-256 checksum for a data row."""
        data = json.dumps(row, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def compute_file_checksum(file_path: Path) -> str:
        """Compute SHA-256 checksum for a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def verify_checksum(data: Any, expected_checksum: str) -> bool:
        """Verify data integrity against expected checksum."""
        if isinstance(data, (dict, list)):
            data = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
        elif isinstance(data, str):
            data = data.encode("utf-8")

        actual = hashlib.sha256(data).hexdigest()
        return actual == expected_checksum

    @staticmethod
    def compute_certificate_signature(cert_data: dict, private_key: bytes) -> str:
        """Compute cryptographic signature for certificate."""
        import hmac

        data = json.dumps(cert_data, sort_keys=True).encode()
        signature = hmac.new(private_key, data, hashlib.sha256).hexdigest()
        return signature

    @staticmethod
    def verify_certificate_signature(
        cert_data: dict,
        signature: str,
        public_key: bytes,
    ) -> bool:
        """Verify certificate signature."""
        import hmac

        data = json.dumps(cert_data, sort_keys=True).encode()
        expected = hmac.new(public_key, data, hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected)
```

### 6.2 Hash Chain Verification

```python
class HashChainVerifier:
    """Verifies hash chain integrity for audit logs."""

    def compute_chain_hash(
        self,
        entry_data: dict,
        previous_hash: Optional[str],
    ) -> str:
        """Compute hash for chain entry."""
        chain_data = json.dumps(
            {**entry_data, "previous_hash": previous_hash},
            sort_keys=True,
        ).encode()
        return hashlib.sha256(chain_data).hexdigest()

    def verify_chain(
        self,
        entries: list[dict],
    ) -> ChainVerificationResult:
        """Verify complete hash chain."""
        previous_hash = None

        for idx, entry in enumerate(entries):
            # Verify previous hash link
            if entry["previous_hash"] != previous_hash:
                return ChainVerificationResult(
                    status="broken",
                    broken_at_index=idx,
                    message=f"Chain link broken at entry {idx}",
                )

            # Verify entry hash
            expected = self.compute_chain_hash(entry, previous_hash)
            if entry["entry_hash"] != expected:
                return ChainVerificationResult(
                    status="broken",
                    broken_at_index=idx,
                    message=f"Entry hash mismatch at index {idx}",
                )

            previous_hash = entry["entry_hash"]

        return ChainVerificationResult(
            status="valid",
            entries_verified=len(entries),
        )
```

---

## 7. Access Control

### 7.1 Module-Level Access Control

```python
class DataAccessController:
    """Controls data access at module level."""

    # Module → required permissions for data access
    MODULE_ACCESS = {
        "identity": {
            "read": ["user.read", "identity.read"],
            "write": ["user.write", "identity.write"],
            "admin": ["user.admin", "identity.admin"],
        },
        "authorization": {
            "read": ["role.read", "permission.read"],
            "write": ["role.write", "permission.write"],
            "admin": ["role.admin", "permission.admin"],
        },
        "learning": {
            "read": ["course.read", "lesson.read"],
            "write": ["course.write", "lesson.write"],
            "admin": ["course.admin"],
        },
        "assessment": {
            "read": ["assessment.read"],
            "write": ["assessment.write"],
            "admin": ["assessment.admin"],
        },
        "audit": {
            "read": ["audit.read"],
            "write": ["audit.write"],  # Append-only
            "admin": ["audit.admin"],
        },
        "configuration": {
            "read": ["config.read"],
            "write": ["config.write"],
            "admin": ["config.admin"],
        },
    }

    def check_access(
        self,
        user_permissions: list[str],
        module: str,
        operation: str,
    ) -> bool:
        """Check if user has access to module data."""
        required = self.MODULE_ACCESS.get(module, {}).get(operation, [])
        return any(perm in user_permissions for perm in required)
```

### 7.2 Row-Level Access Control

```python
class RowLevelAccess:
    """Row-level access control for multi-tenant data."""

    def __init__(self, user_id: UUID, user_org_id: Optional[UUID] = None):
        self.user_id = user_id
        self.user_org_id = user_org_id

    def get_user_filter(self) -> FilterSpecification:
        """Get filter for user's own data."""
        return FilterSpecification("user_id", "eq", self.user_id)

    def get_org_filter(self) -> FilterSpecification:
        """Get filter for user's organization data."""
        if self.user_org_id:
            return FilterSpecification("organization_id", "eq", self.user_org_id)
        return FilterSpecification("user_id", "eq", self.user_id)

    def apply_access_control(
        self,
        query: Select,
        entity_type: str,
    ) -> Select:
        """Apply row-level access control to query."""
        if entity_type in ("users", "sessions", "notifications"):
            return query.where(self.get_user_filter().to_clause())
        elif entity_type in ("courses", "enrollments"):
            return query.where(self.get_org_filter().to_clause())
        return query  # No restriction
```

---

## 8. Access Auditing

### 8.1 Data Access Logging

```python
class DataAccessAuditor:
    """Logs all data access operations."""

    async def log_access(
        self,
        user_id: UUID,
        entity_type: str,
        entity_id: Optional[UUID],
        operation: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """Log a data access event."""
        entry = AuditEntry(
            action=f"data.{operation}",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=json.dumps({
                "access_type": "data_read" if operation == "read" else "data_write",
                "timestamp": datetime.utcnow().isoformat(),
            }),
        )

        await self.audit_writer.write(entry)

    async def log_sensitive_access(
        self,
        user_id: UUID,
        entity_type: str,
        entity_id: UUID,
        fields_accessed: list[str],
        purpose: str,
    ):
        """Log access to sensitive fields."""
        entry = AuditEntry(
            action="data.sensitive_access",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            metadata=json.dumps({
                "fields": fields_accessed,
                "purpose": purpose,
                "timestamp": datetime.utcnow().isoformat(),
            }),
        )

        await self.audit_writer.write(entry)
```

---

## 9. Privacy Controls

### 9.1 Data Minimization

```python
class DataMinimizer:
    """Implements data minimization principles."""

    MINIMIZATION_RULES = {
        "audit_entries": {
            "exclude_fields": ["old_value", "new_value"],  # Exclude diffs from default queries
            "anonymize_if": {"purpose": "analytics"},
        },
        "sessions": {
            "exclude_fields": ["user_agent", "ip_address"],  # Exclude from list views
            "retain_days": 90,
        },
        "notifications": {
            "retain_days": 90,
            "anonymize_after_days": 30,
        },
        "learning_sessions": {
            "exclude_fields": ["time_logs"],  # Exclude granular time data
            "aggregate_after_days": 365,
        },
    }

    def minimize_response(
        self,
        data: dict,
        entity_type: str,
        purpose: str = "default",
    ) -> dict:
        """Apply data minimization to response data."""
        rules = self.MINIMIZATION_RULES.get(entity_type, {})

        minimized = data.copy()

        # Exclude fields
        exclude = rules.get("exclude_fields", [])
        for field in exclude:
            minimized.pop(field, None)

        # Anonymize if needed
        anonymize_if = rules.get("anonymize_if", {})
        if anonymize_if.get("purpose") == purpose:
            minimized = self._anonymize(minimized)

        return minimized

    def _anonymize(self, data: dict) -> dict:
        """Anonymize PII fields."""
        import hashlib

        pii_fields = ["email", "display_name", "ip_address"]
        anonymized = data.copy()

        for field in pii_fields:
            if field in anonymized and anonymized[field]:
                hash_val = hashlib.sha256(
                    str(anonymized[field]).encode()
                ).hexdigest()[:8]
                anonymized[field] = f"anon_{hash_val}"

        return anonymized
```

### 9.2 Purpose Limitation

```python
class PurposeLimitation:
    """Enforces data purpose limitation."""

    PURPOSES = {
        "authentication": ["users.email", "users.password_hash", "sessions"],
        "authorization": ["users.id", "roles", "permissions"],
        "learning": ["courses", "lessons", "progress", "enrollments"],
        "assessment": ["assessments", "questions", "attempts", "results"],
        "analytics": ["progress", "enrollments", "results"],  # Aggregated only
        "audit": ["audit_entries"],  # Full access for security
        "support": ["users.email", "users.display_name"],  # Minimal for support
    }

    def get_accessible_entities(self, purpose: str) -> list[str]:
        """Get entities accessible for a given purpose."""
        return self.PURPOSES.get(purpose, [])

    def check_purpose(self, entity_type: str, purpose: str) -> bool:
        """Check if entity is accessible for the purpose."""
        accessible = self.get_accessible_entities(purpose)
        return entity_type in accessible
```

---

## 10. Secure Defaults

### 10.1 Default Security Configuration

```python
SECURE_DEFAULTS = {
    "database": {
        "encryption_enabled": True,
        "sqlcipher": True,
        "foreign_keys": True,
        "secure_delete": False,  # Set True for sensitive tables
        "wal_mode": True,
        "synchronous": "NORMAL",
    },
    "authentication": {
        "password_min_length": 12,
        "password_require_uppercase": True,
        "password_require_lowercase": True,
        "password_require_digit": True,
        "password_require_special": True,
        "max_login_attempts": 5,
        "lockout_duration_minutes": 30,
        "session_timeout_hours": 24,
        "mfa_encouraged": True,
    },
    "api": {
        "rate_limit_per_minute": 60,
        "rate_limit_per_hour": 1000,
        "cors_origins": ["http://localhost:*"],
        "helmet_enabled": True,
    },
    "backup": {
        "encryption_enabled": True,
        "compression_enabled": True,
        "integrity_check": True,
        "retention_days": 365,
    },
    "audit": {
        "enabled": True,
        "async_writes": True,
        "hash_chain": True,
        "retention_years": 7,
    },
}
```

### 10.2 Security Headers

```python
SECURITY_HEADERS = {
    "Content-Security-Policy": "default-src 'self'",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}
```

---

*This document defines the complete data security architecture for AuthShield Lab.*
