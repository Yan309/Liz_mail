# Streamlit Configuration

This directory contains Streamlit configuration for the application.
It should be included in the repository for Hugging Face deployment.

## Files

- `config.toml` - Main Streamlit configuration
  - Sets port to 7860 (Hugging Face standard)
  - Configures theme colors
  - Disables usage stats for privacy

## Important

Do NOT add `secrets.toml` to this directory - use Hugging Face's Repository Secrets instead.
