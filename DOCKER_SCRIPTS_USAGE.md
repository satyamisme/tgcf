# Using Docker Management Scripts for tgcf

This document explains how to use the provided shell scripts to manage `tgcf` running inside a Docker container. These scripts help automate building the Docker image, starting, stopping, and viewing logs for your `tgcf` container.

## Prerequisites

1.  **Docker Installed:** Ensure Docker is installed and running on your system.
2.  **`Dockerfile`:** A `Dockerfile` must be present in the root directory of the `tgcf` project. This file defines how to build the `tgcf` Docker image.
3.  **Configuration Files:**
    *   `.env`: An environment file named `.env` must be present in the root directory. This file should contain your Telegram API credentials, bot tokens, passwords, etc. Example:
        ```env
        API_ID=1234567
        API_HASH=your_api_hash
        BOT_TOKEN=your_bot_token # If using a bot account for tgcf or plugins
        SESSION_STRING=your_session_string # If using a user account for tgcf or plugins
        PASSWORD=your_web_ui_password
        TGCF_MODE=live # or "past"
        # Add other necessary environment variables
        ```
    *   `tgcf.config.json`: Your main `tgcf` configuration file, named `tgcf.config.json`, must be present in the root directory.
4.  **Scripts:** The following scripts should be present in the root directory:
    *   `build-image.sh`
    *   `start-container.sh`
    *   `stop-container.sh`
    *   `view-logs.sh`

## Script Permissions

Before first use, make the scripts executable:

```bash
chmod +x build-image.sh start-container.sh stop-container.sh view-logs.sh
```

## Script Usage

It's recommended to run these scripts from the root directory of the `tgcf` project.

### 1. `build-image.sh`

*   **Purpose:** Builds (or rebuilds) the Docker image for `tgcf`. The image will be tagged as `tgcf-image`.
*   **Usage:**
    ```bash
    ./build-image.sh
    ```
*   Run this script once initially, and then again whenever you modify the `Dockerfile` or need to update the base image/dependencies within your `tgcf` Docker image.

### 2. `start-container.sh`

*   **Purpose:** Starts the `tgcf` application (assumed to be `tgcf-web` by default, listening on port 8501) in a detached Docker container named `my-tgcf-container`.
    *   It mounts your local `.env` and `tgcf.config.json` files into the container.
    *   It checks if the `tgcf-image` exists (build it first if not).
    *   It checks if a container with the same name is already running or stopped (and removes stopped ones before starting).
*   **Usage:**
    ```bash
    ./start-container.sh
    ```
*   If successful, it will indicate that the container has started and, if `tgcf-web` is running, that it should be accessible on port 8501 of your host machine (e.g., `http://localhost:8501`).
*   **Note on Configuration Path in Docker:** This script mounts `tgcf.config.json` to `/app/tgcf.config.json` and makes environment variables from `.env` available inside the container. Your `Dockerfile`'s `WORKDIR` should ideally be `/app`, or `tgcf` inside the container must be configured to look for its configuration at `/app/tgcf.config.json`.

### 3. `view-logs.sh`

*   **Purpose:** Displays the logs from the running `my-tgcf-container`.
*   **Usage:**
    *   To view live (tailed) logs:
        ```bash
        ./view-logs.sh
        ```
        (Press `Ctrl+C` to stop tailing.)
    *   To view all past logs:
        ```bash
        ./view-logs.sh --all
        ```
*   This is useful for monitoring `tgcf`'s activity or troubleshooting issues.

### 4. `stop-container.sh`

*   **Purpose:** Stops and removes the `my-tgcf-container`.
*   **Usage:**
    ```bash
    ./stop-container.sh
    ```
*   This will first attempt to gracefully stop the container and then remove it.

## Workflow Summary

1.  Place your `Dockerfile`, `.env`, and `tgcf.config.json` in the project root.
2.  Make scripts executable: `chmod +x *.sh`.
3.  Build the image: `./build-image.sh`.
4.  Start the container: `./start-container.sh`.
5.  Check logs if needed: `./view-logs.sh`.
6.  Access `tgcf-web` via `http://localhost:8501` (if `tgcf-web` is the application).
7.  Stop the container when done: `./stop-container.sh`.

These scripts provide a straightforward way to manage your `tgcf` Docker deployment. Remember to customize your `.env` and `tgcf.config.json` files according to your needs.
