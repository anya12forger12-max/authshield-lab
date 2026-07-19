# Support — AuthShield Lab

This page describes the available support channels for AuthShield Lab.

---

## Documentation

The first resource for help is the project documentation:

| Document | Description |
|----------|-------------|
| [README](README.md) | Project overview and quick start |
| [Developer Onboarding](docs/development/ONBOARDING.md) | Setup and getting started guide |
| [Contributing Guide](CONTRIBUTING.md) | How to contribute |
| [Changelog](CHANGELOG.md) | Release history and changes |
| [Roadmap](ROADMAP.md) | Project direction and milestones |
| [Accessibility Statement](ACCESSIBILITY.md) | Accessibility features and compliance |
| [Security Policy](SECURITY.md) | Security practices and vulnerability reporting |

---

## GitHub Issues

For bug reports, feature requests, and specific technical problems:

- **Bug Reports**: [Open a bug report](https://github.com/anya12forger12-max/authshield-lab/issues/new?template=bug_report.md)
- **Feature Requests**: [Request a feature](https://github.com/anya12forger12-max/authshield-lab/issues/new?template=feature_request.md)
- **Browse All Issues**: [View open issues](https://github.com/anya12forger12-max/authshield-lab/issues)

When filing an issue, please include:
- Your environment (OS, browser, Node.js version)
- Steps to reproduce the problem
- Expected vs. actual behavior
- Screenshots or error logs if applicable

---

## GitHub Discussions

For questions, ideas, and community conversation:

- **General Questions**: [Discussions](https://github.com/anya12forger12-max/authshield-lab/discussions)
- **Ideas & Feature Proposals**: Use the `Ideas` category
- **Show and Tell**: Share what you have built with AuthShield Lab
- **Q&A**: Ask and answer community questions

Discussions are the preferred channel for:
- How-to questions
- Architecture decisions
- Roadmap proposals
- Community showcases

---

## Email Support

| Contact | Email | Response Time |
|---------|-------|---------------|
| General Support | support@authshieldlab.dev | 3-5 business days |
| Security Vulnerabilities | security@authshieldlab.dev | 24 hours |
| Accessibility Feedback | accessibility@authshieldlab.dev | 48 hours |
| Code of Conduct Issues | conduct@authshieldlab.dev | 48 hours |

**Note**: For security vulnerabilities, please follow the process described in [SECURITY.md](SECURITY.md) and do not use the general support email.

---

## Frequently Asked Questions

### General

**Q: Is AuthShield Lab free to use?**
A: Yes. AuthShield Lab is open-source under the MIT License. You can use, modify, and distribute it freely.

**Q: Does AuthShield Lab require internet access?**
A: No. AuthShield Lab is designed to work fully offline. No external API calls or cloud services are required.

**Q: What browsers are supported?**
A: Chrome 100+, Firefox 100+, Safari 16+, and Edge 100+. See the [Accessibility Statement](ACCESSIBILITY.md) for full details.

### Installation

**Q: What Node.js version do I need?**
A: Node.js v20.0 or later is required.

**Q: Can I use Docker instead of installing locally?**
A: Yes. Run `docker compose up --build` to start the platform in containers.

**Q: How do I update to the latest version?**
A: Pull the latest changes (`git pull`) and run `npm install` to update dependencies.

### Development

**Q: How do I run the tests?**
A: Run `npm test` for unit tests, `npm run test:a11y` for accessibility tests, or `npm run test:coverage` for a full coverage report.

**Q: How do I run the linter?**
A: Run `npm run lint` to check for issues, or `npm run lint:fix` to auto-fix them.

**Q: What is the code style?**
A: We use Prettier for formatting and ESLint for code quality. See the [Contributing Guide](CONTRIBUTING.md) for details.

### Security

**Q: Is it safe to run attack simulations?**
A: Yes. All simulations run in a sandboxed environment on your local machine. No external requests are made. See [SECURITY.md](SECURITY.md) for details.

**Q: How do I report a security vulnerability?**
A: Email security@authshieldlab.dev. Do not open a public GitHub Issue. See [SECURITY.md](SECURITY.md) for the full process.

### Accessibility

**Q: Is AuthShield Lab accessible?**
A: Yes. We are committed to WCAG 2.2 AA compliance. See [ACCESSIBILITY.md](ACCESSIBILITY.md) for details and known limitations.

**Q: I found an accessibility issue. How do I report it?**
A: Open a GitHub Issue with the `accessibility` label or email accessibility@authshieldlab.dev.

---

## Community

- **GitHub Discussions**: [Community forum](https://github.com/anya12forger12-max/authshield-lab/discussions)
- **Contributing**: [Contributing Guide](CONTRIBUTING.md)
- **Code of Conduct**: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

---

## Response Expectations

| Channel | Expected Response Time |
|---------|----------------------|
| GitHub Issues | 3-5 business days |
| GitHub Discussions | 3-7 business days |
| Security Reports | 24 hours |
| Accessibility Feedback | 48 hours |
| General Email | 3-5 business days |

**Note**: AuthShield Lab is maintained by a community of volunteers. Response times may vary based on contributor availability. We appreciate your patience.

---

*If you have suggestions for improving this support page, please [open an issue](https://github.com/anya12forger12-max/authshield-lab/issues).*
