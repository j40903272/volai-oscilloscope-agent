.PHONY: help install test lint format clean run-server run-agent

help:
	@echo "Oscilloscope Control System - Available Commands:"
	@echo ""
	@echo "  make install          Install all dependencies (Claude + HuggingFace)"
	@echo "  make install-claude   Install Claude dependencies only (faster, smaller)"
	@echo "  make install-hf       Install HuggingFace dependencies (for local models)"
	@echo "  make test             Run tests"
	@echo "  make lint             Run linter (ruff)"
	@echo "  make format           Format code (black)"
	@echo "  make clean            Clean temporary files"
	@echo "  make run-server       Start MCP server"
	@echo "  make test-mcp         Test MCP server functionality"
	@echo "  make run-agent        Run natural language agent"
	@echo "  make run-agent-offline Run agent in demo mode (no scope needed)"
	@echo "  make check-device     Check oscilloscope connection"
	@echo "  make test-measure     Test direct measurement on channel 1"
	@echo "  make test-voltage     Quick voltage test (simpler)"
	@echo "  make test-screen      Test screen capture (fast method)"
	@echo "  make run-web          Launch web interface (Streamlit)"
	@echo ""

install:
	@echo "Installing all dependencies (Claude + HuggingFace)..."
	python3 -m pip install -r requirements.txt
	python3 -m pip install -r requirements-huggingface.txt
	python3 -m pip install -e .
	@echo "✅ Full installation complete!"

install-claude:
	@echo "Installing Claude dependencies only (lighter, faster)..."
	python3 -m pip install -r requirements.txt
	python3 -m pip install -e .
	@echo "✅ Claude installation complete!"
	@echo "💡 To add HuggingFace later: make install-hf"

install-hf:
	@echo "Installing HuggingFace dependencies..."
	python3 -m pip install -r requirements-huggingface.txt
	@echo "✅ HuggingFace dependencies installed!"

test:
	pytest tests/ -v

lint:
	ruff check src/ examples/ tests/

format:
	black src/ examples/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -f *.log

run-server:
	@echo "Starting MCP Server..."
	@echo "Press Ctrl+C to stop"
	@echo ""
	python3 -m src.mcp_server.server

test-mcp:
	@echo "Testing MCP Server (will connect to oscilloscope)..."
	python3 examples/mcp_client.py

run-agent:
	python3 examples/agent_demo.py --interactive

run-agent-offline:
	python3 examples/agent_demo_offline.py

check-device:
	python3 check_oscilloscope.py

test-measure:
	python3 test_measure.py

test-voltage:
	python3 test_voltage_simple.py

test-screen:
	@echo "Testing fast screen capture..."
	python3 test_screen_capture.py

run-web:
	streamlit run app.py

setup-env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file. Please edit it with your settings."; \
	else \
		echo ".env file already exists"; \
	fi

