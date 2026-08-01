import { useEffect } from "react";

export default function ModalFeature({ isOpen, onClose, feature }) {
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (event) => {
      if (event.key === "Escape") onClose();
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !feature) return null;

  return (
    <div className="modal fade show d-block" tabIndex="-1" role="dialog" aria-modal="true" aria-label={`${feature.title} details`}>
      <div className="modal-dialog modal-dialog-centered modal-lg" role="document">
        <div className="modal-content border-0 shadow-lg" style={{ background: "rgba(15, 23, 42, 0.97)" }}>
          <div className="modal-header border-0">
            <div className="d-flex align-items-center gap-3">
              <div className={`rounded-2xl bg-gradient-to-br ${feature.accent} p-3 text-2xl`}>
                {feature.icon}
              </div>
              <div>
                <h5 className="modal-title text-white mb-0">{feature.title}</h5>
                <p className="small text-slate-400 mb-0">{feature.tagline}</p>
              </div>
            </div>
            <button type="button" className="btn-close btn-close-white" aria-label="Close" onClick={onClose}></button>
          </div>
          <div className="modal-body py-3">
            <div className="row g-3">
              <div className="col-12 col-md-6">
                <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
                  <h6 className="text-cyan-300 mb-2">Overview</h6>
                  <p className="small text-slate-300 mb-0">{feature.overview}</p>
                </div>
              </div>
              <div className="col-12 col-md-6">
                <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
                  <h6 className="text-cyan-300 mb-2">How it works</h6>
                  <p className="small text-slate-300 mb-0">{feature.howItWorks}</p>
                </div>
              </div>
              <div className="col-12 col-md-6">
                <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
                  <h6 className="text-cyan-300 mb-2">Technologies</h6>
                  <p className="small text-slate-300 mb-0">{feature.technologies}</p>
                </div>
              </div>
              <div className="col-12 col-md-6">
                <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
                  <h6 className="text-cyan-300 mb-2">Benefits</h6>
                  <p className="small text-slate-300 mb-0">{feature.benefits}</p>
                </div>
              </div>
            </div>
            <div className="rounded-2xl border border-cyan-400/20 bg-cyan-500/10 p-3 mt-3">
              <h6 className="text-cyan-300 mb-1">Future scope</h6>
              <p className="small text-slate-300 mb-0">{feature.futureScope}</p>
            </div>
          </div>
          <div className="modal-footer border-0">
            <button type="button" className="btn btn-outline-light" onClick={onClose}>Close</button>
          </div>
        </div>
      </div>
    </div>
  );
}
