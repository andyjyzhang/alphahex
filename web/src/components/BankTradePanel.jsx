import React, { useState } from "react";
import { RESOURCE_META, RESOURCE_ORDER } from "../format.js";

function ResourceToken({ resource }) {
  const meta = RESOURCE_META[resource];
  return (
    <span className="res-chip-icon" style={{ "--res": meta.color }} title={meta.label}>
      {meta.icon}
    </span>
  );
}

export default function BankTradePanel({ actions, onAction }) {
  const ratios = {};
  for (const action of actions) ratios[action.payload.give] = action.payload.give_count;
  const gives = RESOURCE_ORDER.filter((resource) => resource in ratios);

  const [give, setGive] = useState(gives[0]);
  const [receive, setReceive] = useState(null);

  const effGive = gives.includes(give) ? give : gives[0];
  const receives = RESOURCE_ORDER.filter((resource) => resource !== effGive);
  const effReceive = receives.includes(receive) ? receive : receives[0];
  const ratio = ratios[effGive];
  const trade = actions.find((action) => action.payload.give === effGive && action.payload.receive === effReceive);

  return (
    <div className="trade-panel">
      <div className="action-group-head">
        <span>Bank trade</span>
      </div>

      <div className="trade-grid">
        <span className="trade-label">You give</span>
        <div className="res-chips">
          {gives.map((resource) => (
            <button
              key={resource}
              className={`res-chip${resource === effGive ? " sel" : ""}`}
              onClick={() => setGive(resource)}
              title={`${ratios[resource]}:1 ${RESOURCE_META[resource].label}`}
            >
              <ResourceToken resource={resource} />
              <span className="res-chip-ratio">{ratios[resource]}:1</span>
            </button>
          ))}
        </div>

        <span className="trade-label">You get</span>
        <div className="res-chips">
          {receives.map((resource) => (
            <button
              key={resource}
              className={`res-chip${resource === effReceive ? " sel" : ""}`}
              onClick={() => setReceive(resource)}
              title={RESOURCE_META[resource].label}
            >
              <ResourceToken resource={resource} />
            </button>
          ))}
        </div>
      </div>

      <button className="btn-primary trade-go" disabled={!trade} onClick={() => trade && onAction(trade)}>
        <span className="trade-go-side">{ratio} {RESOURCE_META[effGive].icon}</span>
        <span className="trade-arrow">-&gt;</span>
        <span className="trade-go-side">1 {RESOURCE_META[effReceive].icon}</span>
      </button>
    </div>
  );
}
