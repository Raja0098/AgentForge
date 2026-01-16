<template>
  <aside class="node-panel">

    <!-- ================= Header ================= -->
    <h3>📦 Components</h3>

    <!-- ================= Agents ================= -->
    <div class="node-section">
      <h4>🤖 Agents</h4>

      <div
        v-for="agent in store.state.availableNodes.agents"
        :key="agent.type"
        class="node-item"
        :class="{ selected: isSelected(agent, 'agent') }"
        @click="selectNode(agent, 'agent')"
      >
        <span class="node-icon">
          {{ agent.icon || '🤖' }}
        </span>
        <span class="node-name">
          {{ agent.name }}
        </span>
      </div>
    </div>

    <!-- ================= Tools ================= -->
    <div class="node-section">
      <h4>🔧 Tools</h4>

      <div
        v-for="tool in store.state.availableNodes.tools"
        :key="tool.type"
        class="node-item"
        :class="{ selected: isSelected(tool, 'tool') }"
        @click="selectNode(tool, 'tool')"
      >
        <span class="node-icon">
          {{ tool.icon || '🔧' }}
        </span>
        <span class="node-name">
          {{ tool.name }}
        </span>
      </div>
    </div>

  </aside>
</template>


<script setup>
import { useStore } from 'vuex'

const store = useStore()

/* ================= Actions ================= */
const selectNode = (node, category) => {
  store.commit('SET_TEMPLATE', {
    ...node,
    category
  })
}

/* ================= Helpers ================= */
const isSelected = (node, category) => {
  const selected = store.state.selectedTemplate

  return (
    selected &&
    selected.type === node.type &&
    selected.category === category
  )
}
</script>

<style>
/* =====================================================
   NODE PANEL
   ===================================================== */
.node-panel {
  width: 260px;
  background: var(--bg-panel);
  border-right: 1px solid #e5e7eb;
  overflow-y: auto;
  padding: 1.5rem;
}

.node-panel h3 {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

/* =====================================================
   SECTIONS
   ===================================================== */
.node-section {
  margin-bottom: 2rem;
}

.node-section h4 {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.75rem;
}

/* =====================================================
   NODE ITEMS
   ===================================================== */
.node-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;

  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;

  border-radius: 8px;
  border: 2px solid #e5e7eb;

  cursor: pointer;
  transition: all 0.2s ease;
}

.node-item:hover {
  border-color: var(--primary);
  background: #f0f4ff;
}

.node-item.selected {
  border-color: var(--primary);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

/* =====================================================
   CONTENT
   ===================================================== */
.node-icon {
  font-size: 1.5rem;
}

.node-name {
  font-size: 0.9rem;
  font-weight: 500;
}
</style>