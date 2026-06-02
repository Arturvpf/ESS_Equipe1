import React from "react";
import { useAuth } from "../context/AuthContext";
import Navbar from "../components/Navbar";

function InfoRow({ label, value }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "3px" }}>
      <span style={{ fontSize: "0.72rem", color: "#2c6fac", textTransform: "uppercase", letterSpacing: "0.05em" }}>
        {label}
      </span>
      <span style={{ fontSize: "0.92rem", color: "#555" }}>{value || "—"}</span>
    </div>
  );
}

export default function Perfil() {
  const { user } = useAuth();

  return (
    <Navbar>
      <h1 style={s.title}>Meu Perfil</h1>
      <div style={s.card}>
        <div style={s.grid}>
          <InfoRow label="Nome"  value={user?.nome} />
          <InfoRow label="CPF"   value={user?.cpf} />
          <InfoRow label="Tipo"  value={user?.tipo} />
          {user?.matricula && <InfoRow label="Matrícula" value={user.matricula} />}
          {user?.curso     && <InfoRow label="Curso"     value={user.curso} />}
          {user?.siape     && <InfoRow label="SIAPE"     value={user.siape} />}
        </div>
      </div>
    </Navbar>
  );
}

const s = {
  title: { fontSize: "1.4rem", fontWeight: "700", color: "#1e3a5f", marginBottom: "1.5rem" },
  card: {
    background: "rgba(255,255,255,0.04)",
    border: "1px solid rgba(255,255,255,0.07)",
    borderRadius: "12px",
    padding: "1.5rem",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))",
    gap: "1.25rem",
  },
};
