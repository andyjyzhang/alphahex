import React from "react";
import { RESOURCE_META, RESOURCE_ORDER } from "../format.js";

const BANK_TOTAL = 19;

export default function BankPanel({ state }) {
  const held = Object.fromEntries(RESOURCE_ORDER.map((resource) => [resource, 0]));
  for (const player of state.players) {
    for (const resource of RESOURCE_ORDER) held[resource] += player.resources[resource] || 0;
  }
  const devLeft = state.dev_card_deck?.length ?? 0;

  return (
    <div className="panel bank-panel">
      <h2>Bank</h2>
      <div className="bank-res">
        {RESOURCE_ORDER.map((resource) => (
          <div className="bank-cell" key={resource} title={RESOURCE_META[resource].label}>
            <span className="bank-icon" style={{ "--res": RESOURCE_META[resource].color }}>
              {RESOURCE_META[resource].icon}
            </span>
            <span className="bank-count">{Math.max(0, BANK_TOTAL - held[resource])}</span>
          </div>
        ))}
      </div>
      <div className="bank-dev">
        <span>Dev card deck</span>
        <strong>{devLeft}</strong>
      </div>
    </div>
  );
}
