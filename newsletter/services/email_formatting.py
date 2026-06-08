from html import escape


def build_subject(topic):
    return f"Your {topic.strip().title()} News Digest"


def build_digest_html(topic, articles):
    title = escape(topic.strip().title())
    article_html = []

    for article in articles:
        article_title = escape(article["title"])
        description = escape(article["description"])
        source = escape(article["source"])
        url = escape(article["url"], quote=True)
        article_html.append(
            f"""
            <tr>
                <td style="padding:18px 0;border-bottom:1px solid #e5e7eb;">
                    <h2 style="font-size:18px;line-height:1.3;margin:0 0 8px;color:#111827;">{article_title}</h2>
                    <p style="font-size:14px;line-height:1.6;margin:0 0 10px;color:#4b5563;">{description}</p>
                    <p style="font-size:13px;margin:0 0 10px;color:#6b7280;">{source}</p>
                    <a href="{url}" style="color:#0f766e;font-weight:600;">Read full article</a>
                </td>
            </tr>
            """
        )

    return f"""
    <!doctype html>
    <html>
    <body style="margin:0;padding:0;background:#f3f4f6;font-family:Arial,sans-serif;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f3f4f6;padding:24px;">
            <tr>
                <td align="center">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:680px;background:#ffffff;border-radius:8px;padding:28px;">
                        <tr>
                            <td>
                                <h1 style="font-size:24px;line-height:1.25;margin:0 0 8px;color:#111827;">Latest {title} News</h1>
                                <p style="font-size:15px;line-height:1.6;margin:0 0 8px;color:#4b5563;">Here are the top 5 recent articles for this topic.</p>
                            </td>
                        </tr>
                        {''.join(article_html)}
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
