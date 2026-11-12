import os
import json
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Daily Neuron API", version="1.0.0")

# Preloaded Curated AI News Items with Dual Formats
NEWS_DATABASE = [
    {
        "id": "deepseek-v3",
        "title": "DeepSeek-V3: 671B MoE с 37B активных параметров бросает вызов проприетарным моделям",
        "category": "LLM",
        "hype_score": 98,
        "source": "GitHub / DeepSeek-AI",
        "timestamp": "2026-11-12T08:00:00Z",
        "summary_10s": [
            "671B общих параметров при 37B активируемых на токен благодаря архитектуре Multi-head Latent Attention (MLA).",
            "Обучена всего за 2.788M H800 GPU-часов, стоимость тренировки составила менее $6M.",
            "Превзошла Llama 3.1 405B и приблизилась к Claude 3.5 Sonnet на математических и кодовых бенчмарках."
        ],
        "technical_teardown": {
            "architecture": "DeepSeek Sparse MoE + Multi-Head Latent Attention (MLA)",
            "context_window": "128,000 токенов (Native YARN rotary scaling)",
            "benchmarks": {"MMLU": "88.5%", "HumanEval": "82.6%", "MATH-500": "90.2%"},
            "quantization": "FP8 Mixed Precision Native Checkpoints",
            "vram_requirement": "8x H100 (80GB) для квантованного FP8 инференса без разгрузки в CPU"
        }
    },
    {
        "id": "wan-2-1",
        "title": "Wan 2.1: Открытая диффузионная модель генерации 1080p видео с пространственно-временным VAE",
        "category": "Video Gen",
        "hype_score": 94,
        "source": "HuggingFace / Wan-Video",
        "timestamp": "2026-11-12T06:30:00Z",
        "summary_10s": [
            "Генерация фотореалистичного 1080p видео с кинематографической физикой и устойчивыми пальцами.",
            "Поддерживает как Text-to-Video, так и Image-to-Video на открытых весах 1.3B и 14B.",
            "Встроенная генерация аудиодорожки и пространственно-временной автоэнкодер (3D Causal VAE)."
        ],
        "technical_teardown": {
            "architecture": "DiT (Diffusion Transformer) с 3D Spatio-Temporal Attention",
            "resolution": "До 1920x1080 при 24 FPS (до 5 секунд непрерывного движения)",
            "benchmarks": {"VBench": "84.3/100", "Temporal Consistency": "0.91"},
            "quantization": "GGUF Q4_K_M для потребительских GPU",
            "vram_requirement": "12GB VRAM для модели 1.3B; 24GB VRAM для модели 14B в FP8"
        }
    },
    {
        "id": "vllm-v07",
        "title": "vLLM v0.7: Нулевое копирование тензоров и PagedAttention V3 для серверного инференса",
        "category": "Open Source",
        "hype_score": 89,
        "source": "GitHub / vllm-project",
        "timestamp": "2026-11-11T22:15:00Z",
        "summary_10s": [
            "Прирост пропускной способности генерации токенов на 42% на кластерах H100.",
            "Полная нативная поддержка спекулятивного декодирования и квантования FP8/INT4 AWQ.",
            "Интеграция с Ray v2.30 для распределенного обслуживания моделей до 1T параметров."
        ],
        "technical_teardown": {
            "architecture": "PagedAttention-3 с блочным кэшем в pinned memory",
            "speculative_decoding": "Medusa / Eagle heads без дополнительного процесса",
            "benchmarks": {"Throughput": "4,820 tok/sec на 8x A100", "TTFT (Latency)": "14ms"},
            "quantization": "Marlin, GPTQ, AWQ, BitsAndBytes 4-bit",
            "vram_requirement": "Экономия до 35% видеопамяти под KV-кэш по сравнению с v0.6"
        }
    },
    {
        "id": "smolagents",
        "title": "Smolagents от HuggingFace: Агенты на чистом Python коде вместо медленного JSON Tool Calling",
        "category": "Agents",
        "hype_score": 91,
        "source": "HuggingFace Hub",
        "timestamp": "2026-11-11T19:40:00Z",
        "summary_10s": [
            "Агенты пишут исполняемые сниппеты Python вместо громоздких структурированных JSON схем.",
            "Экономия контекстного окна до 70% и ускорение многошаговых рассуждений в 3 раза.",
            "Встроенная изоляция в WebAssembly и песочницах для защиты от случайного выполнения опасных команд."
        ],
        "technical_teardown": {
            "architecture": "CodeAgent с AST-валидацией и REPL окружением",
            "token_efficiency": "3.2x меньше токенов на цепочку reasoning по сравнению с ReAct JSON",
            "benchmarks": {"GAIA Benchmark": "48.2% (1-е место среди легковесных фреймворков)"},
            "sandbox": "Pyodide / E2B microVMs",
            "vram_requirement": "Работает локально с моделями от 3B (Llama 3.2 3B)"
        }
    }
]

TICKER_ITEMS = [
    "🔥 DeepSeek-V3 достиг 88.5% на MMLU",
    "🎬 Wan 2.1 14B выложен на HuggingFace",
    "⚡️ vLLM v0.7 ускорил serving на 42%",
    "🤖 Smolagents обогнал ReAct на GAIA Benchmark"
]

class NewsItem(BaseModel):
    id: str
    title: str
    category: str
    hype_score: int
    source: str
    timestamp: str
    summary_10s: List[str]
    technical_teardown: dict

@app.get("/api/news")
def get_news(category: Optional[str] = None, min_hype: Optional[int] = Query(0, ge=0, le=100)):
    items = NEWS_DATABASE
    if category and category.lower() != "all":
        items = [i for i in items if i["category"].lower() == category.lower()]
    if min_hype > 0:
        items = [i for i in items if i["hype_score"] >= min_hype]
    return {"count": len(items), "news": items}

@app.get("/api/news/{item_id}")
def get_single_news(item_id: str):
    item = next((i for i in NEWS_DATABASE if i["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    return item

@app.get("/api/ticker")
def get_ticker():
    return {"ticker": TICKER_ITEMS}

@app.post("/api/news/crawl")
def trigger_crawl():
    # Simulate news ingestion cycle
    new_count = len(NEWS_DATABASE)
    return {
        "status": "success",
        "ingested_count": new_count,
        "sources_polled": ["GitHub Trending AI", "HuggingFace Trending Models", "Arxiv cs.AI"],
        "message": f"Свежие тренды успешно проанализированы. Всего материалов в базе: {new_count}."
    }

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(CURRENT_DIR, "index.html")

@app.get("/", response_class=HTMLResponse)
def serve_index():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Daily Neuron API is running. UI template not found.</h1>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8004, reload=False)
