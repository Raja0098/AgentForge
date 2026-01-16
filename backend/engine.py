# backend/engine.py

from collections import deque


class WorkflowEngine:
    """
    Executes a workflow DAG using topological sorting.
    Each node is executed only after its dependencies complete.
    """

    def __init__(self, registry):
        self.registry = registry

    async def execute(self, workflow):
        """
        Execute the given workflow.

        Returns:
            results (dict): node_id -> output
            logs (list): execution logs
        """
        results = {}

        # ================================
        # Build graph structures
        # ================================
        node_map = {node.id: node for node in workflow.nodes}
        adjacency = {node.id: [] for node in workflow.nodes}
        indegree = {node.id: 0 for node in workflow.nodes}

        for connection in workflow.connections:
            adjacency[connection.source].append(connection.target)
            indegree[connection.target] += 1

        # ================================
        # Topological sort (Kahn's Algorithm)
        # ================================
        queue = deque(node_id for node_id, deg in indegree.items() if deg == 0)
        execution_order = []

        while queue:
            current = queue.popleft()
            execution_order.append(current)

            for neighbor in adjacency[current]:
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)

        if len(execution_order) != len(node_map):
            raise Exception("Cycle detected in workflow")

        # ================================
        # Identify output node (if exists)
        # ================================
        output_node_id = None
        for node in workflow.nodes:
            if node.subtype == "output":
                output_node_id = node.id
                break

        # ================================
        # Execute nodes in order
        # ================================
        for node_id in execution_order:
            node = node_map[node_id]

            # Instantiate node
            node_instance = self.registry.get_node_instance(node.subtype)

            # Collect parent outputs
            parent_outputs = {
                conn.source: results[conn.source]
                for conn in workflow.connections
                if conn.target == node_id and conn.source in results
            }

            # Execute node
            output = await node_instance.execute(node.config, parent_outputs)
            results[node_id] = output

            # ================================
            # Guardrail blocking support
            # ================================
            if output.get("blocked") is True:
                if output_node_id:
                    output_node = self.registry.get_node_instance("output")
                    results[output_node_id] = await output_node.execute(
                        {}, {node_id: output}
                    )
                break

        # ================================
        # Execution logs
        # ================================
        logs = [
            {
                "event": "completed"
            }
        ]

        return results, logs
