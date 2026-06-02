import React from "react";
import Navbar from "./Navbar";

/**
 * Página genérica "em desenvolvimento".
 * Uso: <WipPage title="Reservas de Sala" />
 */
export default function WipPage({ title }) {
  return (
    <Navbar>
      <div style={s.wrapper}>
        <span style={s.badge}>{title}</span>
        <h1 style={s.title}>{title}</h1>
        <p style={s.text}>Esta funcionalidade está em desenvolvimento.</p>
      </div>
    </Navbar>
  );
}

const s = {
  wrapper: {
    paddingTop: "3rem",
  },
  badge: {
    display: "inline-block",
    background: "rgba(67,97,238,0.15)",
    border: "1px solid rgba(67,97,238,0.3)",
    color: "#7b96ff",
    padding: "3px 12px",
    borderRadius: "20px",
    fontSize: "0.75rem",
    letterSpacing: "0.05em",
    textTransform: "uppercase",
    marginBottom: "1rem",
  },
  title: {
    fontSize: "1.6rem",
    fontWeight: "700",
    color: "#fff",
    marginBottom: "0.75rem",
    letterSpacing: "-0.02em",
  },
  text: {
    color: "#555",
    fontSize: "0.92rem",
  },
};
