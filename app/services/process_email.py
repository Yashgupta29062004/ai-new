import os
import sys
import smtplib
from pathlib import Path
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.databases.repositry import Repository
from app.databases.model import Digest

# ── Source metadata ─────────────────────────────────────────────────────────
SOURCE_META = {
    "anthropic": {"label": "Anthropic", "emoji": "🟠", "color": "#d97706"},
    "openai":    {"label": "OpenAI",    "emoji": "🟢", "color": "#059669"},
    "youtube":   {"label": "YouTube",   "emoji": "📺", "color": "#dc2626"},
}


def _score_badge(score: float) -> str:
    """Return an inline-styled score badge."""
    if score is None:
        return ""
    if score >= 8.0:
        bg, fg = "#064e3b", "#34d399"
    elif score >= 6.0:
        bg, fg = "#451a03", "#fb923c"
    else:
        bg, fg = "#1e1b4b", "#a5b4fc"
    return (
        f'<span style="background:{bg};color:{fg};padding:2px 10px;'
        f'border-radius:12px;font-size:11px;font-weight:700;'
        f'letter-spacing:0.5px;">⭐ {score:.1f}/10</span>'
    )


def _render_card(digest: Digest, rank: int) -> str:
    meta = SOURCE_META.get(digest.article_type, {"label": digest.article_type, "color": "#6b7280"})
    badge = _score_badge(digest.score or 0)
    source_tag = (
        f'<span style="background:#1e293b;color:{meta["color"]};'
        f'padding:2px 9px;border-radius:10px;font-size:11px;font-weight:600;">'
        f'{meta["label"]}</span>'
    )
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:12px;">
      <tr>
        <td style="background:#1a1a2e;border:1px solid #2d2d44;border-radius:10px;
                   padding:20px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
          <!-- Header row -->
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td>{source_tag} &nbsp; {badge}</td>
              <td align="right" style="color:#475569;font-size:12px;">#{rank}</td>
            </tr>
          </table>
          <!-- Title -->
          <p style="margin:10px 0 8px;font-size:16px;font-weight:700;color:#f1f5f9;line-height:1.4;">
            {digest.title}
          </p>
          <!-- Summary -->
          <p style="margin:0 0 14px;font-size:14px;color:#94a3b8;line-height:1.7;">
            {digest.summary}
          </p>
          <!-- Read more -->
          <a href="{digest.url}"
             style="color:#7c3aed;font-size:13px;font-weight:600;text-decoration:none;">
            Read full article →
          </a>
        </td>
      </tr>
    </table>"""


def _render_html(digests: List[Digest], hours: int) -> str:
    today = datetime.now(timezone.utc).strftime("%B %d, %Y")
    cards_html = "".join(_render_card(d, i + 1) for i, d in enumerate(digests))
    count = len(digests)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily AI Digest — {today}</title>
</head>
<body style="margin:0;padding:0;background:#0f0f13;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">

  <!-- Wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f0f13;padding:30px 0;">
    <tr>
      <td align="center">
        <table width="640" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%;">

          <!-- ── HEADER ── -->
          <tr>
            <td style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);
                       border-radius:14px 14px 0 0;padding:40px 32px;text-align:center;">
              <p style="margin:0 0 6px;font-size:12px;font-weight:600;letter-spacing:3px;
                        color:#7c3aed;text-transform:uppercase;">Daily Digest</p>
              <h1 style="margin:0 0 8px;font-size:28px;font-weight:800;color:#f1f5f9;">
                🤖 AI News Digest
              </h1>
              <p style="margin:0;font-size:14px;color:#64748b;">{today} &nbsp;·&nbsp; Top {count} stories</p>
            </td>
          </tr>

          <!-- ── STATS BAR ── -->
          <tr>
            <td style="background:#12122a;padding:14px 32px;border-left:1px solid #1e1e3a;
                       border-right:1px solid #1e1e3a;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="color:#94a3b8;font-size:13px;">
                    🟠 <strong style="color:#f1f5f9;">Anthropic</strong>
                    &nbsp;&nbsp;|&nbsp;&nbsp;
                    🟢 <strong style="color:#f1f5f9;">OpenAI</strong>
                    &nbsp;&nbsp;|&nbsp;&nbsp;
                    📺 <strong style="color:#f1f5f9;">YouTube</strong>
                    &nbsp;&nbsp;·&nbsp;&nbsp;
                    Last <strong style="color:#7c3aed;">{hours}h</strong>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ── ARTICLES ── -->
          <tr>
            <td style="background:#0f0f13;padding:24px 28px;
                       border:1px solid #1e1e3a;border-top:none;">
              {cards_html}
            </td>
          </tr>

          <!-- ── FOOTER ── -->
          <tr>
            <td style="background:#12122a;border:1px solid #1e1e3a;border-top:none;
                       border-radius:0 0 14px 14px;padding:24px 32px;text-align:center;">
              <p style="margin:0 0 6px;font-size:13px;color:#475569;">
                Ranked by relevance score · Powered by Gemini
              </p>
              <p style="margin:0;font-size:11px;color:#334155;">
                You're receiving this because you set up the AI News Aggregator.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def send_digest_email(hours: int = 24, top_n: int = 10) -> dict:
    """
    Main entry point called by daily_runner.py.
    Fetches top digests, renders HTML, and sends via Gmail SMTP.
    """
    smtp_host     = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port     = int(os.getenv("SMTP_PORT", "587"))
    smtp_user     = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    email_to      = os.getenv("DIGEST_EMAIL_TO", smtp_user)

    if not smtp_user or not smtp_password:
        return {
            "success": False,
            "articles_count": 0,
            "error": "SMTP_USER or SMTP_PASSWORD not set in environment.",
        }

    repo = Repository()
    digests = repo.get_recent_digests(hours=hours, top_n=top_n)

    if not digests:
        return {
            "success": False,
            "articles_count": 0,
            "error": "No digests found for the given time window.",
        }

    today = datetime.now(timezone.utc).strftime("%B %d, %Y")
    subject = f"🤖 Daily AI Digest — {today} ({len(digests)} stories)"

    html_body = _render_html(digests, hours)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = smtp_user
    msg["To"]      = email_to
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, email_to, msg.as_string())

        print(f" Email sent to {email_to} with {len(digests)} articles.")
        return {"success": True, "articles_count": len(digests)}

    except Exception as e:
        print(f" Email send failed: {e}")
        return {"success": False, "articles_count": 0, "error": str(e)}


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    print(" Sending digest email...")
    result = send_digest_email(hours=24, top_n=10)
    if result["success"]:
        print(f" Done! Sent {result['articles_count']} articles.")
    else:
        print(f" Failed: {result.get('error')}")
