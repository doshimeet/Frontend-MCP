"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

export interface UserProfile {
  name: string;
  email: string;
  role: string;
  tenantId?: string;
}

export interface AuthContextType {
  appMode: "internal" | "external";
  isAuthenticated: boolean;
  user: UserProfile | null;
  login: () => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  appMode: "internal",
  isAuthenticated: true,
  user: null,
  login: () => {},
  logout: () => {},
});

export const useAuth = () => useContext(AuthContext);

export interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const appMode = (process.env.NEXT_PUBLIC_APP_MODE as "internal" | "external") || "internal";
  
  // Default authenticated mock profile for smooth local development
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(true);
  const [user, setUser] = useState<UserProfile | null>({
    name: "Enterprise Developer",
    email: "developer@worldbankgroup.org",
    role: "Lead Architect",
    tenantId: "wbg-cloud-tenant-01",
  });

  const login = () => {
    // Azure MSAL Entra ID integration hook point
    setIsAuthenticated(true);
    setUser({
      name: "Enterprise Developer",
      email: "developer@worldbankgroup.org",
      role: "Lead Architect",
      tenantId: "wbg-cloud-tenant-01",
    });
  };

  const logout = () => {
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ appMode, isAuthenticated, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;
