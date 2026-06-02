import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/**
 * Protege rotas por autenticação e por tipo de usuário.
 *
 * Uso:
 *   <ProtectedRoute>                        — só exige login
 *   <ProtectedRoute roles={["admin"]}>      — só admin acessa
 *   <ProtectedRoute roles={["discente","docente"]}> — discente ou docente
 */
export default function ProtectedRoute({ children, roles }) {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (roles && !roles.includes(user.tipo)) {
    return <Navigate to="/perfil" replace />;
  }

  return children;
}
