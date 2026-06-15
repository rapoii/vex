---
name: react-patterns
description: Use modern React component, hook, state, data-fetching, and accessibility patterns.
argument-hint: "[scope | file | goal]"
metadata:
  origin: VEX
  category: reference
  triggers: ["React components/hooks", "Client/server state design", "JSX review"]
---

# React Patterns

Modern patterns for building robust React applications.

## When to Activate

- Creating or modifying React components.
- Designing state management solutions.
- Data fetching logic.
- Reviewing JSX code.

## Core Principles

### 1. Component Composition
Prefer composition over configuration (huge prop lists).

**Bad (Configuration):**
```tsx
<Dialog title="Warning" content="Delete?" onConfirm={handleDelete} showCancel={true} />
```

**Good (Composition):**
```tsx
<Dialog>
  <DialogHeader>Warning</DialogHeader>
  <DialogContent>Delete?</DialogContent>
  <DialogActions>
    <Button variant="ghost">Cancel</Button>
    <Button variant="danger" onClick={handleDelete}>Confirm</Button>
  </DialogActions>
</Dialog>
```

### 2. State Management Separation
Distinguish between UI State (modals, dropdowns) and Server State (database data).

- **UI State**: `useState`, `useReducer`, Zustand, Context.
- **Server State**: React Query, SWR, Apollo. Do NOT store server data in global Redux/Zustand stores unnecessarily.

### 3. Custom Hooks for Logic Extraction
Keep components focused on rendering. Move business logic to custom hooks.

```tsx
// ❌ Bad: Logic inside component
function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetch('/api/users').then(res => res.json()).then(data => {
      setUsers(data);
      setLoading(false);
    });
  }, []);
  
  // render...
}

// ✅ Good: Logic in hook
function useUsers() {
  // Can use React Query here internally
  return useQuery('users', () => fetch('/api/users').then(res => res.json()));
}

function UserList() {
  const { data: users, isLoading } = useUsers();
  // render...
}
```

### 4. React Server Components (RSC) (Next.js App Router)
Understand the boundary between Client and Server components.
- Default to Server Components (no `"use client"`).
- Add `"use client"` only when needing interactivity (onClick, useState, browser APIs).
- Pass data from Server to Client via props.

### 5. Dependency Arrays in `useEffect` / `useCallback`
Always include all external variables used inside the effect.

```tsx
// ❌ Bad: Missing dependency
useEffect(() => {
  fetchData(userId);
}, []); // Warning: React Hook useEffect has a missing dependency: 'userId'

// ✅ Good
useEffect(() => {
  fetchData(userId);
}, [userId]);
```

## Common Pitfalls

- **Over-using `useEffect`**: Deriving state or responding to user events doesn't need an effect. If you can calculate it during render, do it. If it's a click handler, put logic in the handler.
- **Stale Closures**: Forgetting dependencies in `useCallback` or `useEffect` causing old state values to be used.
- **Prop Drilling**: Passing props down 5 levels. Use Context or Component Composition.
- **Missing Keys**: Not providing stable `key` props in `.map()`. Avoid using array indices as keys if the list can change.

## Verification

- Does it render correctly without warnings in the console?
- Do interactive elements respond properly?
- Is there unnecessary re-rendering? (Use React DevTools Profiler).
