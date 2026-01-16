<template>
  <div class="canvas-container">
    <div ref="canvas" class="canvas" @click="addNode">

      <!-- ================= Workflow Header ================= -->
      <div class="workflow-name-badge">
        <span class="badge-icon">📋</span>
        {{ store.state.workflow.name }}
      </div>

      <div v-if="selectedTemplate" class="canvas-hint">
        <span class="hint-icon">👆</span>
        Click to add <strong>{{ selectedTemplate.name }}</strong>
      </div>

      <!-- ================= Connections Layer ================= -->
      <svg class="connections-layer">
        <defs>
          <marker
            id="arrowhead"
            markerWidth="12"
            markerHeight="12"
            refX="11"
            refY="6"
            orient="auto"
          >
            <polygon points="0 0, 12 6, 0 12" fill="#667eea" />
          </marker>
        </defs>

        <line
          v-for="(conn, i) in connections"
          :key="i"
          class="connection-line"
          marker-end="url(#arrowhead)"
          :x1="getConnectionPoints(conn).x1"
          :y1="getConnectionPoints(conn).y1"
          :x2="getConnectionPoints(conn).x2"
          :y2="getConnectionPoints(conn).y2"
        />
      </svg>

      <!-- ================= Nodes ================= -->
      <div
        v-for="(node, index) in nodes"
        :key="node.id"
        class="flowchart-node"
        :class="getNodeClass(node)"
        :style="{ left: centerX + 'px', top: getNodeY(index) + 'px' }"
      >

        <!-- Node Header -->
        <div class="flowchart-node-header">
          <span class="node-icon">{{ getNodeIcon(node) }}</span>
          <span class="node-title">{{ node.name }}</span>

          <button
            v-if="node.subtype !== 'input' && node.subtype !== 'output'"
            class="btn-node-delete"
            @click.stop="deleteNode(node.id)"
          >
            ✕
          </button>
        </div>

        <!-- ================= Node Body ================= -->
        <div class="flowchart-node-body">

          <!-- INPUT NODE -->
          <template v-if="node.subtype === 'input'">

            <div class="config-field">
              <label class="input-label">📋 Input Type</label>
              <select
                class="flowchart-select"
                :value="node.config.input_type || 'text'"
                @change="updateConfig(node.id, 'input_type', $event.target.value)"
              >
                <option value="text">✏️ Text</option>
                <option value="url">🔗 URL</option>
                <option value="file">📄 File</option>
              </select>
            </div>

            <div
              v-if="(node.config.input_type || 'text') === 'text'"
              class="config-field"
            >
              <label class="input-label">Text</label>
              <textarea
                class="flowchart-textarea"
                rows="3"
                placeholder="Enter your text..."
                :value="node.config.value || ''"
                @input="updateConfig(node.id, 'value', $event.target.value)"
              />
            </div>

            <div v-if="node.config.input_type === 'url'" class="config-field">
              <label class="input-label">URL</label>
              <input
                type="url"
                class="flowchart-input"
                placeholder="https://example.com"
                :value="node.config.value || ''"
                @input="updateConfig(node.id, 'value', $event.target.value)"
              />
            </div>

            <div v-if="node.config.input_type === 'file'" class="config-field">
              <label class="input-label">Upload File</label>

              <div class="file-upload-zone">
                <input
                  type="file"
                  class="file-input-hidden"
                  :id="`file-${node.id}`"
                  accept=".pdf,.jpg,.jpeg,.png"
                  @change="handleFileUpload(node.id, $event)"
                />

                <label
                  class="file-upload-label"
                  :for="`file-${node.id}`"
                >
                  <span class="upload-icon">📤</span>
                  <span v-if="!node.config.file_name">
                    Choose PDF or Image
                  </span>
                  <span v-else class="file-name">
                    {{ node.config.file_name }}
                  </span>
                </label>
              </div>
            </div>
          </template>

          <!-- LLM NODE -->
          <template v-else-if="node.subtype === 'llm'">
            <div class="config-field">
              <label class="input-label">Prompt</label>
              <textarea
                class="flowchart-textarea"
                rows="2"
                placeholder="Enter prompt..."
                :value="node.config.prompt || ''"
                @input="updateConfig(node.id, 'prompt', $event.target.value)"
              />
            </div>

            <div class="config-field">
              <label class="input-label">Description</label>
              <input
                class="flowchart-input"
                type="text"
                placeholder="Describe what this does..."
                :value="node.config.description || ''"
                @input="updateConfig(node.id, 'description', $event.target.value)"
              />
            </div>

            <div class="config-field">
              <label class="input-label">Execution Mode</label>
              <select
                class="flowchart-select"
                :value="node.config.execution_mode || 'user_prompt'"
                @change="updateConfig(node.id, 'execution_mode', $event.target.value)"
              >
                <option value="user_prompt">User Prompt</option>
                <option value="system_prompt">System Prompt</option>
                <option value="combined">Combined</option>
              </select>
            </div>
          </template>

          <!-- WEB SEARCH NODE -->
          <template v-else-if="node.subtype === 'web_search'">
            <div class="auto-process">
              <span class="auto-icon">🔍</span>
              <span>Searches the web automatically</span>
            </div>
          </template>

          <!-- OUTPUT NODE -->
          <template v-else-if="node.subtype === 'output'">
            <div class="auto-process output">
              <span class="auto-icon">✅</span>
              <span>Final workflow output</span>
            </div>
          </template>

          <!-- DEFAULT NODE -->
          <template v-else>
            <div class="auto-process">
              <span class="auto-icon">⚙️</span>
              <span>Auto-processes previous output</span>
            </div>
          </template>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useStore } from 'vuex'

