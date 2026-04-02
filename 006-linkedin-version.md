Why I Chose arq and RQ Over Celery for LLM Workloads

If you're building LLM apps with FastAPI, you need a task queue. LLM API calls take 2-30 seconds — you can't block your web server. But Celery is overkill for this.

LLM workloads are I/O bound. You're waiting on HTTP responses, not crunching numbers. Celery spawns separate OS processes per worker — great for CPU isolation, wasteful for network waits.

The numbers tell the story. For 50 concurrent LLM calls:
- Celery (prefork): ~2.5 GB, 50 processes
- Celery (gevent): ~500 MB, 1 process
- RQ: ~2.5 GB, 50 processes
- arq: ~80 MB, 1 process, 50 coroutines

arq is async-native. It runs 50 concurrent tasks in a single process because they're all just awaiting network I/O. It was built by Samuel Colvin (same person behind Pydantic).

Rate limiting is simpler too. Celery's rate_limit is per-worker, not global — 5 workers × 10/min = 50/min actual. With arq's single-process async model, an in-process semaphore gives you true global rate limiting.

I use both arq and RQ:
- arq → LLM API calls (scoring, summarization, embeddings). Async, high concurrency, low memory
- RQ → Simple sync tasks (emails, reports, cleanup). Dead simple, "just write a function"

Both share the same Redis. No RabbitMQ, no Celery Beat, no Flower dashboard. Just Redis, which I already need for caching.

When to still use Celery: CPU-heavy work (image processing, ML training), complex workflows (chaining, fan-out, chord), or multi-broker requirements.

The LLM ecosystem is I/O-bound by nature. Your tools should reflect that.

Full post with code examples and comparison tables: https://github.com/dangquan1402/community-contributor-posts/blob/main/006-lightweight-task-queues-for-llm-apps.md
