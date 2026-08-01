/**
 * Punto de entrada. Decide dónde aterriza la app:
 *
 *   sin sesión        -> alta / acceso del adulto
 *   sin perfil        -> creación del perfil del niño
 *   todo listo        -> el reto de la semana
 */

import { Redirect } from 'expo-router';
import React, { useEffect } from 'react';

import { useChildren } from '../src/api/hooks';
import { Loading } from '../src/components/ui';
import { useSession } from '../src/context/SessionContext';

export default function Index() {
  const { ready, token, activeChildId, setActiveChild } = useSession();
  const { data: children, isLoading } = useChildren();

  useEffect(() => {
    if (children && children.length > 0 && !activeChildId) {
      setActiveChild(children[0].child_id);
    }
  }, [children, activeChildId, setActiveChild]);

  if (!ready) return <Loading />;
  if (!token) return <Redirect href="/login" />;
  if (isLoading || !children) return <Loading />;
  if (children.length === 0) return <Redirect href="/onboarding/child" />;
  if (!activeChildId) return <Loading />;

  return <Redirect href="/kid/week" />;
}
