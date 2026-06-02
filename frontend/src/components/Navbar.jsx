import React from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const ROLE_LABELS = {
  discente: "DISCENTE",
  docente:  "DOCENTE",
  admin:    "ADMIN",
};

const NAV_ITEMS = {
  discente: [
    { label: "Reservas de Sala",         path: "/reservas-de-sala" },
    { label: "Reservas de Equipamentos", path: "/reservas-de-equipamento" },
    { label: "Meu perfil",               path: "/perfil" },
  ],
  docente: [
    { label: "Reservas de Sala", path: "/reservas-de-sala" },
    { label: "Manutenções",      path: "/solicitacoes-de-manutencao" },
    { label: "Meu perfil",       path: "/perfil" },
  ],
  admin: [
    { label: "Salas",       path: "/salas" },
    { label: "Reservas",    path: "/reservas" },
    { label: "Manutenções", path: "/manutencoes" },
    { label: "Meu perfil",  path: "/perfil" },
  ],
};

function getInitials(nome) {
  if (!nome) return "?";
  const parts = nome.trim().split(" ");
  return (parts[0][0] + (parts[1]?.[0] || "")).toUpperCase();
}

export default function Navbar({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  const navItems  = NAV_ITEMS[user?.tipo] || [];
  const roleLabel = ROLE_LABELS[user?.tipo] || "";
  const initials  = getInitials(user?.nome);

  return (
    <div style={s.wrapper}>
      <header style={s.navbar}>
        {/* Logo */}
        <div style={s.logoArea}>
          <span style={s.logoDot} />
          <Link to={navItems[0]?.path || "/"} style={s.brand}>Salla</Link>
        </div>

        {/* Nav links */}
        <nav style={s.navLinks}>
          {navItems.filter(i => i.path !== "/perfil").map(item => {
            const active = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                style={{ ...s.navItem, ...(active ? s.navItemActive : {}) }}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Perfil */}
        <div style={s.profileArea}>
          <Link to="/perfil" style={s.profileLink}>
            <span style={s.avatar}>{initials}</span>
            <div style={s.profileInfo}>
              <span style={s.profileName}>
                {(() => {
                  const partes = user?.nome?.trim().split(/\s+/) || [];
                  return partes.length > 1
                    ? `${partes[0]} ${partes[partes.length - 1]}`
                    : partes[0] || "";
                })()}
              </span>
              <span style={s.profileRole}>{roleLabel}</span>
            </div>
          </Link>
          <button style={s.logoutBtn} onClick={handleLogout} title="Sair">✕</button>
        </div>
      </header>

      <main style={s.main}>
        {children}
      </main>
    </div>
  );
}

const s = {
  wrapper:       { minHeight: "100vh", background: "#f7f8fa", color: "#f0f0f0", fontFamily: "system-ui, sans-serif" },
  navbar:        { display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 2rem", height: "58px", background: "#16182a", borderBottom: "1px solid rgba(255,255,255,0.06)", position: "sticky", top: 0, zIndex: 100, gap: "2rem" },
  logoArea:      { display: "flex", alignItems: "center", gap: "8px", flexShrink: 0 },
  logoDot:       { width: "10px", height: "10px", borderRadius: "50%", background: "#4361ee" },
  brand:         { fontSize: "1.1rem", fontWeight: "700", color: "#fff", textDecoration: "none", fontFamily: "Georgia, serif", letterSpacing: "-0.02em" },
  navLinks:      { display: "flex", alignItems: "center", gap: "0.25rem", flex: 1, justifyContent: "center" },
  navItem:       { padding: "6px 14px", borderRadius: "6px", color: "#888", textDecoration: "none", fontSize: "0.88rem", fontWeight: "500", whiteSpace: "nowrap" },
  navItemActive: { background: "rgba(255,255,255,0.08)", color: "#fff", fontWeight: "600" },
  profileArea:   { display: "flex", alignItems: "center", gap: "0.75rem", flexShrink: 0 },
  profileLink:   { display: "flex", alignItems: "center", gap: "0.6rem", textDecoration: "none" },
  avatar:        { width: "34px", height: "34px", borderRadius: "50%", background: "#4361ee", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.75rem", fontWeight: "700", flexShrink: 0 },
  profileInfo:   { display: "flex", flexDirection: "column", lineHeight: 1.2 },
  profileName:   { fontSize: "0.85rem", color: "#e0e0e0", fontWeight: "600" },
  profileRole:   { fontSize: "0.68rem", color: "#666", letterSpacing: "0.05em", fontWeight: "700" },
  logoutBtn:     { background: "none", border: "none", color: "#555", cursor: "pointer", fontSize: "0.8rem", padding: "4px 6px", borderRadius: "4px" },
  main:          { padding: "2rem" },
};
