# RL Trading Bot
## Deep Reinforcement Learning that trades like a pro

Build, train, and evaluate a trading agent powered by Proximal Policy Optimization (PPO).

Features:
- Reinforcement Learning application with a modern PPO pipeline.
- Clean architecture with dependency injection, modular environments, and reusable policies.
- Command-line UX for reproducible experiments and fast iteration.
- Hardware-aware PyTorch models that scale from CPU to GPU seamlessly.

---

## What it does

- Downloads market candlestick data for any symbol/interval you choose.
- Trains a PPO-based trading agent on multi-timescale price action and state features.
- Encodes technical context via 1D convolutions across higher and lower timeframes.
- Learns trading behavior with actor-critic PPO and evaluates performance over long horizons.

The result: a data-driven, repeatable RL workflow that can be extended to new markets, policies, and evaluation 
strategies.

---

## Architecture At A Glance

- Data layer
  - Fetch and persist candlestick data using a clean repository/persistence boundary.
  - Fully configurable intervals and lookbacks for realistic multi-resolution signals.

- RL core
  - PPO policy with shared feature extractor:
    - Parallel 1D CNN feature stacks for higher and lower timeframe OHLC data.
    - Additional portfolio/episode state features baked into the model’s shared torso.
    - Actor (action probabilities) + Critic (state value) heads for stable PPO training.

- Training loop
  - Reproducible runs via UUID-based policy IDs.
  - Configurable episodes, timesteps, and observation windows.
  - Device-aware tensors automatically leverage GPU if available.

- CLI-driven workflow
  - Explicit “download” vs “train” modes.
  - Typed, discoverable options with sensible defaults for fast prototyping.

---

## Quickstart

Requirements:
- Python 3.11.9
- Virtual environment (virtualenv)
- Dependencies from requirements.txt

Setup:
1) Create and activate a virtualenv
2) Install dependencies
3) Run the CLI

Example:
```bash
# 1) Create & activate venv
python3 -m venv .venv source .venv/bin/activate  # Windows: .venv\Scripts\activate
# 2) Install deps & change to project root
pip install -r requirements.txt
cd src
# 3) Download candlestick data
python -m trading_bot --download
--base-asset BTC
--quote-asset USDT
--interval 1h
# 4) Train PPO trading agent
python -m trading_bot --train
--base-asset BTC --quote-asset USDT
--lower-interval 5m
--higher-interval 1h
--lower-interval-lookback-candles 96
--higher-interval-lookback-candles 120
--episodes 10000
--max-time-steps 864
```

Tip: Provide a specific PPO policy ID to reproduce runs across machines/seeds. 
If not provided, the system generates one automatically.

---

## Key capabilities

- Multi-resolution market understanding
  - Model “sees” both lower and higher timeframe structures through dedicated CNN branches.

- Rich state representation
  - The agent reasons over position status, unrealized PnL, drawdowns, episode age, action patience, and recent win 
  ratios—features engineered for practical trading behavior.

- Reproducibility and portability
  - Deterministic configuration via CLI and policy IDs.
  - Persistence interfaces for loading/saving trained policies.

- Extensibility
  - Swap data sources or storage backends by implementing the provided interfaces.
  - Plug in new reward functions, action spaces, or environment rules.
  - Evolve the PPO policy architecture without changing training commands.

---

## Designed for engineering rigor

- Modularity
  - Clear separation of concerns across data, environments, policies, and use-cases.

- Testability
  - Dependency-injected components make it straightforward to stub repositories and test training logic.

- Observability
  - Structured logging throughout long-running tasks such as downloads and training.

---

## Commands reference

- Download data
  - --download
  - --base-asset, --quote-asset
  - --interval

- Train PPO agent
  - --train
  - --base-asset, --quote-asset
  - --ppo-policy-id (optional, UUID)
  - --lower-interval, --higher-interval
  - --lower-interval-lookback-candles, --higher-interval-lookback-candles
  - --episodes, --max-time-steps

Run with:
```bash 
python -m trading_bot [OPTIONS]
```

---

## License

This project is licensed under the terms of the LICENSE file in the repository.

---

Want to discuss the design, training curves, or deployment story? I am happy to walk through the architecture and 
decisions in detail.
