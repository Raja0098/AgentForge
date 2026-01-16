<template>
  <div class="app-container">

    <!-- ================= HEADER ================= -->
    <header class="app-header">
      <div class="header-content">

        <!-- Left: Logo + Title -->
        <div class="header-left">
          <div class="logo-section">
            <div class="logo-icon">🤖</div>

            <div>
              <h1>Build Your Own AI Agents</h1>
              <p>Build AI workflows Easily Just Drag and Drop the tools and agents — No code required</p>
            </div>
          </div>
        </div>

        <!-- Right: Actions -->
        <div class="header-actions">
          <button
            class="btn-secondary"
            @click="showWorkflowManager = true"
          >
            <span class="btn-icon">📁</span>
            Workflows
          </button>

          <button
            class="btn-save"
            @click="showSaveDialog = true"
          >
            <span class="btn-icon">💾</span>
            Save
          </button>

          <button
            class="btn-new"
            @click="newWorkflow"
          >
            <span class="btn-icon">➕</span>
            New
          </button>
        </div>

      </div>
    </header>

    <!-- ================= MAIN LAYOUT ================= -->
    <div class="app-main">
      <NodePanel />
      <Canvas />
      <ExecutionPanel />
    </div>

    <!-- ================= SAVE WORKFLOW MODAL ================= -->
    <div
      v-if="showSaveDialog"
      class="modal-overlay"
      @click.self="showSaveDialog = false"
    >
      <div class="modal-content">

        <div class="modal-header">
          <h3>💾 Save Workflow</h3>

          <button
            class="btn-close-modal"
            @click="showSaveDialog = false"
          >
            ✕
          </button>
        </div>

        <input
          v-model="workflowName"
          type="text"
          class="workflow-name-input"
          placeholder="Enter workflow name (e.g., Finance Pipeline)"
          @keyup.enter="saveWorkflowWithName"
        />

        <div class="modal-actions">
          <button
            class="btn-cancel"
            @click="showSaveDialog = false"
          >
            Cancel
          </button>

          <button
            class="btn-confirm"
            @click="saveWorkflowWithName"
          >
            Save
          </button>
        </div>

      </div>
    </div>

    <!-- ================= WORKFLOW MANAGER ================= -->
    <WorkflowManager
      v-if="showWorkflowManager"
      @close="showWorkflowManager = false"
    />

  </div>
</template>


<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'

import NodePanel from './components/NodePanel.vue'
import Canvas from './components/Canvas.vue'
import ExecutionPanel from './components/ExecutionPanel.vue'
import WorkflowManager from './components/WorkflowManager.vue'

const store = useStore()

/* ================= UI STATE ================= */
const showSaveDialog = ref(false)
const showWorkflowManager = ref(false)

/* ================= WORKFLOW NAME ================= */
const workflowName = computed({
  get: () => store.state.workflow.name,
  set: (val) => store.commit('SET_WORKFLOW_NAME', val)
})

/* ================= LIFECYCLE ================= */
onMounted(async () => {
  store.dispatch('loadSavedWorkflows')

  try {
    const res = await fetch('http://127.0.0.1:8000/api/nodes')
    const nodes = await res.json()
    store.commit('SET_AVAILABLE_NODES', nodes)
  } catch (err) {
    console.error('Failed to load nodes:', err)
    alert('⚠️ Failed to connect to backend. Please ensure the server is running.')
  }
})

/* ================= ACTIONS ================= */
const saveWorkflowWithName = () => {
  if (!workflowName.value.trim()) {
    alert('Please enter a workflow name')
    return
  }

  store.dispatch('saveWorkflow')
  showSaveDialog.value = false

  alert(`✅ Workflow "${workflowName.value}" saved!`)
}

const newWorkflow = () => {
  if (store.state.workflow.nodes.length > 0) {
    if (!confirm('Create new workflow? Unsaved changes will be lost.')) {
      return
    }
  }

  store.commit('CLEAR_WORKFLOW')
}
</script>


<style>/* =====================================================
   APP CONTAINER
   ===================================================== */
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fa;
}

/* =====================================================
   HEADER
   ===================================================== */
.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1.5rem 2rem;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* Logo */
.logo-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-icon {
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.app-header h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
}

.app-header p {
  margin: 0.25rem 0 0;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.9);
}

/* Header Actions */
.header-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-icon {
  margin-right: 0.5rem;
}

.btn-save,
.btn-new,
.btn-secondary {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  border: none;
  color: white;
  transition: all 0.3s ease;
}

/* Button variants */
.btn-save {
  background: rgba(16, 185, 129, 0.9);
}

.btn-save:hover {
  background: #10b981;
}

.btn-new {
  background: rgba(59, 130, 246, 0.9);
}

.btn-new:hover {
  background: #3b82f6;
}

.btn-secondary {
  background: rgba(107, 114, 128, 0.9);
}

.btn-secondary:hover {
  background: #6b7280;
}

/* =====================================================
   MAIN LAYOUT
   ===================================================== */
.app-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* =====================================================
   SAVE MODAL
   ===================================================== */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  min-width: 450px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
  border-bottom: 2px solid #e5e7eb;
}

.workflow-name-input {
  width: calc(100% - 4rem);
  margin: 1.5rem 2rem;
  padding: 0.85rem 1rem;
  border-radius: 10px;
  border: 2px solid #e5e7eb;
  font-size: 1rem;
}

.workflow-name-input:focus {
  outline: none;
  border-color: #667eea;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem 2rem;
  background: #f9fafb;
  border-top: 2px solid #e5e7eb;
}
</style>