const store = useStore()
const canvas = ref(null)

const nodes = computed(() => store.state.workflow.nodes)
const connections = computed(() => store.state.workflow.connections)
const selectedTemplate = computed(() => store.state.selectedTemplate)

/* ================= Layout Constants ================= */
const NODE_WIDTH = 380
const NODE_HEIGHT = 280  // Fixed height for all nodes
const GAP = 80
const START_Y = 120

const centerX = computed(() => {
  if (!canvas.value) return 0
  return canvas.value.clientWidth / 2 - NODE_WIDTH / 2
})

const getNodeY = (index) =>
  START_Y + index * (NODE_HEIGHT + GAP)

/* ================= Helpers ================= */
const getNodeIcon = (node) => ({
  input: '📥',
  output: '📤',
  llm: '🤖',
  summarizer: '📝',
  guardrail: '🛡️',
  web_search: '🔍'
}[node.subtype] || '⚙️')

const getNodeClass = (node) => ({
  'node-input': node.subtype === 'input',
  'node-output': node.subtype === 'output',
  'node-llm': node.subtype === 'llm',
  'node-tool': node.type === 'tool'
})

const getConnectionPoints = (conn) => {
  const from = nodes.value.findIndex(n => n.id === conn.source)
  const to = nodes.value.findIndex(n => n.id === conn.target)

  if (from === -1 || to === -1) {
    return { x1: 0, y1: 0, x2: 0, y2: 0 }
  }

  const x = centerX.value + NODE_WIDTH / 2
  return {
    x1: x,
    y1: getNodeY(from) + NODE_HEIGHT,
    x2: x,
    y2: getNodeY(to)
  }
}

/* ================= Actions ================= */
const addNode = async () => {
  if (!selectedTemplate.value) return

  // Auto-add Input node
  if (nodes.value.length === 0) {
    store.commit('ADD_NODE', {
      id: 'input_node',
      type: 'tool',
      subtype: 'input',
      name: 'Input',
      position: null,
      config: { value: '' }
    })
  }

  // Capture previous node BEFORE adding new one
  const previousNode = nodes.value[nodes.value.length - 1]

  const newNode = {
    id: `node_${Date.now()}`,
    type: selectedTemplate.value.category || selectedTemplate.value.type,
    subtype: selectedTemplate.value.type,
    name: selectedTemplate.value.name,
    position: null,
    config: {}
  }

  store.commit('ADD_NODE', newNode)

  // ⏳ Wait for DOM to update
  await nextTick()

  // Connect after DOM is ready
  if (previousNode) {
    store.commit('ADD_CONNECTION', {
      source: previousNode.id,
      target: newNode.id
    })
  }

  store.dispatch('saveWorkflow')
}

const updateConfig = (nodeId, key, value) => {
  store.commit('UPDATE_NODE_CONFIG', { nodeId, key, value })
  store.dispatch('saveWorkflow')
}

const deleteNode = (id) => {
  if (confirm('Delete this node?')) {
    store.commit('DELETE_NODE', id)
    store.dispatch('saveWorkflow')
  }
}

const handleFileUpload = async (nodeId, event) => {
  const file = event.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  try {
    const res = await fetch('http://127.0.0.1:8000/api/upload', {
      method: 'POST',
      body: formData
    })

    const result = await res.json()

    if (!result.success) throw new Error(result.error)

    updateConfig(nodeId, 'value', result.file_path)
    updateConfig(nodeId, 'file_name', file.name)

    alert(`✅ File uploaded: ${file.name}`)
  } catch (err) {
    console.error(err)
    alert('❌ File upload failed')
  }
}
</script>

<style>
/* =====================================================
   CANVAS LAYOUT
   ===================================================== */
.canvas-container {
  flex: 1;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  overflow: auto;
  position: relative;
}

.canvas {
  width: 100%;
  min-height: 2000px;
  position: relative;
  padding: 2rem 0 150px 0;
}

/* =====================================================
   WORKFLOW HEADER
   ===================================================== */
