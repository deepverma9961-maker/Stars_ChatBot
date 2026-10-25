import { Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/layout/Sidebar";
import MarketingOverview from "./pages/MarketingOverview";
import ExecutiveOverview from "./pages/ExecutiveOverview";
import PlanDetail from "./pages/PlanDetail";
import HedisMeasures from "./pages/HedisMeasures";
import Simulator from "./pages/Simulator";
import AgentExecution from "./pages/AgentExecution";
import ImpactProjector from "./pages/ImpactProjector";
import CampaignROI from "./pages/CampaignROI";
import AlertsPriorities from "./pages/AlertsPriorities";
import MemberGapList from "./pages/MemberGapList";
import CahpsOverview from "./pages/CahpsOverview";

export default function App() {
  return (
    <div className="flex h-screen overflow-hidden bg-brand-dark">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Navigate to="/marketing" replace />} />
          <Route path="/marketing" element={<MarketingOverview />} />
          <Route path="/executive" element={<ExecutiveOverview />} />
          <Route path="/plan/:contractId" element={<PlanDetail />} />
          <Route path="/hedis" element={<HedisMeasures />} />
          <Route path="/simulator" element={<Simulator />} />
          <Route path="/agent" element={<AgentExecution />} />
          <Route path="/projector" element={<ImpactProjector />} />
          <Route path="/campaigns" element={<CampaignROI />} />
          <Route path="/alerts" element={<AlertsPriorities />} />
          <Route path="/members" element={<MemberGapList />} />
          <Route path="/cahps" element={<CahpsOverview />} />
        </Routes>
      </main>
    </div>
  );
}
