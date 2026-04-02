---
layout: post
title: "Why I Chose arq and RQ Over Celery for LLM Workloads"
date: 2026-04-02
---

If you're building LLM-powered applications with FastAPI, you need a task queue. LLM API calls are slow — 2 to 30 seconds per request. You can't block your web server on that. But the default answer in the Python world has always been Celery, and for LLM workloads, Celery is overkill.

* TOC
{:toc}

## LLM Workloads Are I/O Bound

The first thing to understand is that LLM workloads are fundamentally I/O bound. You're not doing heavy computation — you're waiting for an HTTP response from OpenAI, Anthropic, or your self-hosted model. The CPU is idle while you wait. This changes everything about what you need from a task queue.

Celery was designed for a different world. It was built for CPU-bound tasks — image processing, data crunching, report generation. It uses multiprocessing by default, spawning separate OS processes for each worker. That makes sense when you need CPU isolation. But for I/O-bound LLM calls, you're paying the memory overhead of multiple processes just to... wait on network responses.

| Aspect | CPU-Bound (Celery's sweet spot) | I/O-Bound (LLM calls) |
|---|---|---|
| Bottleneck | CPU computation | Network latency |
| Concurrency model | Multiprocessing (OS processes) | Async I/O or threading |
| Memory per worker | High (each process = full Python runtime) | Low (coroutines share one process) |
| Typical task duration | Milliseconds to seconds | 2-30 seconds |
| Scaling strategy | More CPU cores | More concurrent connections |

---

## Celery vs RQ vs arq

| Feature | Celery | RQ (Redis Queue) | arq |
|---|---|---|---|
| Broker | Redis, RabbitMQ, SQS, etc. | Redis only | Redis only |
| Concurrency | Multiprocessing, eventlet, gevent | Multiprocessing (1 task per worker) | Native async/await |
| Async support | No native async (gevent/eventlet as workaround) | No (sync only) | First-class |
| Dependencies | Heavy (~15 transitive deps) | Minimal (~3 deps) | Minimal (~2 deps) |
| Setup complexity | High (broker config, result backend, serializer, etc.) | Low | Low |
| Rate limiting | Built-in (per-task) | Manual | Manual (but async makes it natural) |
| Retry logic | Built-in, configurable | Built-in, basic | Built-in, configurable |
| Monitoring | Flower (separate service) | rq-dashboard | arq's built-in health checks |
| Task routing | Advanced (multiple queues, priority) | Basic (named queues) | Basic (named queues) |
| Periodic tasks | Celery Beat (separate process) | rq-scheduler (separate) | Built-in cron support |
| Learning curve | Steep | Gentle | Gentle |

Here's what the setup looks like for each:

```python
# Celery — lots of configuration
from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')
app.conf.update(
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    task_routes={'tasks.score': {'queue': 'llm'}},
    task_rate_limit='10/m',
)

@app.task(bind=True, max_retries=3, retry_backoff=True)
def score_response(self, text):
    # This is sync — Celery runs it in a subprocess
    result = openai_client.chat.completions.create(...)
    return result.choices[0].message.content
```

```python
# RQ — simple and straightforward
from redis import Redis
from rq import Queue

redis_conn = Redis()
q = Queue('llm', connection=redis_conn)

def score_response(text):
    # Plain sync function
    result = openai_client.chat.completions.create(...)
    return result.choices[0].message.content

# Enqueue
job = q.enqueue(score_response, text, retry=Retry(max=3, interval=60))
```

```python
# arq — async-native, fits naturally with FastAPI
from arq import create_pool
from arq.connections import RedisSettings

async def score_response(ctx, text):
    # Native async — no thread pool, no subprocess
    result = await async_openai_client.chat.completions.create(...)
    return result.choices[0].message.content

class WorkerSettings:
    functions = [score_response]
    redis_settings = RedisSettings()
    max_jobs = 50  # 50 concurrent async tasks in ONE process
```

Notice the difference: [arq [1]](https://arq-docs.helpmanual.io/) runs 50 concurrent LLM calls in a single process because they're all just awaiting network I/O. [Celery [3]](https://docs.celeryq.dev/) would need 50 processes for the same concurrency. [RQ [2]](https://python-rq.org/) would need 50 worker processes.

One important note: Celery still has no native async/await support as of 2025. The [async support issue (GitHub #6552)](https://github.com/celery/celery/issues/6552) has been open since 2020 and keeps getting deferred. You can use gevent or eventlet as workarounds, or third-party packages like celery-aio-pool, but these are hacks around a fundamentally sync architecture. arq was built async from day one — by Samuel Colvin, the same person behind Pydantic.

---

## Memory Footprint

The memory difference is significant in practice:

| Setup | Concurrency | Memory usage | Processes |
|---|---|---|---|
| Celery (prefork, default) | 50 tasks | ~2.5 GB (50 × ~50 MB) | 50 |
| Celery (gevent) | 50 tasks | ~500 MB (1 process + greenlets) | 1 |
| RQ | 50 tasks | ~2.5 GB (50 × ~50 MB) | 50 |
| arq | 50 tasks | ~80 MB (1 process, 50 coroutines) | 1 |

These are rough numbers, but the order of magnitude is real. When you're deploying on a single VPS or a small Kubernetes pod, this matters.

---

## Rate Limiting LLM APIs

Every LLM provider has [rate limits [4]](https://platform.openai.com/docs/guides/rate-limits) — requests per minute, tokens per minute, sometimes both. If you blast 100 concurrent requests, you'll get 429 errors. You need to throttle.

Celery has built-in rate limiting (`rate_limit='10/m'`), but it's per-worker, not global. If you have 5 workers each set to 10/minute, you're actually doing 50/minute. You need a separate mechanism for global rate limiting.

With arq, since everything runs in one process with async, you can use a simple semaphore or token bucket:

```python
import asyncio
from collections import deque
import time

class RateLimiter:
    def __init__(self, max_per_minute: int):
        self.max_per_minute = max_per_minute
        self.semaphore = asyncio.Semaphore(max_per_minute)
        self.timestamps: deque = deque()

    async def acquire(self):
        await self.semaphore.acquire()
        now = time.monotonic()
        # Clean old timestamps
        while self.timestamps and self.timestamps[0] < now - 60:
            self.timestamps.popleft()
            self.semaphore.release()
        self.timestamps.append(now)

rate_limiter = RateLimiter(max_per_minute=50)

async def score_response(ctx, text):
    await rate_limiter.acquire()
    result = await async_openai_client.chat.completions.create(...)
    return result
```

Because arq workers are single-process async, this in-process rate limiter actually works. With Celery's multiprocessing, you'd need Redis-based distributed rate limiting — more complexity.

---

## Why I Use Both arq and RQ

arq is my default for LLM API calls — scoring, summarization, embeddings, anything that's an async HTTP call to an LLM provider. The async-native design means I get high concurrency with minimal resources, and it fits perfectly with FastAPI's async ecosystem.

RQ I use for simpler background tasks that are sync by nature — sending emails, generating PDF reports, running database migrations, cleanup jobs. Tasks where I don't need high concurrency and the simplicity of "just write a regular function" is the priority.

<pre class="mermaid">
graph LR
    API["FastAPI"] --> R["Redis"]
    R --> ARQ["arq Worker"]
    R --> RQW["RQ Worker"]
    ARQ --> LLM["LLM APIs"]
    RQW --> SYNC["Sync Tasks"]

    style API fill:#264653,stroke:#264653,color:#fff
    style R fill:#e76f51,stroke:#e76f51,color:#fff
    style ARQ fill:#2a9d8f,stroke:#2a9d8f,color:#fff
    style RQW fill:#e9c46a,stroke:#e9c46a,color:#000
    style LLM fill:#2d6a4f,stroke:#2d6a4f,color:#fff
    style SYNC fill:#f4a261,stroke:#f4a261,color:#000
</pre>

Both share the same Redis instance. FastAPI enqueues to whichever queue fits the task. No RabbitMQ, no Celery Beat process, no Flower monitoring server. Just Redis, which I already need for caching and session storage.

---

## FastAPI Integration

The integration with [FastAPI [6]](https://fastapi.tiangolo.com/tutorial/background-tasks/) is clean:

```python
from fastapi import FastAPI
from arq import create_pool
from arq.connections import RedisSettings

app = FastAPI()

@app.on_event("startup")
async def startup():
    app.state.arq = await create_pool(RedisSettings())

@app.post("/score")
async def score(text: str):
    job = await app.state.arq.enqueue_job("score_response", text)
    return {"job_id": job.job_id}

@app.get("/score/{job_id}")
async def get_score(job_id: str):
    job = await app.state.arq.job(job_id)
    if await job.status() == "complete":
        return {"score": await job.result()}
    return {"status": "processing"}
```

No sync/async bridge. No thread pool executor wrapping. The whole stack is async end-to-end: FastAPI → Redis → arq → [async LLM client [7]](https://docs.python.org/3/library/asyncio.html).

---

## When to Actually Use Celery

Celery isn't dead — it's just not the right tool for every job:

| Use case | Best choice | Why |
|---|---|---|
| LLM API calls (scoring, summarization) | arq | Async I/O, high concurrency, low memory |
| Simple background jobs (email, cleanup) | RQ | Dead simple, sync is fine |
| CPU-heavy tasks (image processing, ML training) | Celery | Multiprocessing isolates CPU work |
| Complex workflows (chaining, fan-out, chord) | Celery | Built-in primitives for task composition |
| Multi-broker (RabbitMQ + Redis + SQS) | Celery | Only option with multi-broker support |
| Enterprise with existing Celery infra | Celery | Migration cost isn't worth it |

The pattern I've settled on: arq for I/O-bound LLM work, RQ for simple sync tasks, and Celery only if I genuinely need its workflow primitives or multi-broker support.

---

## The Bottom Line

If you're already running FastAPI + Redis (which most LLM apps are), arq adds almost zero operational complexity. It's just another async process reading from the same Redis. Compare that to Celery, which wants its own broker, result backend, Beat scheduler, and Flower dashboard.

The LLM ecosystem is I/O-bound by nature. Your tools should reflect that.

What task queue setup are you using for LLM workloads? Have you found Celery worth the overhead, or have you moved to something lighter?

---

References:

[1] ["arq — Job queues and RPC in python with asyncio and redis."](https://arq-docs.helpmanual.io/) Samuel Colvin.  
[2] ["RQ: Simple job queues for Python."](https://python-rq.org/) RQ Project.  
[3] ["Celery — Distributed Task Queue."](https://docs.celeryq.dev/) Celery Project.  
[4] ["Rate Limiting."](https://platform.openai.com/docs/guides/rate-limits) OpenAI.  
[5] ["Anthropic API Rate Limits."](https://docs.anthropic.com/en/api/rate-limits) Anthropic.  
[6] ["FastAPI Background Tasks."](https://fastapi.tiangolo.com/tutorial/background-tasks/) FastAPI.  
[7] ["asyncio — Asynchronous I/O."](https://docs.python.org/3/library/asyncio.html) Python.  
