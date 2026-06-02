import React, { useEffect, useState, useCallback } from "react";
import { api } from "../../api/client";
import { useAuth } from "../../context/AuthContext";
import Navbar from "../../components/Navbar";

const STATUS = {
  pending:   { label: "Pendente",   badge: s_badge("ffd166", "333")    },
  confirmed: { label: "Confirmada", badge: s_badge("06d6a0", "fff")    },
  denied:    { label: "Negada",     badge: s_badge("e63946", "fff")    },
  completed: { label: "Concluída",  badge: s_badge("4361ee", "fff")    },
};

function s_badge(bg, color) {
  return {
    display: "inline-block", padding: "2px 10px", borderRadius: "12px",
    fontSize: "0.72rem", fontWeight: "700",
    background: `#${bg}`, color: `#${color}`,
  };
}

function toIso(datetimeLocal) {
  return datetimeLocal.length === 16 ? datetimeLocal + ":00" : datetimeLocal;
}

function formatDate(isoStr) {
  const [y, m, d] = isoStr.split("T")[0].split("-");
  return `${d}/${m}/${y}`;
}

function formatTime(isoStr) {
  return isoStr.split("T")[1]?.slice(0, 5) ?? "";
}

// ── Nova Reserva ────────────────────────────────────────────────────────────

function NovaReservaForm({ authParams, onCreated }) {
  const [rooms, setRooms] = useState([]);
  const [roomsError, setRoomsError] = useState(false);
  const [form, setForm] = useState({ room: "", start_time: "", end_time: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    api.get("/api/rooms/?limit=100")
      .then(({ rooms }) => {
        setRooms(rooms);
        if (rooms.length > 0) setForm((f) => ({ ...f, room: rooms[0].name }));
      })
      .catch(() => setRoomsError(true));
  }, []);

  function set(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      await api.post(`/api/reservations/?${authParams()}`, {
        room: form.room,
        start_time: toIso(form.start_time),
        end_time: toIso(form.end_time),
      });
      setSuccess("Reserva criada com sucesso! Aguardando confirmação do administrador.");
      setForm({ room: rooms.length > 0 ? rooms[0].name : "", start_time: "", end_time: "" });
      onCreated();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={s.card}>
      <h2 style={s.cardTitle}>Nova Reserva</h2>
      <form onSubmit={handleSubmit} style={s.form}>
        <div style={s.grid2}>
          <div style={s.field}>
            <label style={s.label} htmlFor="nova-room">Sala</label>
            {roomsError ? (
              <input id="nova-room" style={s.input} value={form.room}
                onChange={set("room")} placeholder="Ex: D005" required />
            ) : (
              <select id="nova-room" style={s.input} value={form.room}
                onChange={set("room")} required>
                {rooms.map((r) => (
                  <option key={r.name} value={r.name}>{r.name}</option>
                ))}
              </select>
            )}
          </div>
          <div />
          <div style={s.field}>
            <label style={s.label} htmlFor="nova-start">Início</label>
            <input id="nova-start" style={s.input} type="datetime-local"
              value={form.start_time} onChange={set("start_time")} required />
          </div>
          <div style={s.field}>
            <label style={s.label} htmlFor="nova-end">Fim</label>
            <input id="nova-end" style={s.input} type="datetime-local"
              value={form.end_time} onChange={set("end_time")} required />
          </div>
        </div>
        {error   && <p style={s.error}>{error}</p>}
        {success && <p style={s.success}>{success}</p>}
        <div style={{ marginTop: "0.75rem" }}>
          <button type="submit" style={s.btn} disabled={loading}>
            {loading ? "Confirmando..." : "Confirmar reserva"}
          </button>
        </div>
      </form>
    </div>
  );
}

// ── Modal de Edição ─────────────────────────────────────────────────────────

