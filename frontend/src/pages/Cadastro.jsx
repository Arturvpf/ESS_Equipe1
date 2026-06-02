import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api } from "../api/client";

export default function Cadastro() {
  const [form, setForm] = useState({
    nome: "", cpf: "", senha: "", tipo: "discente",
    matricula: "", curso: "", siape: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  function set(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const payload = { nome: form.nome, cpf: form.cpf, senha: form.senha, tipo: form.tipo };
      if (form.tipo === "discente") {
        payload.matricula = form.matricula;
        payload.curso = form.curso;
      } else {
        payload.siape = form.siape;
      }
      await api.post("/users/", payload);
      navigate("/login");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={s.wrapper}>
      <div style={s.bg} aria-hidden="true">
        <div style={s.blob1} />
        <div style={s.blob2} />
      </div>

      <div style={s.card}>
        <Link to="/" style={s.brand}>Salla</Link>
        <p style={s.subtitle}>Crie sua conta universitária</p>

        <form onSubmit={handleSubmit} style={s.form}>

          <Field label="Nome completo">
            <input style={s.input} value={form.nome} onChange={set("nome")} required />
          </Field>

          <Field label="CPF">
            <input style={s.input} placeholder="000.000.000-00" value={form.cpf} onChange={set("cpf")} required />
          </Field>

          {/* Tipo */}
          <div style={s.toggleRow}>
            {["discente", "docente"].map((tipo) => (
              <button
                key={tipo}
                type="button"
                style={{ ...s.toggleBtn, ...(form.tipo === tipo ? s.toggleActive : {}) }}
                onClick={() => setForm((f) => ({ ...f, tipo }))}
              >
                {tipo === "discente" ? "Discente" : "Docente"}
              </button>
            ))}
          </div>

          {form.tipo === "discente" && (
            <div style={s.grid2}>
              <Field label="Matrícula">
                <input style={s.input} value={form.matricula} onChange={set("matricula")} required />
              </Field>
              <Field label="Curso">
                <input style={s.input} value={form.curso} onChange={set("curso")} required />
              </Field>
            </div>
          )}

          {form.tipo === "docente" && (
            <Field label="SIAPE">
              <input style={s.input} value={form.siape} onChange={set("siape")} required />
            </Field>
          )}

          <Field label="Senha">
            <input
              style={s.input}
              type="password"
              placeholder="Mínimo 6 caracteres"
              value={form.senha}
              onChange={set("senha")}
              minLength={6}
              maxLength={128}
              required
            />
          </Field>

          {error && <p style={s.error}>{error}</p>}

          <button type="submit" style={s.btn} disabled={loading}>
            {loading ? "Cadastrando..." : "Criar conta"}
          </button>
        </form>

        <p style={s.footer}>
          Já tem conta?{" "}
          <Link to="/login" style={s.link}>Entrar</Link>
        </p>
      </div>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
      <label style={{
        fontSize: "0.78rem", fontWeight: "600", color: "#aaa",
        textTransform: "uppercase", letterSpacing: "0.05em",
      }}>
        {label}
      </label>
      {children}
    </div>
  );
}

const s = {
  wrapper: { minHeight: "100vh", background: "#0f1117", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "system-ui, sans-serif", position: "relative", overflow: "hidden", padding: "2rem 1rem" },
  bg:      { position: "absolute", inset: 0, pointerEvents: "none" },
  blob1:   { position: "absolute", top: "-100px", right: "-100px", width: "380px", height: "380px", borderRadius: "50%", background: "#4361ee", opacity: 0.07 },
  blob2:   { position: "absolute", bottom: "-80px", left: "-80px", width: "280px", height: "280px", borderRadius: "50%", background: "#4361ee", opacity: 0.05 },
  card:    { position: "relative", zIndex: 10, background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "16px", padding: "2.5rem 2rem", width: "100%", maxWidth: "420px", backdropFilter: "blur(12px)" },
  brand:   { display: "block", fontSize: "1.8rem", fontWeight: "700", color: "#fff", textDecoration: "none", fontFamily: "Georgia, serif", letterSpacing: "-0.03em", marginBottom: "0.25rem" },
  subtitle: { fontSize: "0.85rem", color: "#666", marginBottom: "1.75rem" },
  form:    { display: "flex", flexDirection: "column", gap: "1rem" },
  toggleRow: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem", marginBottom: "0.25rem" },
  toggleBtn: { padding: "8px", borderRadius: "8px", border: "1px solid rgba(255,255,255,0.1)", background: "transparent", color: "#666", fontSize: "0.88rem", fontWeight: "600", cursor: "pointer" },
  toggleActive: { background: "rgba(67,97,238,0.2)", border: "1px solid #4361ee", color: "#7b96ff" },
  grid2:   { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" },
  input:   { background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px", padding: "10px 14px", color: "#f0f0f0", fontSize: "0.92rem", outline: "none", width: "100%", boxSizing: "border-box" },
  error:   { color: "#ff6b6b", fontSize: "0.82rem", margin: 0 },
  btn:     { marginTop: "0.25rem", background: "#4361ee", color: "#fff", border: "none", borderRadius: "8px", padding: "11px", fontSize: "0.95rem", fontWeight: "700", cursor: "pointer", width: "100%" },
  footer:  { marginTop: "1.5rem", textAlign: "center", fontSize: "0.85rem", color: "#666" },
  link:    { color: "#7b96ff", textDecoration: "none", fontWeight: "600" },
};
