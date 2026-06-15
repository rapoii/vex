const fs = require('fs');

const content = `---
name: vue-patterns
description: Build scalable Vue 3 apps using Composition API, Pinia, Vue Router, and clean architecture.
argument-hint: "[scope | file | goal]"
metadata:
  origin: VEX
  category: reference
---

# Vue Patterns

Actionable steps and concrete examples for building robust Vue 3 applications.

## When to Activate
- Creating or modifying Vue components.
- Designing state management with Pinia.
- Handling Vue reactivity.

## Core Principles

### 1. Composition API First
Prefer \`<script setup>\` and the Composition API over the Options API for better TypeScript support and logic reuse.

**Bad (Options API):**
\`\`\`vue
<script>
export default {
  data() { return { count: 0 } },
  methods: { increment() { this.count++ } }
}
</script>
\`\`\`

**Good (Composition API):**
\`\`\`vue
<script setup>
import { ref } from 'vue';
const count = ref(0);
const increment = () => count.value++;
</script>
\`\`\`

### 2. State Management (Pinia)
Use Pinia instead of Vuex. Keep stores focused and modular.

\`\`\`typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const isLoggedIn = computed(() => !!user.value)
  
  async function login(credentials) {
    user.value = await api.login(credentials)
  }

  return { user, isLoggedIn, login }
})
\`\`\`

### 3. Extracting Composables
Move reusable logic out of components into composables (custom hooks).

\`\`\`typescript
// useFetch.js
import { ref, isRef, unref, watchEffect } from 'vue'

export function useFetch(url) {
  const data = ref(null)
  const error = ref(null)

  watchEffect(async () => {
    data.value = null
    error.value = null
    try {
      const res = await fetch(unref(url))
      data.value = await res.json()
    } catch (e) {
      error.value = e
    }
  })

  return { data, error }
}
\`\`\`

## Common Pitfalls
- **Losing Reactivity**: Destructuring props without \`toRefs\` or using \`ref\` for objects instead of \`reactive\` incorrectly.
- **Mutating Props**: Attempting to modify a prop directly inside a child component. Always emit an event.
- **Memory Leaks**: Forgetting to clean up event listeners inside \`onUnmounted\`.

## Verification Checklist
- [ ] Logic is extracted to composables if reused.
- [ ] State mutations happen in Pinia stores, not randomly in components.
- [ ] Reactivity is preserved when destructuring.
`;

fs.writeFileSync('C:/Users/rafi/vex-project/skills/reference/vue-patterns/SKILL.md', content);
console.log('Updated vue-patterns');
