"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

export interface MsalUser {
  name: string;
  email: string;
  role: string;
  isAuthenticated: boolean;
}

interface MsalAuthContextType {
  user: MsalUser;
  login: () => Promise<void>;
  logout: () => void;
  switchRole: (role: string) => void;
}

const MsalAuthContext = createContext<MsalAuthContextType>({
  user: {
    name: "Alexandre Dubois",
    email: "adubois@worldbank.org",
    role: "Senior Procurement Specialist",
    isAuthenticated: true,
  },
  login: async () => {},
  logout: () => {},
  switchRole: () => {},
});

export const useMsalAuth = () => useContext(MsalAuthContext);

export function MsalAuthentication({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<MsalUser>({
    name: "Alexandre Dubois",
    email: "adubois@worldbank.org",
    role: "Senior Procurement Specialist",
    isAuthenticated: true,
  });

  const login = async () => {
    setUser((prev) => ({ ...prev, isAuthenticated: true }));
  };

  const logout = () => {
    setUser((prev) => ({ ...prev, isAuthenticated: false }));
  };

  const switchRole = (newRole: string) => {
    setUser((prev) => ({ ...prev, role: newRole }));
  };

  return (
    <MsalAuthContext.Provider value={{ user, login, logout, switchRole }}>
      {children}
    </MsalAuthContext.Provider>
  );
}
