import type React from 'react';
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { ApiError, register } from '../services/authApi';

/**
 * New-user registration.
 *
 * Previously the only way into the app was the login form, so a brand-new user
 * had no way to create an account at all. The backend's `RegistrationRequest`
 * requires `confirm_password` and `privacy_policy_accepted`, which this form
 * mirrors exactly.
 */

/** Backend `PASSWORD_MIN_LENGTH` (app/config/constants.py). */
const PASSWORD_MIN_LENGTH = 12;

export function RegisterPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [privacyAccepted, setPrivacyAccepted] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!privacyAccepted) {
      setError('You must explicitly accept the Privacy Policy to proceed.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (password.length < PASSWORD_MIN_LENGTH) {
      setError(`Password must be at least ${PASSWORD_MIN_LENGTH} characters long.`);
      return;
    }

    setError('');
    setLoading(true);
    try {
      await register({
        username,
        password,
        confirm_password: confirmPassword,
        display_name: displayName,
        // Only send email when provided; the backend field is optional.
        ...(email ? { email } : {}),
        privacy_policy_accepted: true,
      });
      navigate('/login', { state: { registered: true } });
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : 'Something went wrong. Please try again.',
      );
    } finally {
      setLoading(false);
    }
  };

  const inputClass =
    'w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-primary)] px-3 py-2 text-[var(--color-text-primary)] outline-none focus:border-[var(--color-accent)]';
  const labelClass = 'mb-1 block text-sm font-medium text-[var(--color-text-primary)]';

  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-primary)] p-4">
      <div className="w-full max-w-md rounded-xl border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-8 shadow-lg">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">AuthShield Lab</h1>
          <p className="mt-1 text-sm text-[var(--color-text-secondary)]">Create your account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="register-username" className={labelClass}>
              Username
            </label>
            <input
              id="register-username"
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
              minLength={4}
              maxLength={32}
              autoComplete="username"
              className={inputClass}
              autoFocus
            />
          </div>

          <div>
            <label htmlFor="register-display-name" className={labelClass}>
              Display name
            </label>
            <input
              id="register-display-name"
              type="text"
              value={displayName}
              onChange={e => setDisplayName(e.target.value)}
              required
              maxLength={64}
              autoComplete="name"
              className={inputClass}
            />
          </div>

          <div>
            <label htmlFor="register-email" className={labelClass}>
              Email <span className="text-[var(--color-text-muted)]">(optional)</span>
            </label>
            <input
              id="register-email"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              autoComplete="email"
              className={inputClass}
            />
          </div>

          <div>
            <label htmlFor="register-password" className={labelClass}>
              Password
            </label>
            <input
              id="register-password"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              minLength={PASSWORD_MIN_LENGTH}
              autoComplete="new-password"
              className={inputClass}
            />
            <p className="mt-1 text-xs text-[var(--color-text-muted)]">
              At least {PASSWORD_MIN_LENGTH} characters with uppercase, lowercase, a number and a
              symbol.
            </p>
          </div>

          <div>
            <label htmlFor="register-confirm-password" className={labelClass}>
              Confirm password
            </label>
            <input
              id="register-confirm-password"
              type="password"
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
              required
              autoComplete="new-password"
              className={inputClass}
            />
          </div>

          <label className="flex items-start gap-2 text-sm text-[var(--color-text-primary)]">
            <input
              type="checkbox"
              checked={privacyAccepted}
              onChange={e => setPrivacyAccepted(e.target.checked)}
              className="mt-0.5"
            />
            <span>I explicitly accept the Privacy Policy to use AuthShield Lab.</span>
          </label>

          {error && (
            <p role="alert" className="text-sm text-[var(--color-danger)]">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-[var(--color-accent)] px-4 py-2 font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50"
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-[var(--color-text-secondary)]">
          Already have an account?{' '}
          <Link to="/login" className="text-[var(--color-accent)] hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
