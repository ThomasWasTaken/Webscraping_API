# 🏢 Danish Housing Monitor

A robust, automated web scraper built with **Python** and **Playwright** to monitor real estate listings in Denmark. It currently supports tracking **CEJ** and **Kereby**, sending instant notifications to **Telegram** the moment a new apartment hits the market.

---

## ✨ Features

* **Dual-Mode Detection**: 
    * **Hash-based**: Monitors specific XPaths for any text/content changes (ideal for CEJ).
    * **Set-based**: Tracks unique listing URLs to identify exactly which new properties were added (ideal for Kereby).
* **Dynamic Content Handling**: Uses Playwright to handle JavaScript-rendered sites and automated scrolling to trigger "lazy-loading" elements.
* **Instant Alerts**: Integrated with the Telegram Bot API for real-time mobile notifications.
* **Clean Data**: Text normalization ensures you don't get "false positive" alerts due to extra whitespace or formatting shifts.
