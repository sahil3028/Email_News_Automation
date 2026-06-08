import re
from datetime import date, timedelta

import requests
from django.conf import settings


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "for",
    "from",
    "in",
    "into",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}

SYNONYMS = {
    "ai": {"artificial intelligence", "machine learning", "genai", "generative ai"},
    "job": {"jobs", "employment", "hiring", "recruitment", "workforce", "jobseekers", "labor", "labour"},
    "jobs": {"job", "employment", "hiring", "recruitment", "workforce", "jobseekers", "labor", "labour"},
    "market": {"markets", "economy", "sector", "industry"},
    "india": {"indian", "bharat"},
    "technology": {"tech", "software", "it"},
}

MANDATORY_CONCEPTS = {
    "job",
    "jobs",
    "india",
    "indian",
}


def _topic_terms(topic):
    words = re.findall(r"[a-z0-9]+", topic.lower())
    return [word for word in words if word not in STOP_WORDS]


def _expanded_terms(terms):
    expanded = set(terms)
    for term in terms:
        expanded.update(SYNONYMS.get(term, set()))
    return expanded


def _term_variants(term):
    return {term, *SYNONYMS.get(term, set())}


def _contains_variant(text, term):
    for variant in _term_variants(term):
        if re.search(rf"\b{re.escape(variant)}\b", text):
            return True
    return False


def _build_query(topic, terms):
    quoted_topic = f'"{topic}"'
    if not terms:
        return quoted_topic

    required_terms = " AND ".join(terms[:5])
    if len(terms) == 1:
        return f'{quoted_topic} OR {terms[0]}'
    return f"{quoted_topic} OR ({required_terms})"


def _article_text(article):
    fields = [
        article.get("title") or "",
        article.get("description") or "",
        article.get("content") or "",
        (article.get("source") or {}).get("name") or "",
    ]
    return " ".join(fields).lower()


def _score_article(article, topic, terms, expanded_terms):
    title = (article.get("title") or "").lower()
    description = (article.get("description") or "").lower()
    content = (article.get("content") or "").lower()
    display_text = f"{title} {description}"
    full_text = _article_text(article)
    topic_lower = topic.lower()

    score = 0
    if topic_lower in title:
        score += 12
    elif topic_lower in full_text:
        score += 8

    for term in terms:
        if term in MANDATORY_CONCEPTS and not _contains_variant(display_text, term):
            return 0

    matched_display_groups = 0
    for term in terms:
        variants = _term_variants(term)
        display_matched = False
        for variant in variants:
            variant_pattern = rf"\b{re.escape(variant)}\b"
            if re.search(variant_pattern, title):
                score += 5
                display_matched = True
                break
            if re.search(variant_pattern, description):
                score += 3
                display_matched = True
                break
            if re.search(variant_pattern, content):
                score += 1
                break
        if display_matched:
            matched_display_groups += 1

    for term in expanded_terms - set(terms):
        if term in title:
            score += 2
        elif term in description:
            score += 1

    if terms and matched_display_groups == len(terms):
        score += 8
    if terms and matched_display_groups < min(2, len(terms)) and topic_lower not in display_text:
        return 0

    return score


def _title_key(title):
    title = re.sub(r"^(analysis|opinion|explainer)[-:\s]+", "", title.lower())
    words = re.findall(r"[a-z0-9]+", title)
    return " ".join(word for word in words if word not in STOP_WORDS)[:90]


def _clean_article(article):
    return {
        "title": article["title"],
        "description": article.get("description") or "No description available.",
        "url": article["url"],
        "source": (article.get("source") or {}).get("name") or "Unknown source",
    }


def fetch_news(topic, limit=5):
    topic = (topic or "").strip()
    if not topic:
        raise ValueError("Enter a topic before previewing or sending.")
    if not settings.NEWS_API_KEY:
        raise RuntimeError("Missing environment variable: API_KEY")

    terms = _topic_terms(topic)
    params = {
        "q": _build_query(topic, terms),
        "from": (date.today() - timedelta(days=30)).isoformat(),
        "sortBy": "relevancy",
        "language": "en",
        "searchIn": "title,description,content",
        "pageSize": min(100, max(30, limit * 10)),
        "apiKey": settings.NEWS_API_KEY,
    }

    try:
        response = requests.get("https://newsapi.org/v2/everything", params=params, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError("News API request failed. Please try again later.") from exc

    payload = response.json()
    if payload.get("status") != "ok":
        raise RuntimeError(payload.get("message") or "News API returned an error.")

    candidates = []
    expanded_terms = _expanded_terms(terms)
    seen_urls = set()
    seen_titles = set()
    for article in payload.get("articles", []):
        if not article.get("title") or not article.get("url"):
            continue
        if article["url"] in seen_urls:
            continue
        title_key = _title_key(article["title"])
        if title_key in seen_titles:
            continue
        seen_urls.add(article["url"])
        seen_titles.add(title_key)
        score = _score_article(article, topic, terms, expanded_terms)
        if score > 0:
            candidates.append((score, article))

    candidates.sort(key=lambda item: item[0], reverse=True)
    articles = [_clean_article(article) for _, article in candidates[:limit]]

    if not articles:
        raise RuntimeError("No relevant articles were found for that topic. Try a broader topic.")
    return articles
