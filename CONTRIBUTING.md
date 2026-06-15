# Contributing to VEX

VEX is a free, MIT-licensed agent harness system. We welcome contributions to core tools, skills, rules, and the marketplace.

## Development Workflow

1. Fork the repository.
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/vex.git`
3. Install dependencies: `npm install && pip install -e .`
4. Create a branch: `git checkout -b feat/your-feature`
5. Follow the [Development Workflow](rules/common/development-workflow.md) (Plan -> TDD -> Code Review).

## Testing

All code changes must be accompanied by tests. We use Python `unittest` to minimize external dependencies.

Run the test suite:
```bash
npm run test
# OR
python -m unittest discover -s tests
```

## Adding Skills to the Marketplace

1. Create your skill in the `skills/` directory under the appropriate category.
2. Ensure your skill has a valid `manifest.json`.
3. Use the installer CLI to prepare it: `python marketplace/installer.py publish skills/category/your-skill`
4. Submit a Pull Request.

## Rules and Guidelines

- Keep code simple and immutable where possible.
- Avoid external dependencies unless absolutely necessary.
- Security is paramount. Do not execute untrusted code without validation.
- See `CLAUDE.md` and the `rules/` directory for detailed architecture and style guidelines.
