import pytest
from fastapi.testclient import TestClient
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR in sys.path:
    sys.path.remove(BASE_DIR)
sys.path.insert(0, BASE_DIR)
for mod in list(sys.modules.keys()):
    if mod == "web" or mod.startswith("web.") or mod == "bot" or mod.startswith("bot."):
        del sys.modules[mod]

from web.app import app, NEWS_DATABASE, TICKER_ITEMS
from bot.bot import create_daily_neuron_bot, CATEGORIES, USER_SUBSCRIPTIONS, DIGEST_ITEMS

client = TestClient(app)

def test_api_get_all_news():
    res = client.get("/api/news")
    assert res.status_code == 200
    data = res.json()
    assert "news" in data
    assert data["count"] >= 4
    # Check structure
    first = data["news"][0]
    assert "summary_10s" in first
    assert len(first["summary_10s"]) == 3
    assert "technical_teardown" in first
    assert "hype_score" in first

def test_api_news_filtering_by_category():
    res = client.get("/api/news?category=llm")
    assert res.status_code == 200
    data = res.json()
    assert all(item["category"] == "LLM" for item in data["news"])

def test_api_news_filtering_by_min_hype():
    res = client.get("/api/news?min_hype=93")
    assert res.status_code == 200
    data = res.json()
    assert all(item["hype_score"] >= 93 for item in data["news"])

def test_api_single_news_item():
    res = client.get("/api/news/deepseek-v3")
    assert res.status_code == 200
    item = res.json()
    assert item["id"] == "deepseek-v3"
    assert "Multi-Head Latent Attention" in item["technical_teardown"]["architecture"]

    res_404 = client.get("/api/news/non_existent_id")
    assert res_404.status_code == 404

def test_api_ticker_and_crawler():
    res_ticker = client.get("/api/ticker")
    assert res_ticker.status_code == 200
    assert len(res_ticker.json()["ticker"]) >= 3

    res_crawl = client.post("/api/news/crawl")
    assert res_crawl.status_code == 200
    assert res_crawl.json()["status"] == "success"
    assert res_crawl.json()["ingested_count"] >= 4

def test_bot_subscription_filtering_logic():
    # User subscribed only to 'video'
    test_user_id = 99999
    USER_SUBSCRIPTIONS[test_user_id] = {"video"}

    subs = USER_SUBSCRIPTIONS[test_user_id]
    filtered_digest = [item for item in DIGEST_ITEMS if item["cat"] in subs]
    assert len(filtered_digest) == 1
    assert filtered_digest[0]["cat"] == "video"

def test_bot_app_initialization():
    bot, dp = create_daily_neuron_bot()
    assert bot is not None
    assert dp is not None
    assert len(dp.sub_routers) >= 1
    assert "llm" in CATEGORIES
    assert "agents" in CATEGORIES
