setup:
	cp security/pre-commit-hook.sh .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	@echo "✅ Pre-commit hook installed"

pre-commit: setup

test:
	python3 tests/test_repo_contract.py
