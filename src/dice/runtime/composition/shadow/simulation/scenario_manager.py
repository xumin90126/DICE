"""
Phase 6.1-L2.1: ScenarioManager — Simulation Logic (Phase B implemented).

Responsibility:
    Create and validate SimulationScenario objects. Scenarios define
    the parameters, constraints, and expected behaviors for a simulation run.

    This runs entirely inside the Shadow Simulation namespace — scenarios are
    hypothetical artifacts that are NEVER executed against the Capability
    Runtime or Registry.

Input:
    - SimulationRequest (from SimulationEngine)

Output:
    - SimulationScenario (validated, ready for SimulationEngine) or None

Forbidden:
    - ❌ No Capability Registry access
    - ❌ No Runtime 1-8 modification
    - ❌ No production execution paths
    - ❌ No activation paths

Shadow guarantees:
    - shadow_marked = True on all artifacts
    - origin = "composition_shadow_storage"
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .models import SimulationRequest, SimulationScenario


class ScenarioManager:
    """Create and validate simulation scenarios (Shadow-only)."""

    def __init__(self) -> None:
        # In-memory template registry (shadow storage). Templates are plain
        # dicts registered by tests / bootstrap; never persisted to Runtime.
        self._templates: Dict[str, Dict] = {}

    def create_scenario(
        self, request: SimulationRequest
    ) -> Optional[SimulationScenario]:
        """Build a validated SimulationScenario from a SimulationRequest.

        Resolution order for each field (later wins):
            capabilities: request.scope["capabilities"] → template → []
            name:         request.scope["name"] → template → request.intent
            constraints:  template["constraints"] → {}
            expected:     template["expected"] → {}
            parameters:   template["parameters"] → request parameters

        Returns:
            SimulationScenario with all parameters resolved, or None if the
            built scenario fails validation.
        """
        # ── Template resolution ──
        template_id: Optional[str] = None
        req_params = request.parameters if isinstance(request.parameters, dict) else {}
        scope = request.scope if isinstance(request.scope, dict) else {}

        template_id = req_params.get("template_id") or scope.get("template_id")
        template: Dict = self._load_template(template_id) if template_id else {}

        # ── Capabilities resolution ──
        capabilities = scope.get("capabilities")
        if capabilities is None:
            capabilities = template.get("capabilities", [])
        if not isinstance(capabilities, list):
            capabilities = list(capabilities) if capabilities else []
        # Keep only string capability ids (filter non-string noise).
        capabilities = [c for c in capabilities if isinstance(c, str)]

        # ── Name resolution ──
        name = scope.get("name") or template.get("name") or request.intent or "scenario"
        if not isinstance(name, str):
            name = str(name)

        # ── Build scenario (shadow-only) ──
        scenario = SimulationScenario(
            name=name,
            capabilities=capabilities,
            constraints=dict(template.get("constraints", {}) or {}),
            expected=dict(template.get("expected", {}) or {}),
            parameters=dict(template.get("parameters", {}) or {}),
            shadow_marked=True,
            origin="composition_shadow_storage",
        )

        # ── Resolve parameters (request values overlay template defaults) ──
        self._resolve_parameters(scenario, request)

        # ── Validate ──
        if not self.validate_scenario(scenario):
            return None
        return scenario

    def validate_scenario(self, scenario: SimulationScenario) -> bool:
        """Validate a scenario meets all shadow constraints and preconditions.

        Checks:
            - scenario is not None
            - shadow_marked is True (C2)
            - origin is composition_shadow_storage (C2)
            - capabilities / constraints / expected / parameters are well-typed

        Returns:
            True if scenario passes all validations.
        """
        if scenario is None:
            return False
        if not getattr(scenario, "shadow_marked", False):
            return False
        if scenario.origin != "composition_shadow_storage":
            return False
        if not isinstance(scenario.capabilities, list):
            return False
        if not isinstance(scenario.constraints, dict):
            return False
        if not isinstance(scenario.expected, dict):
            return False
        if not isinstance(scenario.parameters, dict):
            return False
        return True

    def _load_template(self, template_id: str) -> Dict:
        """Load a scenario template from shadow storage (in-memory registry).

        Missing / unregistered templates safely degrade to an empty dict —
        no exception escapes the shadow boundary.

        Returns:
            A shallow copy of the registered template, or {} if absent.
        """
        if not template_id:
            return {}
        template = self._templates.get(template_id)
        if template is None:
            return {}
        return dict(template)

    def _resolve_parameters(
        self, scenario: SimulationScenario, request: SimulationRequest
    ) -> None:
        """Overlay request values onto scenario parameters (request wins).

        Request parameters (and request.scope["parameters"]) take precedence
        over any template defaults already present on the scenario.
        Mutates ``scenario.parameters`` in place.
        """
        req_params = request.parameters if isinstance(request.parameters, dict) else {}
        scenario.parameters.update(req_params)

        scope = request.scope if isinstance(request.scope, dict) else {}
        scope_params = scope.get("parameters")
        if isinstance(scope_params, dict):
            scenario.parameters.update(scope_params)
