# EchoMindAiBot 🚀🧠

> **Note:** This bot serves as the core backend and intelligent CMS, transforming raw inputs into structured insights that power a dynamic personal dashboard. For more details, visit: [Priyanshu-Priya/personal-website](https://github.com/Priyanshu-Priya/personal-website).

EchoMindAiBot is your personal AI-powered knowledge management and ingestion layer natively built into Telegram. It acts as an intelligent funnel for your personal dashboard, automatically categorizing and deeply analyzing the content you consume, while also capturing your everyday fleeting thoughts.

## 🌟 Core Features

The bot operates across two distinct domains:

### 1. Resonance (Content Curation)
Paste a URL, an article link, a podcast name, or a book title. The bot will:
- Automatically detect the content type (`Video`, `Article`, `Book`, `Podcast`).
- Fetch exact metadata (avoids AI hallucinations by using the YouTube oEmbed API for videos).
- Process the content through **Groq AI (Llama 3.3 70B)** to generate:
  - A piercing, 15-word intellectual insight (for videos, books, podcasts).
  - A highly intellectual summary (for articles).
  - 1-5 Star Ratings and semantic tags.
- Provide an interactive inline keyboard to **Confirm**, **Edit**, or **Regenerate** the review before saving to the Supabase `resonance` table.

### 2. Thoughts (Observations)
Type a plain text message. The bot will:
- Verify if it should be treated as a Content Link or a Thought.
- Prompt you for a **Mood** (Select from a beautifully formatted emoji list, type a custom mood, or skip entirely).
- Ask for **Visibility** (Publish immediately or Keep Private).
- Save the observation seamlessly to your Supabase `thoughts` table.

---

## 🏗️ Architecture

The codebase follows a strictly modular, scaling-friendly architecture:

```text
Dashboard Automation/
├── bot/
│   ├── core/           # Entry point routers, sessions, generic DB client
│   ├── resonance/      # Domain: AI logic, Content detection, Resonance DB Repo
│   └── thoughts/       # Domain: Mood workflows, UI state, Thoughts DB Repo
```

---

## 🛠️ Prerequisites

- **Python 3.10+**
- **Telegram Bot Token** (Get this from [@BotFather](https://t.me/BotFather))
- **Groq API Key** (For LLM inference)
- **Supabase Project** (Database URL and Service Role Key)

### Database Schema
You must have two tables in your Supabase `public` schema:

1. **`resonance`**
   - `id` (uuid)
   - `created_at` (timestamptz)
   - `title` (text)
   - `url` (text)
   - `type` (text)
   - `commentary` (text)
   - `resonance_score` (int2)
   - `tags` (text)

2. **`thoughts`**
   - `id` (uuid)
   - `created_at` (timestamptz)
   - `content` (text)
   - `mood` (text)
   - `is_published` (boolean)

---

## 🚀 Installation & Setup

1. **Clone the repository** (if applicable) and navigate to the project directory:
   ```bash
   cd "Dashboard Automation"
   ```

2. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root of the project with the following keys:
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-supabase-service-role-key

   TELEGRAM_BOT_TOKEN=your-bot-token

   GROQ_API_KEY=your-groq-api-key

   # Comma-separated list of Telegram User IDs allowed to use the bot
   AUTHORIZED_USER_IDS=123456789,987654321
   ```
   > *Tip: You can use `@userinfobot` on Telegram to find your User ID.*

4. **Run the Bot**:
   ```bash
   python run.py
   ```

---

## 🎮 Usage & Commands

You can interact with the bot through natural conversation or use the powerful built-in commands for a faster workflow:

- 💭 `/thought <text>` — Instantly start a fleeting observation. Skips routing menus and jumps straight to the Mood selector!
- 🧠 `/resonance <link or title>` — Bypasses all questions and forces the AI to curate the text as Resonance content.
- ⚡ `/fast` — Toggles "Fast Mode," saving all Resonance URLs instantly without asking for confirmation.
- ❌ `/cancel` — Instantly discards whatever menu or input you're currently in.
- 📖 `/help` — Displays an in-app usage guide.

---

## 🛡️ Security

The bot uses an `@authorized` decorator across all handlers. Any user attempting to send a message to the bot whose User ID is not found in the `AUTHORIZED_USER_IDS` environment whitelist will be instantly rejected.
