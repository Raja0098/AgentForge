<template>
  <aside class="execution-panel">

    <!-- ================= Header ================= -->
    <div class="panel-header">
      <h3>⚡ Execution</h3>
      <span
        v-if="executionResult?.logs"
        class="execution-time"
      >
        {{ getTotalTime() }}
      </span>
    </div>

    <!-- ================= Run Button ================= -->
    <button
      class="btn-run"
      :class="{ executing: isExecuting }"
      :disabled="isExecuting || !hasNodes"
      @click="runWorkflow"
    >
      {{ isExecuting ? '⏳ Running...' : '▶ Run Workflow' }}
    </button>

    <!-- ================= Results ================= -->
    <div v-if="executionResult" class="results-container">

      <!-- -------- Success -------- -->
      <template
        v-if="executionResult.status === 'success' && executionResult.result"
      >
        <div
          v-for="(output, nodeId) in executionResult.result"
          :key="nodeId"
          class="result-card"
          :class="{ error: !output.success }"
        >
          <div class="result-header">
            <span class="node-name">
              {{ getNodeName(nodeId) }}
            </span>

            <span
              class="status-badge"
              :class="{ success: output.success, error: !output.success }"
            >
              {{ output.success ? '✓' : '✗' }}
            </span>
          </div>

          <div class="result-body">
            <div
              v-if="output.success"
              class="output-text"
            >
              {{ output.data }}
            </div>

            <div
              v-else
              class="error-text"
            >
              ❌ {{ output.error }}
            </div>
          </div>

          <div
            v-if="output.success"
            class="result-meta"
          >
            <span
              v-if="output.node_type"
              class="meta-tag"
            >
              {{ output.node_type }}
            </span>

            <span
              v-if="output.original_length"
              class="meta-info"
            >
              {{ output.original_length }} → {{ output.summary_length }} chars
            </span>
          </div>
        </div>

        <!-- -------- Logs -------- -->
        <div
          v-if="executionResult.logs"
          class="logs-section"
        >
          <h4>📊 Execution Logs</h4>

          <div class="logs-list">
            <div
              v-for="(log, index) in executionResult.logs"
              :key="index"
              class="log-item"
            >
              <span
                v-if="log.node"
                class="log-node"
              >
                {{ log.node }}
              </span>

              <span
                v-if="log.duration_ms"
                class="log-time"
              >
                {{ log.duration_ms }}ms
              </span>

              <span
                v-if="log.event === 'complete'"
                class="log-complete"
              >
                ✅ Total: {{ log.total_ms }}ms
              </span>
            </div>
          </div>
        </div>
      </template>

      <!-- -------- Error -------- -->
      <template v-else-if="executionResult.status === 'error'">
        <div class="error-state">
          <div class="error-icon">⚠️</div>
          <div class="error-message">
            {{ executionResult.message }}
          </div>
        </div>
      </template>

    </div>

    <!-- ================= Placeholder ================= -->
    <div v-else class="result-placeholder">
      <div class="placeholder-icon">🚀</div>
      <p>Add nodes and click Run to see results</p>
    </div>

  </aside>
</template>


<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'

const store = useStore()

/* ================= State ================= */
const executionResult = computed(() => store.state.executionResult)
const isExecuting = computed(() => store.state.isExecuting)
const hasNodes = computed(() => store.state.workflow.nodes.length > 0)

/* ================= Actions ================= */
const runWorkflow = () => {
  store.dispatch('executeWorkflow')
}

/* ================= Helpers ================= */
const getNodeName = (nodeId) => {
  const node = store.state.workflow.nodes.find(n => n.id === nodeId)
  return node ? node.name : nodeId
}

const getTotalTime = () => {
  const logs = executionResult.value?.logs
  if (!logs) return ''

  const completed = logs.find(log => log.event === 'complete')
  return completed ? `${completed.total_ms}ms` : ''
}
</script>


<style scoped>
.execution-panel {
  width: 340px;
  background: #f9fafb;
  border-left: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  padding: 1.5rem 1.5rem 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
}

.execution-time {
  font-size: 0.75rem;
  color: #6b7280;
  background: #e5e7eb;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.btn-run {
  margin: 1rem 1.5rem;
  width: calc(100% - 3rem);
  padding: 0.85rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-run:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.btn-run:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-run.executing {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.results-container {
  flex: 1;
  overflow-y: auto;
  padding: 0 1.5rem 1.5rem;
}

.result-card {
  background: white;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  margin-bottom: 1rem;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.result-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.result-card.error {
  border-color: #fca5a5;
  background: #fef2f2;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.node-name {
  font-weight: 600;
  font-size: 0.85rem;
  color: #374151;
}

.status-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
}

.status-badge.success {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.error {
  background: #fee2e2;
  color: #991b1b;
}

.result-body {
  padding: 1rem;
}

.output-text {
  font-size: 0.85rem;
  line-height: 1.6;
  color: #374151;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 300px;
  overflow-y: auto;
}

.error-text {
  color: #dc2626;
  font-size: 0.85rem;
}

.result-meta {
  padding: 0.5rem 1rem;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.meta-tag {
  font-size: 0.7rem;
  padding: 0.2rem 0.5rem;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 4px;
  font-weight: 500;
}

.meta-info {
  font-size: 0.7rem;
  color: #6b7280;
}

.logs-section {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 2px solid #e5e7eb;
}

.logs-section h4 {
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: #374151;
}

.logs-list {
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  padding: 0.75rem;
}

.log-item {
  font-size: 0.75rem;
  padding: 0.4rem 0;
  color: #6b7280;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f3f4f6;
}

.log-item:last-child {
  border-bottom: none;
}

.log-node {
  font-weight: 500;
  color: #374151;
}

.log-time {
  background: #f3f4f6;
  padding: 0.15rem 0.4rem;
  border-radius: 3px;
  font-family: monospace;
}

.log-complete {
  color: #059669;
  font-weight: 600;
}

.error-state {
  text-align: center;
  padding: 2rem 1rem;
  background: white;
  border-radius: 10px;
  border: 1px solid #fca5a5;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-message {
  color: #dc2626;
  font-size: 0.9rem;
  line-height: 1.5;
}

.result-placeholder {
  text-align: center;
  padding: 3rem 1rem;
  color: #9ca3af;
}

.placeholder-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.result-placeholder p {
  font-size: 0.9rem;
  margin: 0;
}

/* Scrollbar styling */
.results-container::-webkit-scrollbar {
  width: 6px;
}

.results-container::-webkit-scrollbar-track {
  background: #f3f4f6;
}

.results-container::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.results-container::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

.output-text::-webkit-scrollbar {
  width: 4px;
}

.output-text::-webkit-scrollbar-track {
  background: #f9fafb;
}

.output-text::-webkit-scrollbar-thumb {
  background: #e5e7eb;
  border-radius: 2px;
}
</style>
