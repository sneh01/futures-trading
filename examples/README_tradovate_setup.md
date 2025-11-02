# Tradovate Paper Trading Setup Instructions

This guide explains how to set up your environment for using the `ExecutionEngine` with Tradovate's paper trading API.

## 1. Obtain Tradovate API Credentials
- Sign up for a Tradovate demo account at https://tradovate.com/
- Request API access and obtain the following credentials:
  - Username
  - Password
  - App ID
  - App Secret

## 2. Set Environment Variables
For security, store your credentials as environment variables. You can do this in your terminal before running your script:

```bash
export TRADOVATE_USERNAME="your_username"
export TRADOVATE_PASSWORD="your_password"
export TRADOVATE_APP_ID="your_app_id"
export TRADOVATE_APP_SECRET="your_app_secret"
```

You can add these lines to your `~/.bash_profile`, `~/.zshrc`, or equivalent shell config file for persistence.

## 3. Run the Example Script
Navigate to your project directory and run:

```bash
python examples/tradovate_paper_example.py
```

This will:
- Authenticate with Tradovate's demo API
- Place a sample market order using the provided signal

## 4. Notes
- The example uses demo (paper) trading. For live trading, set `tradovate_demo=False` in the `ExecutionEngine`.
- Never commit your credentials to source control.
- For more details, see the official Tradovate API docs: https://api-d.tradovate.com/

---

If you have any issues, double-check your credentials and network connection.
