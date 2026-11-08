"""Password hashing with multiple algorithm support for educational purposes."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import warnings
from typing import Any

import argon2
import argon2.exceptions
from passlib.context import CryptContext


class PasswordHasher:
    """Multi-algorithm password hasher for AuthShieldLab.

    Supports Argon2id (default/recommended), bcrypt, PBKDF2-HMAC-SHA256,
    and SHA-256 (educational-only, insecure). Each algorithm is wrapped with
    proper salting and constant-time comparison where the backend library
    permits it.

    Example::

        hasher = PasswordHasher()
        hashed = hasher.hash_password("my-secret-password")
        assert hasher.verify_password("my-secret-password", hashed)
    """

    _ARGON2ID = "argon2id"
    _BCRYPT = "bcrypt"
    _PBKDF2 = "pbkdf2_sha256"
    _SHA256 = "sha256"

    _SUPPORTED: frozenset[str] = frozenset({_ARGON2ID, _BCRYPT, _PBKDF2, _SHA256})

    def __init__(
        self,
        argon2_time_cost: int = 3,
        argon2_memory_cost: int = 65536,
        argon2_parallelism: int = 4,
        argon2_hash_len: int = 32,
        argon2_salt_len: int = 16,
        bcrypt_rounds: int = 12,
        pbkdf2_rounds: int = 260_000,
        pbkdf2_salt_len: int = 16,
    ) -> None:
        self._argon2_time_cost = argon2_time_cost
        self._argon2_memory_cost = argon2_memory_cost
        self._argon2_parallelism = argon2_parallelism
        self._argon2_hash_len = argon2_hash_len
        self._argon2_salt_len = argon2_salt_len
        self._bcrypt_rounds = bcrypt_rounds
        self._pbkdf2_rounds = pbkdf2_rounds
        self._pbkdf2_salt_len = pbkdf2_salt_len

        self._argon2_hasher = argon2.PasswordHasher(
            time_cost=self._argon2_time_cost,
            memory_cost=self._argon2_memory_cost,
            parallelism=self._argon2_parallelism,
            hash_len=self._argon2_hash_len,
            salt_len=self._argon2_salt_len,
        )

        self._passlib_context = CryptContext(
            schemes=["bcrypt", "pbkdf2_sha256"],
            deprecated="auto",
            bcrypt__rounds=self._bcrypt_rounds,
            pbkdf2_sha256__rounds=self._pbkdf2_rounds,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def hash_password(
        self, password: str, algorithm: str | None = None
    ) -> str:
        """Hash *password* using the specified algorithm.

        Parameters
        ----------
        password:
            Plaintext password to hash.
        algorithm:
            One of ``argon2id``, ``bcrypt``, ``pbkdf2_sha256``, ``sha256``.
            Defaults to ``argon2id`` when ``None``.

        Returns
        -------
        str
            The hashed password string (includes salt and parameters).

        Raises
        ------
        ValueError
            If the algorithm is not supported.
        """
        algo = (algorithm or self._ARGON2ID).lower()
        if algo not in self._SUPPORTED:
            raise ValueError(
                f"Unsupported algorithm '{algo}'. "
                f"Supported: {', '.join(sorted(self._SUPPORTED))}"
            )

        if algo == self._ARGON2ID:
            return self._hash_argon2id(password)
        if algo == self._BCRYPT:
            return self._hash_bcrypt(password)
        if algo == self._PBKDF2:
            return self._hash_pbkdf2(password)
        return self._hash_sha256(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify *password* against a hash.

        Parameters
        ----------
        password:
            The plaintext password to check.
        hashed:
            The stored hash to verify against.

        Returns
        -------
        bool
            ``True`` if the password matches.
        """
        if not password or not hashed:
            return False

        algo_id = self._detect_algorithm(hashed)

        try:
            if algo_id == self._ARGON2ID:
                return self._verify_argon2id(password, hashed)
            if algo_id == self._BCRYPT:
                return self._passlib_context.verify(password, hashed)
            if algo_id == self._PBKDF2:
                return self._passlib_context.verify(password, hashed)
            if algo_id == self._SHA256:
                return self._verify_sha256(password, hashed)
        except Exception:
            return False

        return False

    def get_algorithm_info(self, algorithm: str) -> dict[str, Any]:
        """Return educational information about the given algorithm.

        Parameters
        ----------
        algorithm:
            Algorithm identifier string.

        Returns
        -------
        dict
            Dictionary with ``name``, ``type``, ``security_level``,
            ``description``, ``recommended``, and algorithm-specific parameters.
        """
        algo = algorithm.lower()
        info: dict[str, Any] = {
            self._ARGON2ID: {
                "name": "Argon2id",
                "type": "Memory-Hard KDF",
                "security_level": "Excellent",
                "recommended": True,
                "description": (
                    "Argon2id is the winner of the Password Hashing Competition. "
                    "It combines Argon2i (side-channel resistant) and Argon2d "
                    "(GPU-resistant) by using both data-dependent and data-independent "
                    "memory access. It is the current gold standard for password hashing."
                ),
                "parameters": {
                    "time_cost": self._argon2_time_cost,
                    "memory_cost_kb": self._argon2_memory_cost,
                    "parallelism": self._argon2_parallelism,
                    "hash_length": self._argon2_hash_len,
                    "salt_length": self._argon2_salt_len,
                },
                "strengths": [
                    "Memory-hard: resists GPU/ASIC brute-force attacks",
                    "Configurable cost factors for future-proofing",
                    "Resistant to side-channel attacks (id variant)",
                    "Winner of the Password Hashing Competition (2015)",
                ],
                "weaknesses": [
                    "Higher memory consumption than simpler algorithms",
                    "Requires native library (argon2-cffi)",
                ],
            },
            self._BCRYPT: {
                "name": "bcrypt",
                "type": "Adaptive Hash Function",
                "security_level": "Good",
                "recommended": True,
                "description": (
                    "bcrypt is a widely-adopted adaptive hashing function based on "
                    "Blowfish. It includes a built-in salt and a configurable work "
                    "factor that can be increased over time."
                ),
                "parameters": {
                    "rounds": self._bcrypt_rounds,
                    "salt_length": 16,
                },
                "strengths": [
                    "Widely supported across languages and frameworks",
                    "Adaptive work factor",
                    "Built-in salt generation",
                ],
                "weaknesses": [
                    "Not memory-hard (vulnerable to GPU attacks at high scale)",
                    "Limited to 72-byte password truncation",
                    "Uses Blowfish key schedule (patent concerns in some jurisdictions, now expired)",
                ],
            },
            self._PBKDF2: {
                "name": "PBKDF2-HMAC-SHA256",
                "type": "Key Derivation Function",
                "security_level": "Adequate",
                "recommended": True,
                "description": (
                    "PBKDF2 applies a pseudorandom function (HMAC) to the password "
                    "along with a salt, and repeats the process many times to produce "
                    "a derived key. Standardized in RFC 2898 / NIST SP 800-132."
                ),
                "parameters": {
                    "iterations": self._pbkdf2_rounds,
                    "salt_length": self._pbkdf2_salt_len,
                    "digest": "SHA-256",
                },
                "strengths": [
                    "NIST-approved standard",
                    "No special dependencies",
                    "Simple to implement correctly",
                ],
                "weaknesses": [
                    "Not memory-hard (GPU-acceleratable)",
                    "High iteration count needed for modern hardware",
                ],
            },
            self._SHA256: {
                "name": "SHA-256 (single round, UNSAFE)",
                "type": "Cryptographic Hash Function",
                "security_level": "CRITICAL – DO NOT USE",
                "recommended": False,
                "description": (
                    "SHA-256 alone is NOT a password hashing algorithm. It is a fast "
                    "cryptographic hash designed for data integrity, not password "
                    "storage. A single GPU can test billions of SHA-256 hashes per "
                    "second. This is included for EDUCATIONAL purposes only to "
                    "demonstrate why purpose-built password hashing algorithms exist."
                ),
                "parameters": {
                    "algorithm": "SHA-256",
                    "salt_length": 16,
                    "iterations": 1,
                },
                "strengths": [
                    "Fast (good for data integrity, BAD for passwords)",
                    "Widely available in standard libraries",
                ],
                "weaknesses": [
                    "Extremely fast: billions of guesses/second on modern GPUs",
                    "No key stretching",
                    "No memory hardness",
                    "Virtually every weak password cracked instantly",
                    "EDUCATIONAL USE ONLY – never deploy in production",
                ],
            },
        }.get(algo)

        if info is None:
            raise ValueError(
                f"Unknown algorithm '{algorithm}'. "
                f"Supported: {', '.join(sorted(self._SUPPORTED))}"
            )
        return info

    @staticmethod
    def get_recommended_algorithm() -> str:
        """Return the recommended algorithm name."""
        return "argon2id"

    @staticmethod
    def supported_algorithms() -> list[str]:
        """Return list of supported algorithm identifiers."""
        return sorted(PasswordHasher._SUPPORTED)

    # ------------------------------------------------------------------
    # Internal hashing methods
    # ------------------------------------------------------------------

    def _hash_argon2id(self, password: str) -> str:
        return self._argon2_hasher.hash(password)

    def _hash_bcrypt(self, password: str) -> str:
        return self._passlib_context.hash(password)

    def _hash_pbkdf2(self, password: str) -> str:
        return self._passlib_context.hash(password)

    def _hash_sha256(self, password: str) -> str:
        warnings.warn(
            "SHA-256 is NOT a password hashing algorithm. This hash is generated "
            "for EDUCATIONAL demonstration only. Never use SHA-256 (or any fast "
            "hash) for password storage in production.",
            UserWarning,
            stacklevel=2,
        )
        salt = os.urandom(32)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 1)
        salt_hex = salt.hex()
        hash_hex = dk.hex()
        return f"$sha256$${salt_hex}${hash_hex}"

    # ------------------------------------------------------------------
    # Internal verification methods
    # ------------------------------------------------------------------

    def _verify_argon2id(self, password: str, hashed: str) -> bool:
        try:
            self._argon2_hasher.verify(hashed, password)
            return True
        except argon2.exceptions.VerifyMismatchError:
            return False
        except argon2.exceptions.InvalidHashError:
            return False
        except Exception:
            return False

    @staticmethod
    def _verify_sha256(password: str, hashed: str) -> bool:
        """Verify a SHA-256 hash (insecure, educational only)."""
        parts = hashed.split("$")
        if len(parts) != 5 or parts[1] != "sha256":
            return False
        salt_hex = parts[3]
        stored_hash_hex = parts[4]
        salt = bytes.fromhex(salt_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 1)
        return hmac.compare_digest(dk.hex(), stored_hash_hex)

    @staticmethod
    def _detect_algorithm(hashed: str) -> str | None:
        """Detect which algorithm produced a given hash."""
        if hashed.startswith("$argon2"):
            return "argon2id"
        if hashed.startswith("$2b$") or hashed.startswith("$2a$"):
            return "bcrypt"
        if hashed.startswith("$pbkdf2"):
            return "pbkdf2_sha256"
        if hashed.startswith("$sha256$$"):
            return "sha256"
        return None
