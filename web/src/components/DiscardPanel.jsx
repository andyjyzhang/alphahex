import React, { useState } from "react";
import { RESOURCE_META, RESOURCE_ORDER } from "../format.js";

export default function DiscardPanel({ state, onSubmit }) {
  const playerId = state.current_player;
  const hand = state.players[playerId].resources;
  const handSize = Object.values(hand).reduce((a, b) => a + b, 0);
  const required = Math.floor(handSize / 2);

  const [picked, setPicked] = useState(() => Object.fromEntries(RESOURCE_ORDER.map((resource) => [resource, 0])));
  const total = Object.values(picked).reduce((a, b) => a + b, 0);

  const adjust = (resource, delta) => {
    setPicked((prev) => {
      const next = Math.max(0, Math.min(hand[resource] ?? 0, (prev[resource] ?? 0) + delta));
      return { ...prev, [resource]: next };
    });
  };

  const submit = () => {
    const payload = { resources: {} };
    for (const [resource, count] of Object.entries(picked)) {
      if (count > 0) payload.resources[resource] = count;
    }
    onSubmit({ action_type: "DISCARD", player_id: playerId, payload });
  };

  return (
    <div className="discard-panel">
      <p>
        You rolled into a discard: choose <strong>{required}</strong> cards to discard.
      </p>
      <div className="discard-rows">
        {RESOURCE_ORDER.map((resource) => (
          <div className="discard-row" key={resource}>
            <span className="discard-name">
              <span className="mini-resource" style={{ "--res": RESOURCE_META[resource].color }}>
                {RESOURCE_META[resource].icon}
              </span>
              {RESOURCE_META[resource].label}
            </span>
            <span className="muted">have {hand[resource] ?? 0}</span>
            <div className="stepper">
              <button onClick={() => adjust(resource, -1)} disabled={picked[resource] === 0}>-</button>
              <span className="stepper-value">{picked[resource]}</span>
              <button onClick={() => adjust(resource, 1)} disabled={picked[resource] >= (hand[resource] ?? 0)}>+</button>
            </div>
          </div>
        ))}
      </div>
      <button className="btn-primary" disabled={total !== required} onClick={submit}>
        Discard {total}/{required}
      </button>
    </div>
  );
}
