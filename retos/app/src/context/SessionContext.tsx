/**
 * Sesión del adulto y perfil de niño activo.
 *
 * El token va a `expo-secure-store` (Keystore en Android). El identificador
 * del niño activo va a almacenamiento normal: no es un secreto y no vale nada
 * fuera de una sesión autenticada.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';
import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import { request } from '../api/client';
import type { Child, TokenResponse } from '../api/types';

const TOKEN_KEY = 'retos.token';
const ACTIVE_CHILD_KEY = 'retos.activeChildId';

interface SessionValue {
  ready: boolean;
  token: string | null;
  activeChildId: string | null;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  setActiveChild: (childId: string | null) => Promise<void>;
  refreshActiveChild: () => Promise<Child | null>;
}

const SessionContext = createContext<SessionValue | null>(null);

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [ready, setReady] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [activeChildId, setActiveChildId] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      const [storedToken, storedChild] = await Promise.all([
        SecureStore.getItemAsync(TOKEN_KEY),
        AsyncStorage.getItem(ACTIVE_CHILD_KEY),
      ]);
      setToken(storedToken);
      setActiveChildId(storedChild);
      setReady(true);
    })();
  }, []);

  const persistToken = useCallback(async (value: string) => {
    await SecureStore.setItemAsync(TOKEN_KEY, value);
    setToken(value);
  }, []);

  const signIn = useCallback(
    async (email: string, password: string) => {
      const result = await request<TokenResponse>('/auth/login', {
        method: 'POST',
        body: { email, password },
      });
      await persistToken(result.access_token);
    },
    [persistToken],
  );

  const signUp = useCallback(
    async (email: string, password: string) => {
      const result = await request<TokenResponse>('/auth/register', {
        method: 'POST',
        body: { email, password },
      });
      await persistToken(result.access_token);
    },
    [persistToken],
  );

  const signOut = useCallback(async () => {
    await Promise.all([
      SecureStore.deleteItemAsync(TOKEN_KEY),
      AsyncStorage.removeItem(ACTIVE_CHILD_KEY),
    ]);
    setToken(null);
    setActiveChildId(null);
  }, []);

  const setActiveChild = useCallback(async (childId: string | null) => {
    if (childId) {
      await AsyncStorage.setItem(ACTIVE_CHILD_KEY, childId);
    } else {
      await AsyncStorage.removeItem(ACTIVE_CHILD_KEY);
    }
    setActiveChildId(childId);
  }, []);

  /** Elige el primer perfil si no hay ninguno activo. Devuelve el que quede. */
  const refreshActiveChild = useCallback(async (): Promise<Child | null> => {
    if (!token) return null;
    const list = await request<Child[]>('/children', { token });
    if (list.length === 0) {
      await setActiveChild(null);
      return null;
    }
    const current = list.find((child) => child.child_id === activeChildId);
    const next = current ?? list[0];
    if (next.child_id !== activeChildId) {
      await setActiveChild(next.child_id);
    }
    return next;
  }, [token, activeChildId, setActiveChild]);

  const value = useMemo<SessionValue>(
    () => ({
      ready,
      token,
      activeChildId,
      signIn,
      signUp,
      signOut,
      setActiveChild,
      refreshActiveChild,
    }),
    [ready, token, activeChildId, signIn, signUp, signOut, setActiveChild, refreshActiveChild],
  );

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession(): SessionValue {
  const value = useContext(SessionContext);
  if (!value) {
    throw new Error('useSession debe usarse dentro de SessionProvider');
  }
  return value;
}
