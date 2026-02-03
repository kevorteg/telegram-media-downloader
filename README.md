# 🤖 Telegram Media Downloader Bot

A powerful, cloud-ready Telegram bot designed to automatically download, process, and forward media from **Twitter (X), Instagram, TikTok, YouTube (Shorts)**, and thousands of other sites supported by `yt-dlp`.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Enabled-green?style=for-the-badge&logo=ffmpeg&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)

## ✨ Key Features

*   **Multi-Platform Support**: Downloads high-quality videos from Twitter/X, Instagram, TikTok, Facebook, Reddit, and basically any site supported by `yt-dlp`.
*   **Smart Video Processing**:
    *   **Auto-Compression**: Automatically compresses videos larger than 50MB to fit within Telegram Bot API limits, ensuring delivery even for long content.
    *   **Aspect Ratio Fix**: Uses FFmpeg to detect real video dimensions, preventing the "stretched video" glitch common in Telegram bots.
*   **Twitter Like Monitor**: (Optional) Automatically monitors a target Twitter account's "Likes" and downloads new videos as they are liked.
*   **Cloud-Native & Secure**:
    *   **Dockerized**: Comes with a standardized `Dockerfile` including FFmpeg.
    *   **Environment Cookies**: Supports loading sensitive cookies via Environment Variables (`COOKIES_CONTENT`), eliminating the need to upload `cookies.txt` to public repositories.
*   **Storage Efficient**: Auto-deletes downloaded files immediately after forwarding to keep disk usage near zero.

## 🚀 Quick Deployment (Koyeb / Render)

This project is optimized for PaaS platforms like **Koyeb**.

1.  **Fork** this repository.
2.  Create a new **Web Service** on Koyeb connected to your repo.
3.  **Builder**: Select **Dockerfile**.
4.  **Environment Variables**: Add the following required variables:

| Variable | Description |
| :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | Your Bot Token from @BotFather. |
| `TARGET_CHANNEL_ID` | The Chat ID of the channel/group where videos will be sent. |
| `TWITTER_USERNAME` | (Optional) Twitter username to monitor for likes (without @). |
| `COOKIES_CONTENT` | (Optional/Recommended) Copy & Paste the full content of your `cookies.txt` here to access restricted/18+ content. |
| `ADMIN_USER_IDS` | (Optional) Comma-separated list of User IDs allowed to use admin commands. |

5.  Click **Deploy**.

## 💻 Local Installation

### Prerequisites
*   Python 3.10 or higher.
*   **FFmpeg** installed and added to your system PATH.

### Setup
1.  Clone the repository:
    ```bash
    git clone https://github.com/kevorteg/telegram-media-downloader.git
    cd telegram-media-downloader
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Create a `.env` file (copy from `.env.example` if available) and configure your secrets.
4.  Run the bot:
    ```bash
    python autovideo/bot.py
    ```

## 🍪 Cookie Management

To download content from age-gated or restricted sites (Twitter NSFW, etc.), the bot needs browser cookies.

*   **Method A (Local)**: Place your `cookies.txt` (Netscape format) in the `autovideo/` directory.
*   **Method B (Cloud)**: Copy the text content of your `cookies.txt` and paste it into the `COOKIES_CONTENT` environment variable.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
