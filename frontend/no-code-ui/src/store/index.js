import { createStore } from 'vuex'

export default createStore({
  /* =====================================================
   * STATE
   * ===================================================== */
  state: {
    // All node templates available in the UI
    availableNodes: {
      agents: [],
      tools: [],
      special: []
    },

    // Currently active workflow
    workflow: {
      id: 'wf_default',
      name: 'Untitled Workflow',
      nodes: [],
      connections: []
    },

    // Saved workflows (localStorage)
    savedWorkflows: [],

    // UI / execution state
    selectedTemplate: null,
    executionResult: null,
    isExecuting: false
  },

  /* =====================================================
   * MUTATIONS
   * ===================================================== */
  mutations: {
    /* ---------- Node / Template ---------- */
    SET_AVAILABLE_NODES(state, payload) {
      state.availableNodes = payload
    },

    SET_TEMPLATE(state, template) {
      state.selectedTemplate = template
    },

    /* ---------- Workflow Metadata ---------- */
    SET_WORKFLOW_NAME(state, name) {
      state.workflow.name = name
    },

    LOAD_WORKFLOW(state, workflow) {
      state.workflow = workflow
    },

    CLEAR_WORKFLOW(state) {
      state.workflow = {
        id: `wf_${Date.now()}`,
        name: 'Untitled Workflow',
        nodes: [],
        connections: []
      }

      state.executionResult = null
      state.selectedTemplate = null
    },

    /* ---------- Nodes ---------- */
    ADD_NODE(state, node) {
      state.workflow.nodes.push(node)
      state.selectedTemplate = null
    },

    UPDATE_NODE_CONFIG(state, { nodeId, key, value }) {
      const node = state.workflow.nodes.find(n => n.id === nodeId)
      if (node) {
        node.config[key] = value
      }
    },

    DELETE_NODE(state, nodeId) {
      state.workflow.nodes = state.workflow.nodes.filter(
        node => node.id !== nodeId
      )

      state.workflow.connections = state.workflow.connections.filter(
        conn => conn.source !== nodeId && conn.target !== nodeId
      )
    },

    /* ---------- Connections ---------- */
    ADD_CONNECTION(state, connection) {
      const exists = state.workflow.connections.some(
        c => c.source === connection.source && c.target === connection.target
      )

      if (!exists) {
        state.workflow.connections.push(connection)
      }
    },

    /* ---------- Execution ---------- */
    SET_EXECUTING(state, value) {
      state.isExecuting = value
    },

    SET_EXECUTION_RESULT(state, result) {
      state.executionResult = result
    },

    /* ---------- Saved Workflows ---------- */
    SET_SAVED_WORKFLOWS(state, workflows) {
      state.savedWorkflows = workflows
    },

    ADD_SAVED_WORKFLOW(state, workflow) {
      const index = state.savedWorkflows.findIndex(
        w => w.id === workflow.id
      )

      if (index >= 0) {
        state.savedWorkflows[index] = workflow
      } else {
        state.savedWorkflows.push(workflow)
      }
    },

    DELETE_SAVED_WORKFLOW(state, workflowId) {
      state.savedWorkflows = state.savedWorkflows.filter(
        w => w.id !== workflowId
      )
    }
  },

  /* =====================================================
   * ACTIONS
   * ===================================================== */
  actions: {
    /* ---------- Persistence ---------- */
    saveWorkflow({ state, commit }) {
      const workflows = JSON.parse(
        localStorage.getItem('ai_workflows') || '[]'
      )

      const index = workflows.findIndex(
        w => w.id === state.workflow.id
      )

      if (index >= 0) {
        workflows[index] = {
          ...state.workflow,
          updatedAt: new Date().toISOString()
        }
      } else {
        workflows.push({
          ...state.workflow,
          createdAt: new Date().toISOString()
        })
      }

      localStorage.setItem('ai_workflows', JSON.stringify(workflows))
      commit('SET_SAVED_WORKFLOWS', workflows)
    },

    loadSavedWorkflows({ commit }) {
      const workflows = JSON.parse(
        localStorage.getItem('ai_workflows') || '[]'
      )
      commit('SET_SAVED_WORKFLOWS', workflows)
    },

    loadWorkflow({ commit }, workflowId) {
      const workflows = JSON.parse(
        localStorage.getItem('ai_workflows') || '[]'
      )

      const workflow = workflows.find(w => w.id === workflowId)
      if (workflow) {
        commit('LOAD_WORKFLOW', workflow)
      }
    },

    deleteWorkflow({ state, commit }, workflowId) {
      const workflows = JSON.parse(
        localStorage.getItem('ai_workflows') || '[]'
      )

      const filtered = workflows.filter(w => w.id !== workflowId)
      localStorage.setItem('ai_workflows', JSON.stringify(filtered))
      commit('SET_SAVED_WORKFLOWS', filtered)

      if (state.workflow.id === workflowId) {
        commit('CLEAR_WORKFLOW')
      }
    },

    /* ---------- Execution ---------- */
    async executeWorkflow({ state, commit }) {
      commit('SET_EXECUTING', true)
      commit('SET_EXECUTION_RESULT', null)

      try {
        const response = await fetch(
          'http://127.0.0.1:8000/api/execute',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ workflow: state.workflow })
          }
        )

        const data = await response.json()
        if (!response.ok) {
          throw new Error(data.detail || 'Execution failed')
        }

        commit('SET_EXECUTION_RESULT', {
          status: 'success',
          result: data.result,
          logs: data.logs
        })
      } catch (error) {
        commit('SET_EXECUTION_RESULT', {
          status: 'error',
          message: error.message
        })
      } finally {
        commit('SET_EXECUTING', false)
      }
    }
  }
})
