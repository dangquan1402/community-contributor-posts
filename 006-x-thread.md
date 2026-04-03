1/7
Celery uses 2.5 GB to run 50 LLM API calls.

arq uses 80 MB.

LLM workloads are I/O-bound. Your task queue should be too. Here's what I learned:

2/7
LLM calls take 2-30 seconds. You're waiting on HTTP responses, not crunching numbers.

Celery spawns one OS process per worker. Great for CPU isolation, wasteful for network waits.

3/7
Memory for 50 concurrent LLM calls:

→ Celery (prefork): ~2.5 GB, 50 processes
→ Celery (gevent): ~500 MB, 1 process
→ RQ: ~2.5 GB, 50 processes
→ arq: ~80 MB, 1 process, 50 coroutines

That last line is not a typo.

4/7
Rate limiting with Celery is broken by design.

rate_limit is per-worker, not global. 5 workers x 10/min = 50/min actual.

arq runs in one async process. A simple semaphore gives you true global rate limiting.

5/7
I use both arq and RQ in the same stack:

→ arq: LLM calls (scoring, summarization, embeddings) — async, high concurrency, low memory
→ RQ: sync tasks (emails, reports, cleanup) — dead simple, just write a function

Both share the same Redis. No RabbitMQ needed.

6/7
When Celery still wins:

→ CPU-heavy work (image processing, ML training)
→ Complex workflows (chaining, fan-out, chord)
→ Multi-broker requirements

For pure LLM I/O? Overkill.

7/7
The LLM ecosystem is I/O-bound by nature. Your tools should reflect that.

Full post with diagrams and code:
dangquan1402.github.io/community-contributor-posts/2026/04/02/lightweight-task-queues-for-llm-apps.html

#LLM #Python #AI
