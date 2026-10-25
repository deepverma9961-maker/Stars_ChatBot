import { useState, useMemo } from "react";
import PageShell from "../components/layout/PageShell";
import StarRatingBadge from "../components/shared/StarRatingBadge";
import { useGetHedisMeasures } from "../api/hedis";

const WEIGHTS: Record<string, number> = { HBD: 3, CBP: 3, PCR: 3 };
const THRESHOLDS: Record<string, { "4star": number; "5star": number }> = {
  HBD: { "4star": 80, "5star": 90 }, CBP: { "4star": 70, "5star": 80 },
  PCR: { "4star": 75, "5star": 85 }, BCS: { "4star": 72, "5star": 82 },
  COL: { "4star": 68, "5star": 78 }, COA_MR: { "4star": 82, "5star": 90 },
  COA_PA: { "4star": 74, "5star": 84 }, OMW: { "4star": 62, "5star": 72 },
};

function rateToStars(rate: number, code: string): number {
  const t = THRESHOLDS[code] ?? { "4star": 70, "5star": 80 };
  if (rate >= t["5star"]) return 5;
  if (rate >= t["4star"]) return 4;
  if (rate >= t["4star"] - 8) return 3;
  return 2;
}

export default function ImpactProjector() {
  const { data: measures } = useGetHedisMeasures();
  const [sliders, setSliders] = useState<Record<string, number>>({});

  const setSlider = (code: string, val: number) =>
    setSliders(prev => ({ ...prev, [code]: val }));

  const projected = useMemo(() => {
    if (!measures) return null;
    let totalW = 0, wSum = 0;
    measures.slice(0, 8).forEach(m => {
      const additional = sliders[m.measure_code] ?? 0;
      const newRate = Math.min(100, m.current_rate + additional);
      const stars = rateToStars(newRate, m.measure_code);
      const w = WEIGHTS[m.measure_code] ?? 1;
      wSum += stars * w;
      totalW += w;
    });
    if (!totalW) return 4.0;
    const raw = wSum / totalW;
    return Math.round(raw * 2) / 2;
  }, [measures, sliders]);

  const baseline = 4.0;

  return (
    <PageShell title="Impact Projector" subtitle="Drag sliders to model star rating impact of gap closures">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sliders */}
        <div className="lg:col-span-2 space-y-4">
          {(measures ?? []).slice(0, 8).map(m => {
            const additional = sliders[m.measure_code] ?? 0;
            const newRate = Math.min(100, m.current_rate + additional);
            return (
              <div key={m.measure_code} className="card">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <div className="text-white text-sm font-medium">{m.measure_name}</div>
                    <div className="text-muted text-xs">{m.measure_code} · {WEIGHTS[m.measure_code] === 3 ? "3x weight" : "1x weight"}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-white font-bold">{newRate.toFixed(1)}%</div>
                    {additional > 0 && <div className="text-brand-teal text-xs">+{additional.toFixed(0)}pp</div>}
                  </div>
                </div>
                <input
                  type="range"
                  min={0}
                  max={Math.max(1, 100 - m.current_rate)}
                  step={0.5}
                  value={additional}
                  onChange={e => setSlider(m.measure_code, Number(e.target.value))}
                  className="w-full accent-brand-teal"
                />
                <div className="flex justify-between text-[10px] text-muted mt-1">
                  <span>Base: {m.current_rate.toFixed(1)}%</span>
                  <span>Target: {m.target_rate.toFixed(1)}%</span>
                  <span>Max: 100%</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Projection panel */}
        <div className="space-y-4">
          <div className="card text-center">
            <div className="text-muted text-xs mb-3">Baseline Rating</div>
            <StarRatingBadge rating={baseline} size="lg" />
          </div>
          <div className="card text-center border-brand-teal">
            <div className="text-muted text-xs mb-3">Projected Rating</div>
            {projected !== null && <StarRatingBadge rating={projected} size="lg" />}
            {projected !== null && projected > baseline && (
              <div className="text-brand-teal text-sm mt-2 font-medium">+{(projected - baseline).toFixed(1)} ★ improvement</div>
            )}
          </div>
          <div className="card">
            <div className="section-title text-sm">Slider Summary</div>
            {Object.entries(sliders).filter(([, v]) => v > 0).length === 0 ? (
              <div className="text-muted text-xs">No adjustments made yet</div>
            ) : (
              Object.entries(sliders).filter(([, v]) => v > 0).map(([code, val]) => (
                <div key={code} className="flex justify-between text-xs py-1 border-b border-brand-border/40">
                  <span className="text-white">{code}</span>
                  <span className="text-brand-teal">+{val.toFixed(1)}pp</span>
                </div>
              ))
            )}
          </div>
          <button
            onClick={() => setSliders({})}
            className="w-full py-2 rounded-lg border border-brand-border text-muted text-sm hover:text-white hover:border-white/30 transition"
          >
            Reset All Sliders
          </button>
        </div>
      </div>
    </PageShell>
  );
}
