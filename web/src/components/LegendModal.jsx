import React, { useEffect } from "react";
import { DEV_CARD_META, DEV_CARD_ORDER, HEX_META, RESOURCE_META, RESOURCE_ORDER } from "../format.js";

const DEV_MEANING = {
  KNIGHT: "Move the robber and steal; 3 played = Largest Army (+2 VP)",
  MONOPOLY: "Name a resource; take every one from your opponent",
  YEAR_OF_PLENTY: "Take any 2 resources from the bank",
  ROAD_BUILDING: "Place 2 roads for free",
  VICTORY_POINT: "Worth 1 victory point (kept hidden)",
};

const pieceColor = "#7a6a4e";
function Settlement() {
  return (
    <svg width="22" height="22" viewBox="0 0 22 22">
      <circle cx="11" cy="11" r="7" fill={pieceColor} stroke="#fbf6ea" strokeWidth="2" />
    </svg>
  );
}
function City() {
  return (
    <svg width="22" height="22" viewBox="0 0 22 22">
      <rect x="4" y="4" width="14" height="14" rx="3" fill={pieceColor} stroke="#fbf6ea" strokeWidth="2" />
      <rect x="8" y="8" width="6" height="6" rx="1.5" fill="#ffffff66" />
    </svg>
  );
}
function Road() {
  return (
    <svg width="22" height="22" viewBox="0 0 22 22">
      <line x1="3" y1="16" x2="19" y2="6" stroke={pieceColor} strokeWidth="6" strokeLinecap="round" />
    </svg>
  );
}
function Robber() {
  return (
    <svg width="22" height="22" viewBox="-14 -16 28 32">
      <circle cx="0" cy="0" r="13" fill="rgba(15,12,8,0.82)" />
      <g fill="#ece3cf" stroke="#241c11" strokeWidth="0.6" strokeLinejoin="round">
        <circle cx="0" cy="-7" r="4" />
        <path d="M -3 -3 C -6 1 -7 6 -7 8 L 7 8 C 7 6 6 1 3 -3 C 1.5 -1 -1.5 -1 -3 -3 Z" />
        <rect x="-7.5" y="7.5" width="15" height="3.4" rx="1.7" />
      </g>
    </svg>
  );
}

function Row({ icon, name, meaning }) {
  return (
    <div className="legend-row">
      <span className="legend-icon">{icon}</span>
      <span className="legend-text">
        <span className="legend-name">{name}</span>
        {meaning && <span className="legend-meaning">{meaning}</span>}
      </span>
    </div>
  );
}

export default function LegendModal({ onClose }) {
  useEffect(() => {
    const onKey = (event) => event.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="legend-backdrop" onClick={onClose}>
      <div className="legend-modal" onClick={(event) => event.stopPropagation()}>
        <div className="legend-head">
          <span className="legend-title">Key</span>
          <button className="legend-close" onClick={onClose} aria-label="Close">x</button>
        </div>

        <div className="legend-section">
          <h3>Terrain &amp; Resources</h3>
          <div className="legend-grid">
            {RESOURCE_ORDER.map((resource) => (
              <Row
                key={resource}
                icon={<span className="legend-swatch" style={{ background: HEX_META[resource].color }} />}
                name={HEX_META[resource].label}
                meaning={`${RESOURCE_META[resource].icon} = ${RESOURCE_META[resource].label}`}
              />
            ))}
            <Row icon={<span className="legend-swatch" style={{ background: HEX_META.DESERT.color }} />} name="Desert" meaning="produces nothing" />
          </div>
        </div>

        <div className="legend-section">
          <h3>Board</h3>
          <div className="legend-grid">
            <Row icon={<span className="legend-token">8</span>} name="Number token" meaning="6 and 8 roll most often; dots show odds" />
            <Row icon={<Robber />} name="Robber" meaning="blocks its hex; moved on a 7 or by a Knight" />
            <Row icon={<span className="legend-port">3:1</span>} name="Port" meaning="coastal trade ratio (2:1 specific, 3:1 any)" />
          </div>
        </div>

        <div className="legend-section">
          <h3>Pieces</h3>
          <div className="legend-grid">
            <Row icon={<Settlement />} name="Settlement" meaning="1 VP" />
            <Row icon={<City />} name="City" meaning="2 VP" />
            <Row icon={<Road />} name="Road" meaning="longest = +2 VP" />
          </div>
        </div>

        <div className="legend-section">
          <h3>Development Cards</h3>
          <div className="legend-list">
            {DEV_CARD_ORDER.map((card) => (
              <Row
                key={card}
                icon={<span className="legend-icon-token">{DEV_CARD_META[card].icon}</span>}
                name={DEV_CARD_META[card].label}
                meaning={DEV_MEANING[card]}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
