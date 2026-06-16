---
name: performance-audit
description: Identify and resolve performance bottlenecks via profiling, memory leak detection, render optimization, and Lighthouse audits.
argument-hint: "[audit-target | performance-metric]"
metadata:
  origin: VEX
---

# Performance Audit

Use this skill to diagnose slow page loads, janky animations, high memory usage, or sluggish backend endpoints before rewriting code blindly.

## Triggers

- User complains about "slow", "laggy", or "freezing" application.
- Lighthouse scores (Core Web Vitals) are failing.
- Application crashes with Out Of Memory (OOM) errors.
- Task asks to profile, benchmark, or audit performance.

## Inputs To Inspect

- `package.json` for performance tooling (`clinic`, `0x`, `lighthouse`).
- React/Vue components suspected of excessive re-rendering.
- Backend routes lacking pagination, caching, or db indexes.
- Image assets lacking optimization or sizing.

## Audit Strategy

1. **Measure First**: Never guess the bottleneck. Generate a profile.
2. **Frontend Metrics**: Focus on LCP (Largest Contentful Paint), CLS (Cumulative Layout Shift), and INP (Interaction to Next Paint).
3. **Backend Metrics**: Focus on response time, DB query counts (N+1), and memory heap size.
4. **Fix**: Apply targeted fixes based on the profile data.
5. **Verify**: Measure again to prove the fix worked.

## Frontend: React Render Optimization

Identify components that render too often (use React Profiler).

**Fixing object reference churn:**
```tsx
// ❌ Bad: Creates new object/function every render, busting child memoization
function Parent() {
  const config = { theme: 'dark' };
  const handleClick = () => console.log('clicked');
  return <HeavyChild config={config} onClick={handleClick} />;
}

// ✅ Good: Stable references
function Parent() {
  const config = useMemo(() => ({ theme: 'dark' }), []);
  const handleClick = useCallback(() => console.log('clicked'), []);
  return <HeavyChild config={config} onClick={handleClick} />;
}
```

## Frontend: Core Web Vitals

- **LCP (Loading)**: Preload the hero image. Defer non-critical JS.
- **CLS (Stability)**: Set explicit `width` and `height` on all `<img>` and skeleton loaders.
- **INP (Responsiveness)**: Yield to the main thread during heavy JS tasks using `setTimeout` or Web Workers.

## Backend: Node.js Profiling

Find CPU bottlenecks using Node's built-in profiler:

```bash
# 1. Run app with profiler
node --prof app.js

# 2. Apply load (e.g., using autocannon)
npx autocannon -c 100 -d 10 http://localhost:3000

# 3. Process the log file
node --prof-process isolate-0xnnnnnnnnnnnn-v8.log > processed.txt
```

Find memory leaks by comparing heap snapshots:

```javascript
// Add to your app temporarily to trigger snapshots
const v8 = require('v8');
app.get('/debug/snapshot', (req, res) => {
  const fileName = `/tmp/${Date.now()}.heapsnapshot`;
  v8.writeHeapSnapshot(fileName);
  res.send(`Snapshot saved: ${fileName}`);
});
```

## Database / API Bottlenecks

- Add pagination (`LIMIT` / `OFFSET` or cursors) to unbounded list queries.
- Add caching (Redis, or HTTP Cache-Control headers) to slow, infrequently changing data.
- Ensure heavy operations happen asynchronously via background jobs (Redis/BullMQ) rather than blocking the HTTP response.

## Common Pitfalls

- Profiling in development mode. Development builds contain heavy debug code. Always profile production builds.
- Optimizing code that only accounts for 1% of the total execution time.
- Adding `React.memo` everywhere. Memoization has a cost; only apply it to heavy components or lists.
- Using `console.time` for micro-benchmarks instead of proper statistical tools.

## Done Criteria

- Bottleneck is identified with concrete profiling data.
- Fix targets the specific bottleneck.
- Post-fix profiling shows a measurable improvement.
- Production build succeeds and maintains functionality.
