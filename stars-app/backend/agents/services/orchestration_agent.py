from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from ..models.cohort import CohortRequest
from ..models.nba import NBARequest
from ..models.communication import CommunicationRequest
from ..models.orchestration import (
    CampaignConfig, PipelineState, PipelineStage, PipelineSummary,
    ApprovalRequest,
)
from .cohort_agent import CohortPrioritizationAgent
from .nba_agent import NextBestActionAgent
from .communication_agent import CommunicationAgent

logger = logging.getLogger("agent.orchestration")


class OrchestrationAgent:

    def __init__(self):
        self._pipelines: dict[str, PipelineState] = {}
        self._cohort = CohortPrioritizationAgent()
        self._nba = NextBestActionAgent()
        self._comm = CommunicationAgent()

    def create_campaign(self, config: CampaignConfig) -> PipelineState:
        campaign_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()

        state = PipelineState(
            campaign_id=campaign_id,
            campaign_name=config.campaign_name,
            stage=PipelineStage.prioritization,
            config=config,
            created_at=now,
            updated_at=now,
        )
        self._pipelines[campaign_id] = state

        try:
            self._run_prioritization(state)
            self._run_nba(state)

            if config.mode == "auto":
                self._run_communication(state)
                state.stage = PipelineStage.completed
            else:
                state.stage = PipelineStage.awaiting_approval
        except Exception as exc:
            state.stage = PipelineStage.failed
            state.error = str(exc)[:500]
            logger.error("Pipeline %s failed: %s", campaign_id, exc)

        state.updated_at = datetime.now(timezone.utc).isoformat()
        return state

    def approve_campaign(
        self, campaign_id: str, approval: ApprovalRequest
    ) -> PipelineState:
        state = self._pipelines.get(campaign_id)
        if not state:
            raise ValueError(f"Campaign {campaign_id} not found")
        if state.stage != PipelineStage.awaiting_approval:
            raise ValueError(
                f"Campaign {campaign_id} is in stage {state.stage.value}, "
                f"not awaiting_approval"
            )

        if not approval.approved:
            state.stage = PipelineStage.failed
            state.error = "Rejected by user"
            state.updated_at = datetime.now(timezone.utc).isoformat()
            return state

        if approval.excluded_member_keys and state.nba_result:
            excluded = set(approval.excluded_member_keys)
            state.nba_result.actions = [
                a for a in state.nba_result.actions
                if a.member_key not in excluded
            ]

        try:
            self._run_communication(state)
            state.stage = PipelineStage.completed
        except Exception as exc:
            state.stage = PipelineStage.failed
            state.error = str(exc)[:500]

        state.updated_at = datetime.now(timezone.utc).isoformat()
        return state

    def retry_campaign(self, campaign_id: str) -> PipelineState:
        state = self._pipelines.get(campaign_id)
        if not state:
            raise ValueError(f"Campaign {campaign_id} not found")
        if state.stage != PipelineStage.failed:
            raise ValueError("Only failed pipelines can be retried")

        state.error = None
        try:
            if not state.cohort_result:
                self._run_prioritization(state)
            if not state.nba_result:
                self._run_nba(state)
            if not state.communication_result:
                if state.config.mode == "auto":
                    self._run_communication(state)
                    state.stage = PipelineStage.completed
                else:
                    state.stage = PipelineStage.awaiting_approval
        except Exception as exc:
            state.stage = PipelineStage.failed
            state.error = str(exc)[:500]

        state.updated_at = datetime.now(timezone.utc).isoformat()
        return state

    def get_pipeline(self, campaign_id: str) -> PipelineState | None:
        return self._pipelines.get(campaign_id)

    def list_pipelines(self) -> list[PipelineSummary]:
        summaries = []
        for state in self._pipelines.values():
            total_members = (
                state.cohort_result.total_scored if state.cohort_result else 0
            )
            total_actions = (
                len(state.nba_result.actions) if state.nba_result else 0
            )
            total_sent = (
                state.communication_result.total_sent
                if state.communication_result else 0
            )
            est_closures = 0
            est_cost = 0.0
            if state.nba_result:
                est_closures = round(
                    sum(a.predicted_closure_prob for a in state.nba_result.actions)
                )
                est_cost = state.nba_result.total_budget_estimate

            summaries.append(PipelineSummary(
                campaign_id=state.campaign_id,
                campaign_name=state.campaign_name,
                stage=state.stage.value,
                total_members=total_members,
                total_actions=total_actions,
                total_sent=total_sent,
                estimated_closures=est_closures,
                estimated_cost=est_cost,
                created_at=state.created_at,
            ))
        return summaries

    def _run_prioritization(self, state: PipelineState) -> None:
        state.stage = PipelineStage.prioritization
        req = CohortRequest(
            contract_id=state.config.contract_id,
            measure_code=state.config.measure_code,
            gap_statuses=state.config.gap_statuses,
            propensity_tiers=state.config.propensity_tiers,
            max_members=state.config.max_members,
            measurement_year=state.config.measurement_year,
        )
        state.cohort_result = self._cohort.prioritize(req)

    def _run_nba(self, state: PipelineState) -> None:
        state.stage = PipelineStage.nba
        req = NBARequest(
            members=state.cohort_result.members,
            contract_id=state.config.contract_id,
            budget_per_member=state.config.budget_per_member,
            measurement_year=state.config.measurement_year,
        )
        state.nba_result = self._nba.recommend(req)

    def _run_communication(self, state: PipelineState) -> None:
        state.stage = PipelineStage.communication
        req = CommunicationRequest(
            actions=state.nba_result.actions,
            campaign_name=state.config.campaign_name,
            plan_name=state.config.plan_name,
            dry_run=False,
        )
        state.communication_result = self._comm.execute(req)
