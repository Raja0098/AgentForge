<template>
  <div
    class="modal-overlay"
    @click.self="$emit('close')"
  >
    <div class="manager-content">

      <!-- ================= Header ================= -->
      <div class="manager-header">
        <h2>📁 Saved Workflows</h2>

        <button
          class="btn-close"
          @click="$emit('close')"
        >
          ✕
        </button>
      </div>

      <!-- ================= Empty State ================= -->
      <div
        v-if="workflows.length === 0"
        class="empty-state"
      >
        <div class="empty-icon">📭</div>
        <p>No saved workflows yet</p>
        <small>
          Create and save your first workflow to see it here
        </small>
      </div>

      <!-- ================= Workflow List ================= -->
      <div
        v-else
        class="workflows-list"
      >
        <div
          v-for="workflow in workflows"
          :key="workflow.id"
          class="workflow-card"
        >
          <!-- Workflow Info -->
          <div class="workflow-info">
            <h3>{{ workflow.name }}</h3>

            <div class="workflow-meta">
              <span>{{ workflow.nodes.length }} nodes</span>
              <span>{{ workflow.connections.length }} connections</span>
            </div>

            <small
              v-if="workflow.createdAt"
              class="workflow-date"
            >
              Created: {{ formatDate(workflow.createdAt) }}
            </small>
          </div>

          <!-- Workflow Actions -->
          <div class="workflow-actions">
            <button
              class="btn-load"
              @click="loadWorkflow(workflow.id)"
            >
              📂 Load
            </button>

            <button
              class="btn-run-saved"
              @click="runWorkflow(workflow.id)"
            >
              ▶ Run
            </button>

            <button
              class="btn-delete-wf"
              @click="deleteWorkflow(workflow.id)"
            >
              🗑️
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>


<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'

const store = useStore()
const emit = defineEmits(['close'])

/* ================= State ================= */
const workflows = computed(() => store.state.savedWorkflows)

/* ================= Actions ================= */
const loadWorkflow = (workflowId) => {
  store.dispatch('loadWorkflow', workflowId)
  emit('close')
}

const runWorkflow = async (workflowId) => {
  store.dispatch('loadWorkflow', workflowId)

  // Allow state to settle before execution
  await new Promise(resolve => setTimeout(resolve, 100))

  store.dispatch('executeWorkflow')
  emit('close')
}

const deleteWorkflow = (workflowId) => {
  if (confirm('Delete this workflow permanently?')) {
    store.dispatch('deleteWorkflow', workflowId)
  }
}

/* ================= Helpers ================= */
const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>


<style scoped>/* =====================================================
   MODAL OVERLAY
   ===================================================== */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* =====================================================
   MODAL CONTENT
   ===================================================== */
.manager-content {
  background: white;
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  border-radius: 20px;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* =====================================================
   HEADER
   ===================================================== */
.manager-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2rem;
  border-bottom: 2px solid #e5e7eb;
}

.manager-header h2 {
  margin: 0;
  font-size: 1.5rem;
}

/* Close Button */
.btn-close {
  width: 36px;
  height: 36px;
  background: #fee2e2;
  color: #dc2626;
  border: none;
  border-radius: 8px;
  font-size: 1.25rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-close:hover {
  background: #fca5a5;
}

/* =====================================================
   EMPTY STATE
   ===================================================== */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #9ca3af;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

/* =====================================================
   WORKFLOW LIST
   ===================================================== */
.workflows-list {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.workflow-card {
  display: flex;
  justify-content: space-between;
  align-items: center;

  padding: 1.5rem;
  margin-bottom: 1rem;

  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
  border-radius: 12px;
  border: 2px solid #e5e7eb;

  transition: all 0.2s ease;
}

.workflow-card:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

/* =====================================================
   WORKFLOW INFO
   ===================================================== */
.workflow-info h3 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  color: #111827;
}

.workflow-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.workflow-date {
  font-size: 0.75rem;
  color: #9ca3af;
}

/* =====================================================
   ACTION BUTTONS
   ===================================================== */
.workflow-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-load {
  background: #667eea;
  color: white;
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
}

.btn-load:hover {
  background: #5568d3;
}

.btn-run-saved {
  background: #10b981;
  color: white;
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
}

.btn-run-saved:hover {
  background: #059669;
}

.btn-delete-wf {
  background: #fee2e2;
  color: #dc2626;
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  cursor: pointer;
}

.btn-delete-wf:hover {
  background: #fca5a5;
}

</style>
