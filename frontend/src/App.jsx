import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

import Home     from "./pages/Home";
import Login    from "./pages/Login";
import Cadastro from "./pages/Cadastro";
import Perfil   from "./pages/Perfil";

// Discente
import ReservasSalaDiscente         from "./pages/discente/ReservasSala";
import ReservasEquipamentosDiscente from "./pages/discente/ReservasEquipamentos";

// Docente
import ReservasSalaDocente from "./pages/docente/ReservasSala";
import ManutencoesDocente  from "./pages/docente/Manutencoes";

// Admin
import AdminSalas       from "./pages/admin/Salas";
import AdminReservas    from "./pages/admin/Reservas";
import AdminManutencoes from "./pages/admin/Manutencoes";

import "./styles/global.css";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Públicas */}
          <Route path="/"         element={<Home />} />
          <Route path="/login"    element={<Login />} />
          <Route path="/cadastro" element={<Cadastro />} />

          {/* Perfil — todos */}
          <Route path="/perfil"
            element={<ProtectedRoute><Perfil /></ProtectedRoute>} />

          {/* Discente e Docente compartilham /reservas-de-sala */}
          <Route path="/reservas-de-sala"
            element={
              <ProtectedRoute roles={["discente", "docente"]}>
                <ReservasSalaDiscente />
              </ProtectedRoute>
            }
          />

          {/* Discente */}
          <Route path="/reservas-de-equipamento"
            element={<ProtectedRoute roles={["discente"]}><ReservasEquipamentosDiscente /></ProtectedRoute>} />

          {/* Docente */}
          <Route path="/solicitacoes-de-manutencao"
            element={<ProtectedRoute roles={["docente"]}><ManutencoesDocente /></ProtectedRoute>} />

          {/* Admin */}
          <Route path="/manutencoes"
            element={<ProtectedRoute roles={["admin"]}><AdminManutencoes /></ProtectedRoute>} />
          <Route path="/salas"
            element={<ProtectedRoute roles={["admin"]}><AdminSalas /></ProtectedRoute>} />
          <Route path="/reservas"
            element={<ProtectedRoute roles={["admin"]}><AdminReservas /></ProtectedRoute>} />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
