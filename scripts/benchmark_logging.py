import os, time, sqlite3, argparse, statistics, threading

def bench_once(n: int, pooled: bool, use_threads: int = 1):
    os.environ["CODEX_SQLITE_POOL"] = "1" if pooled else "0"
    from codex.db.sqlite_patch import auto_enable_from_env as _auto
    _auto()

    db = os.getenv("CODEX_SQLITE_DB","codex_bench.sqlite3")
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS bench_log(id INTEGER PRIMARY KEY, ts REAL, msg TEXT)")
    conn.commit(); cur.close()
    if not pooled:
        conn.close()

    def worker(start_i, end_i):
        for i in range(start_i, end_i):
            c = sqlite3.connect(db)
            cu = c.cursor()
            cu.execute("INSERT INTO bench_log(ts,msg) VALUES(?,?)", (time.time(), f"m{i}"))
            c.commit()
            cu.close()
            if not pooled:
                c.close()

    t0 = time.perf_counter()
    if use_threads > 1:
        threads = []
        step = n // use_threads
        for t in range(use_threads):
            a = t*step
            b = n if t==use_threads-1 else (t+1)*step
            th = threading.Thread(target=worker, args=(a,b))
            th.start(); threads.append(th)
        for th in threads: th.join()
    else:
        worker(0,n)
    t1 = time.perf_counter()
    return t1 - t0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=5000)
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--rounds", type=int, default=3)
    args = ap.parse_args()

    base = [bench_once(args.N, pooled=False, use_threads=args.threads) for _ in range(args.rounds)]
    pool = [bench_once(args.N, pooled=True,  use_threads=args.threads) for _ in range(args.rounds)]

    import math
    def thr(n, t): return n/t
    Tb = [thr(args.N, x) for x in base]
    Tp = [thr(args.N, x) for x in pool]

    print("BASE seconds:", base, "median=", statistics.median(base))
    print("POOL seconds:", pool, "median=", statistics.median(pool))
    print("BASE thr:", Tb, "median=", statistics.median(Tb))
    print("POOL thr:", Tp, "median=", statistics.median(Tp))
    imp = (statistics.median(Tp)-statistics.median(Tb)) / max(1e-9, statistics.median(Tb)) * 100.0
    print(f"IMPROVEMENT %: {imp:.2f}")

if __name__ == "__main__":
    main()