function EditarModal({ reserva, authParams, onSaved, onClose }) {
  const [rooms, setRooms] = useState([]);
  const [roomsError, setRoomsError] = useState(false);
  const [form, setForm] = useState({
    room: reserva.room,
    start_time: reserva.start_time.slice(0, 16),
    end_time: reserva.end_time.slice(0, 16),
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/api/rooms/?limit=100")
      .then(({ rooms }) => setRooms(rooms))
      .catch(() => setRoomsError(true));
  }, []);

  function set(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    const updates = {};
    if (form.room !== reserva.room) updates.room = form.room;
    if (toIso(form.start_time) !== reserva.start_time) updates.start_time = toIso(form.start_time);
    if (toIso(form.end_time) !== reserva.end_time) updates.end_time = toIso(form.end_time);
    if (Object.keys(updates).length === 0) { onClose(); return; }
    setLoading(true);
    try {
      await api.put(`/api/reservations/${reserva.id}?${authParams()}`, updates);
      onSaved();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={s.overlay}>
      <div style={s.modal}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1.25rem" }}>
          <h2 style={s.modalTitle}>Editar Reserva</h2>
          <button style={s.closeBtn} onClick={onClose} type="button">✕</button>
        </div>
        <form onSubmit={handleSubmit} style={s.form}>
          <div style={s.field}>
            <label style={s.label} htmlFor="edit-room">Sala</label>
            {roomsError ? (
              <input id="edit-room" style={s.input} value={form.room} onChange={set("room")} required />
            ) : (
              <select id="edit-room" style={s.input} value={form.room} onChange={set("room")} required>
                {rooms.map((r) => <option key={r.name} value={r.name}>{r.name}</option>)}
                {!rooms.find((r) => r.name === form.room) && (
                  <option value={form.room}>{form.room}</option>
                )}
              </select>
            )}
          </div>
          <div style={s.field}>
            <label style={s.label} htmlFor="edit-start">Início</label>
            <input id="edit-start" style={s.input} type="datetime-local"
              value={form.start_time} onChange={set("start_time")} required />
          </div>
          <div style={s.field}>
            <label style={s.label} htmlFor="edit-end">Fim</label>
            <input id="edit-end" style={s.input} type="datetime-local"
              value={form.end_time} onChange={set("end_time")} required />
          </div>
          {error && <p style={s.error}>{error}</p>}
          <div style={{ display: "flex", gap: "0.75rem", marginTop: "0.75rem" }}>
            <button type="submit" style={s.btn} disabled={loading}>
              {loading ? "Salvando..." : "Salvar alterações"}
            </button>
            <button type="button" style={s.btnDanger} onClick={onClose}>Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ── Linha da tabela ─────────────────────────────────────────────────────────

function ReservaRow({ reserva, onEdit, onCancel }) {
  const info      = STATUS[reserva.status] ?? { label: reserva.status, badge: {} };
  const isPending = reserva.status === "pending";

  return (
    <tr style={s.tr}>
      <td style={s.td}>{reserva.room}</td>
      <td style={s.td}>{formatDate(reserva.start_time)}</td>
      <td style={s.td}>{formatTime(reserva.start_time)}</td>
      <td style={s.td}>{formatTime(reserva.end_time)}</td>
      <td style={s.td}><span style={info.badge}>{info.label}</span></td>
      <td style={{ ...s.td, display: "flex", gap: "0.4rem" }}>
        {isPending && (
          <>
            <button style={s.btnSm} type="button" onClick={() => onEdit(reserva)}>
              Editar
            </button>
            <button style={{ ...s.btnSm, ...s.btnSmDanger }} type="button" onClick={() => onCancel(reserva)}>
              Cancelar
            </button>
          </>
        )}
      </td>
    </tr>
  );
}

// ── Página principal ────────────────────────────────────────────────────────

export default function ReservasSala() {
  const { user } = useAuth();
  const [reservas, setReservas]     = useState([]);
  const [loadingList, setLoadingList] = useState(true);
  const [listError, setListError]   = useState("");
  const [filtroStatus, setFiltroStatus] = useState("");
  const [editando, setEditando]     = useState(null);
  const [feedback, setFeedback]     = useState({ type: "", text: "" });

  function authParams() {
    return new URLSearchParams({
      user_cpf:   user.cpf,
      user_nome:  user.nome,
      user_senha: user.senha,
    }).toString();
  }

  const fetchReservas = useCallback(async () => {
    setLoadingList(true);
    setListError("");
    try {
      const qs = filtroStatus
        ? `user_cpf=${user.cpf}&status=${filtroStatus}`
        : `user_cpf=${user.cpf}`;
      const data = await api.get(`/api/reservations/my-reservations?${qs}`);
      setReservas(data);
    } catch (err) {
      setListError(err.message);
    } finally {
      setLoadingList(false);
    }
  }, [user.cpf, filtroStatus]);

  useEffect(() => { fetchReservas(); }, [fetchReservas]);

  function showFeedback(type, text) {
    setFeedback({ type, text });
    setTimeout(() => setFeedback({ type: "", text: "" }), 5000);
  }

  function handleEdited() {
    setEditando(null);
    showFeedback("success", "Reserva atualizada com sucesso!");
    fetchReservas();
  }

  async function handleCancel(reserva) {
    if (!window.confirm(`Cancelar a reserva da sala "${reserva.room}"?`)) return;
    try {
      await api.delete(`/api/reservations/${reserva.id}?${authParams()}`);
      showFeedback("success", "Reserva cancelada com sucesso.");
      fetchReservas();
    } catch (err) {
      showFeedback("error", err.message);
    }
  }

  return (
    <Navbar>
      {editando && (
        <EditarModal
          reserva={editando}
          authParams={authParams}
          onSaved={handleEdited}
          onClose={() => setEditando(null)}
        />
      )}

      <h1 style={s.pageTitle}>Reservas de Sala</h1>

      <NovaReservaForm authParams={authParams} onCreated={fetchReservas} />

      <div style={s.card}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1.25rem" }}>
          <h2 style={s.cardTitle}>Minhas Reservas</h2>
          <select style={{ ...s.input, width: "auto", padding: "5px 10px", fontSize: "0.82rem" }}
            value={filtroStatus} onChange={(e) => setFiltroStatus(e.target.value)}>
            <option value="">Todos os status</option>
            {Object.entries(STATUS).map(([key, { label }]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </div>

        {feedback.text && (
          <p style={{ ...(feedback.type === "success" ? s.success : s.error), marginBottom: "0.75rem" }}>
            {feedback.text}
          </p>
        )}

        {loadingList && <p style={s.muted}>Carregando reservas...</p>}
        {listError   && <p style={s.error}>{listError}</p>}

        {!loadingList && !listError && (
          reservas.length === 0 ? (
            <p style={s.muted}>Você ainda não tem reservas.</p>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table style={s.table}>
                <thead>
                  <tr>
                    {["Sala", "Data", "Início", "Fim", "Status", "Ações"].map((h) => (
                      <th key={h} style={s.th}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {reservas.map((r) => (
                    <ReservaRow key={r.id} reserva={r}
                      onEdit={setEditando} onCancel={handleCancel} />
                  ))}
                </tbody>
              </table>
            </div>
          )
        )}
      </div>
    </Navbar>
  );
}

const s = {
  pageTitle:  { fontSize: "1.4rem", fontWeight: "700", color: "#1e3a5f", marginBottom: "1.5rem" },
  card:       { background: "#fff", borderRadius: "10px", padding: "1.5rem", marginBottom: "1.25rem", boxShadow: "0 1px 4px rgba(0,0,0,.07)" },
  cardTitle:  { fontSize: "1rem", fontWeight: "700", color: "#1a1a2e", margin: 0 },
  modalTitle: { fontSize: "1rem", fontWeight: "700", color: "#1a1a2e", margin: 0 },
  form:       { display: "flex", flexDirection: "column", gap: "0.85rem" },
  grid2:      { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" },
  field:      { display: "flex", flexDirection: "column", gap: "0.35rem" },
  label:      { fontSize: "0.78rem", fontWeight: "600", color: "#555", textTransform: "uppercase", letterSpacing: "0.04em" },
  input:      { width: "100%", padding: "8px 12px", border: "1px solid #d0d0d0", borderRadius: "6px", fontSize: "0.92rem", boxSizing: "border-box", background: "#fff", color: "#1a1a2e" },
  btn:        { background: "#4361ee", color: "#fff", border: "none", borderRadius: "6px", padding: "9px 18px", fontSize: "0.9rem", fontWeight: "700", cursor: "pointer" },
  btnDanger:  { background: "#e63946", color: "#fff", border: "none", borderRadius: "6px", padding: "9px 18px", fontSize: "0.9rem", fontWeight: "700", cursor: "pointer" },
  btnSm:      { background: "#4361ee", color: "#fff", border: "none", borderRadius: "5px", padding: "4px 12px", fontSize: "0.8rem", fontWeight: "600", cursor: "pointer" },
  btnSmDanger: { background: "#e63946" },
  error:      { color: "#e63946", fontSize: "0.84rem", margin: 0 },
  success:    { color: "#2dc653", fontSize: "0.84rem", margin: 0 },
  muted:      { color: "#888", fontSize: "0.88rem" },
  table:      { width: "100%", borderCollapse: "collapse", fontSize: "0.88rem" },
  th:         { textAlign: "left", padding: "8px 10px", background: "#f0f0f5", fontSize: "0.78rem", fontWeight: "700", color: "#444" },
  td:         { padding: "8px 10px", borderBottom: "1px solid #eee", verticalAlign: "middle" },
  tr:         {},
  overlay:    { position: "fixed", inset: 0, background: "rgba(0,0,0,.45)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 200 },
  modal:      { background: "#fff", borderRadius: "12px", padding: "1.75rem", width: "100%", maxWidth: "460px", boxShadow: "0 8px 32px rgba(0,0,0,.18)" },
  closeBtn:   { background: "none", border: "none", fontSize: "1rem", cursor: "pointer", color: "#888", padding: "2px 6px", borderRadius: "4px" },
};
