---
name: bundle-optimizer
description: Optimize JavaScript/CSS bundle sizes via tree shaking, code splitting, lazy loading, and dependency auditing in Vite, Webpack, or Next.js.
argument-hint: "[bundler | target-framework]"
metadata:
  origin: VEX
---

# Bundle Optimizer

Use this skill when an application loads slowly, exceeds performance budgets, or ships too much JavaScript to the client.

## Triggers

- User reports slow initial load time or poor Core Web Vitals (LCP, INP).
- Webpack/Vite/Next.js warns about chunk size exceeding limits.
- Task asks to "reduce bundle size", "optimize chunks", or "tree shake".
- Lighthouse score for Performance is low due to JS execution.

## Inputs To Inspect

- `vite.config.ts`, `next.config.js`, `webpack.config.js`.
- `package.json` to audit large dependencies (e.g., Moment.js, Lodash).
- Entry points (`main.tsx`, `_app.tsx`) checking for heavy global imports.
- Routing configuration (checking for route-based code splitting).

## Optimization Strategy

1. Analyze current bundle to find the largest offenders.
2. Replace heavy legacy libraries with modern, tree-shakeable alternatives.
3. Implement route-level code splitting so users only load what they see.
4. Implement component-level lazy loading for heavy UI (charts, modals, rich text editors).
5. Extract vendor code into separate chunks for better caching.

## 1. Bundle Analysis

Do not optimize blind. Generate a map first.

**Vite:**
```bash
npm i -D rollup-plugin-visualizer
```
```ts
import { visualizer } from 'rollup-plugin-visualizer';
export default defineConfig({
  plugins: [visualizer({ open: true })]
});
```

**Next.js:**
```bash
ANALYZE=true npm run build
```

## 2. Library Replacements

Identify and replace monolithic imports:

- ❌ `import _ from 'lodash'` → ✅ `import get from 'lodash/get'` or native JS
- ❌ `import moment from 'moment'` → ✅ `date-fns` or `dayjs`
- ❌ `import * as Three from 'three'` → ✅ `import { Scene } from 'three'`
- ❌ CommonJS imports → ✅ ES Module imports (for tree shaking)

## 3. Code Splitting & Lazy Loading

**React (Vite/CRA):**
```tsx
import { lazy, Suspense } from 'react';

// Instead of: import HeavyChart from './HeavyChart';
const HeavyChart = lazy(() => import('./HeavyChart'));

function Dashboard() {
  return (
    <Suspense fallback={<Spinner />}>
      <HeavyChart data={data} />
    </Suspense>
  );
}
```

**Next.js:**
```tsx
import dynamic from 'next/dynamic';

const HeavyChart = dynamic(() => import('./HeavyChart'), {
  loading: () => <Spinner />,
  ssr: false // Optional: skip SSR if it relies on window
});
```

## 4. Vendor Chunking (Vite)

Separate third-party code so app updates don't bust the framework cache.

```ts
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          charting: ['chart.js', 'recharts'],
        }
      }
    }
  }
});
```

## Common Pitfalls

- Exporting a default object containing all utilities breaks tree shaking. Export individual functions instead.
- Over-chunking: creating hundreds of tiny 1kb chunks harms performance more than one 50kb chunk due to network overhead.
- Lazy loading above-the-fold content (like the hero image or primary text) ruins LCP. Only lazy load below the fold or behind interactions.
- Importing server-only modules into client components (Next.js), bloating the client bundle with Node.js polyfills.

## Done Criteria

- Bundle visualization confirms heavy libraries are isolated or removed.
- Route navigation loads separate JS chunks.
- Warning thresholds in bundler output pass.
- Above-the-fold content loads synchronously without suspense waterfalls.