.workflow-name-badge {
  position: absolute;
  top: 1.5rem;
  left: 1.5rem;
  background: #ffffff;
  padding: 0.75rem 1.25rem;
  border-radius: 14px;
  font-weight: 600;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border: 2px solid #e5e7eb;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  z-index: 20;
}

.badge-icon {
  font-size: 1.1rem;
}

/* =====================================================
   ADD NODE HINT
   ===================================================== */
.canvas-hint {
  position: sticky;
  top: 1.5rem;
  margin: 0 auto;
  width: fit-content;
  padding: 0.85rem 1.75rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 25;
  animation: pulse 2s ease-in-out infinite;
}

.hint-icon {
  font-size: 1.25rem;
  animation: bounce 1.2s infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4); }
  50% { box-shadow: 0 12px 30px rgba(102, 126, 234, 0.6); }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

/* =====================================================
   CONNECTIONS (ARROWS)
   ===================================================== */
.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  min-height: 2000px;
  pointer-events: none;
  z-index: 1;
}

.connection-line {
  stroke: #667eea;
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
  marker-end: url(#arrowhead);
}

/* =====================================================
   FLOWCHART NODES - FIXED SIZE
   ===================================================== */
.flowchart-node {
  position: absolute;
  width: 380px;
  height: 280px;
  background: white;
  border: 3px solid #cbd5e1;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  z-index: 10;
  display: flex;
  flex-direction: column;
}

.flowchart-node:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
}

/* =====================================================
   NODE TYPES (SHAPES + COLORS)
   ===================================================== */

/* Input */
.node-input {
  border-color: #10b981;
  border-radius: 20px;
  background: linear-gradient(to bottom, #ffffff, #ecfdf5);
}

/* LLM / Agent */
.node-llm,
.node-agent {
  border-color: #8b5cf6;
  border-radius: 14px;
  background: linear-gradient(to bottom, #ffffff, #faf5ff);
}

/* Tool */
.node-tool {
  border-color: #f59e0b;
  border-radius: 10px;
  background: linear-gradient(to bottom, #ffffff, #fffbeb);
}

/* Output */
.node-output {
  border-color: #3b82f6;
  border-radius: 6px;
  border-width: 3px;
  background: linear-gradient(to bottom, #ffffff, #eff6ff);
}

/* =====================================================
   NODE HEADER
   ===================================================== */
.flowchart-node-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  background: #f8fafc;
  border-bottom: 2px solid #e2e8f0;
  flex-shrink: 0;
}

.node-icon {
  font-size: 1.5rem;
}

.node-title {
  flex: 1;
  font-weight: 700;
  font-size: 1rem;
  color: #0f172a;
}

/* Delete Button */
.btn-node-delete {
  width: 30px;
  height: 30px;
  background: #fee2e2;
  color: #dc2626;
  border: none;
  border-radius: 8px;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.btn-node-delete:hover {
  background: #fca5a5;
}

/* =====================================================
   NODE BODY - SCROLLABLE
   ===================================================== */
.flowchart-node-body {
  padding: 1rem 1.25rem;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Custom scrollbar */
.flowchart-node-body::-webkit-scrollbar {
  width: 6px;
}

.flowchart-node-body::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.flowchart-node-body::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.flowchart-node-body::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.config-field {
  margin-bottom: 0.875rem;
}

.config-field:last-child {
  margin-bottom: 0;
}

.input-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  margin-bottom: 0.35rem;
  display: block;
  letter-spacing: 0.025em;
}

/* Inputs */
.flowchart-input,
.flowchart-select,
.flowchart-textarea {
  width: 100%;
  padding: 0.625rem;
  border-radius: 8px;
  border: 2px solid #e2e8f0;
  font-size: 0.8rem;
  font-family: inherit;
  background: white;
}

.flowchart-input:focus,
.flowchart-select:focus,
.flowchart-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.12);
}

.flowchart-textarea {
  resize: vertical;
  min-height: 60px;
  max-height: 120px;
}

/* =====================================================
   AUTO PROCESS BLOCK
   ===================================================== */
.auto-process {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.8rem;
  background: #f0fdf4;
  border: 2px dashed #86efac;
  color: #166534;
  text-align: center;
}

.auto-process.output {
  background: #eff6ff;
  border-color: #93c5fd;
  color: #1e40af;
}

.auto-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

/* =====================================================
   FILE UPLOAD
   ===================================================== */
.file-upload-zone {
  position: relative;
}

.file-input-hidden {
  display: none;
}

.file-upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  padding: 1rem;
  border-radius: 10px;
  border: 2px dashed #cbd5e1;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.2s;
}

.file-upload-label:hover {
  border-color: #667eea;
  background: #f0f4ff;
}

.upload-icon {
  font-size: 1.5rem;
}

.file-name {
  font-size: 0.75rem;
  font-weight: 600;
  color: #10b981;
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>