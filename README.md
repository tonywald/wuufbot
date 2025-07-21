# WuufBot - A Telegram group moderation & management bot

Meet **WuufBot**, a Telegram bot designed for chat moderation and administration. It provides a suite of tools for helping to maintain order, manage users, and assist with chat security.

## Features

- **Moderation**: A suite of commands including ban, mute, kick, and purge to manage chat activity.
- **Security Layers**: Features like a global ban (gban) system and a personal blacklist to protect your communities from malicious users across all groups.
- **Multi-Level Administration**: A permission system with three levels: Owner, Developer, and Support/Sudo users (chat administrators/bot admins), ensuring granular control over the bot's features.
- **Information Retrieval**: Commands to get in-depth information about users, chats, and the bot's own operational status.
- **Configurable**: Configured via environment variables, allowing for easy deployment.

## Known Bugs
- **Groups with topics** Description: The bot works, but its functionality in the topics of a given group disappears. The bot cannot force a search using the user resolver. The target is always the user who created the topic. (It is recommended to use the bot on the General topic). 

## How to run

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/tonywald/wuufbot wuufbot
    ```

2.  **Set up virtual environment & Install requirements:**
    ```bash
    pyenv install 3.12.10 && pyenv local 3.12.10 && pyenv virtualenv project-name && pyenv activate project-name;
    pip install -r requirements.txt  
    ```

3.  **Set up your environment variables:**
    ```bash
    nvim ~/wuufbot/.env
    ```

4.  **Run the bot:**
    Navigate to the bot's directory and run it using the script:
    ```bash
    cd ~/wuufbot && python3 wuufbot.py
    ```


# Official Links:
-   **Support Chat:** https://t.me/wuufbotsupport
