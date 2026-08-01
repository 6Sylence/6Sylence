/**
 * Zona de adultos.
 *
 * La verificación vive aquí y no en quien navega hasta aquí: así un enlace
 * directo o un botón de "atrás" no la esquivan.
 *
 * Visualmente sobria a propósito. Debe notarse que esto no es la app del niño.
 */

import { router } from 'expo-router';
import React, { useState } from 'react';
import { Linking, Pressable, StyleSheet, Text, View } from 'react-native';

import { useChildren, useMilestones, useParent, usePlan } from '../../src/api/hooks';
import { PRIVACY_POLICY_URL } from '../../src/config';
import { ParentalGate } from '../../src/components/ParentalGate';
import {
  Body,
  Button,
  Caption,
  Card,
  Display,
  Loading,
  Screen,
  Title,
} from '../../src/components/ui';
import { useSession } from '../../src/context/SessionContext';
import { colors, radii, spacing, type } from '../../src/theme';

const ENTITLEMENT_LABEL: Record<string, string> = {
  trialing: 'Prueba gratuita',
  active: 'Suscripción activa',
  expired: 'Suscripción caducada',
  none: 'Sin suscripción',
};

function formatDate(value: string | null): string {
  if (!value) return '—';
  return new Date(value).toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
}

export default function ParentsScreen() {
  const [unlocked, setUnlocked] = useState(false);
  const { activeChildId, setActiveChild, signOut } = useSession();

  const parent = useParent();
  const children = useChildren();
  const plan = usePlan(activeChildId);
  const milestones = useMilestones(activeChildId);

  if (!unlocked) {
    return (
      <Screen tone="parent" scroll={false}>
        <ParentalGate
          visible
          onCancel={() => router.back()}
          onSuccess={() => setUnlocked(true)}
        />
      </Screen>
    );
  }

  if (parent.isLoading || children.isLoading) return <Loading />;

  const entitlement = parent.data?.entitlement;

  return (
    <Screen tone="parent">
      <Display>Zona de adultos</Display>

      <Card style={styles.parentCard}>
        <Title>Suscripción</Title>
        <Body>
          {entitlement ? ENTITLEMENT_LABEL[entitlement.status] : '—'}
          {entitlement?.expires_at ? ` · hasta el ${formatDate(entitlement.expires_at)}` : ''}
        </Body>
        <Caption>
          La suscripción se gestiona desde Google Play, en Pagos y suscripciones. Desde ahí
          se cancela en cualquier momento.
        </Caption>
      </Card>

      {plan.data ? (
        <Card style={styles.parentCard}>
          <Title>Progreso de {plan.data.child.name}</Title>
          <Body>
            Semana {plan.data.current_week} de {plan.data.total_weeks} ·{' '}
            {plan.data.completed_weeks.length} completadas
          </Body>
          {plan.data.catchup_weeks.length > 0 ? (
            <Caption>
              Semanas pendientes: {plan.data.catchup_weeks.join(', ')}. Siguen disponibles,
              no caducan.
            </Caption>
          ) : null}
          {plan.data.next_unlock_at ? (
            <Caption>Siguiente semana: {formatDate(plan.data.next_unlock_at)}</Caption>
          ) : null}
        </Card>
      ) : null}

      <Card style={styles.parentCard}>
        <Title>Recompensas de hito</Title>
        {milestones.data && milestones.data.length > 0 ? (
          milestones.data.map((milestone) => (
            <View key={milestone.milestone_id} style={styles.milestone}>
              <Text style={[type.label, { color: colors.parentInk }]}>
                Semana {milestone.week_index} · {milestone.code}
              </Text>
              <Caption>
                {milestone.status === 'canjeado' ? 'Canjeado' : 'Pendiente de canjear'}
              </Caption>
            </View>
          ))
        ) : (
          <Body>Todavía ninguna. Llegan al completar las semanas 4, 8 y 12.</Body>
        )}
        <Caption>
          El envío se solicita en la web con este código. No se piden direcciones dentro de
          la app.
        </Caption>
      </Card>

      <Card style={styles.parentCard}>
        <Title>Perfiles</Title>
        {children.data?.map((child) => (
          <Pressable
            key={child.child_id}
            onPress={() => setActiveChild(child.child_id)}
            style={[styles.childRow, child.child_id === activeChildId && styles.childRowActive]}
          >
            <Text style={[type.label, { color: colors.parentInk }]}>
              {child.name} · {child.age_band} años
            </Text>
            {child.child_id === activeChildId ? <Caption>Activo</Caption> : null}
          </Pressable>
        ))}
        <Button
          label="Añadir otro perfil"
          variant="ghost"
          onPress={() => router.push('/onboarding/child')}
        />
      </Card>

      <Card style={styles.parentCard}>
        <Title>Privacidad</Title>
        <Body>
          De tu hijo guardamos su nombre y su franja de edad. Nada más. Las fotos con las
          que validas los retos no salen de este teléfono: la app nunca las envía ni las
          almacena.
        </Body>
        <Button
          label="Leer la política de privacidad"
          variant="ghost"
          onPress={() => Linking.openURL(PRIVACY_POLICY_URL)}
        />
      </Card>

      <Button label="Volver" variant="ghost" onPress={() => router.replace('/kid/week')} />
      <Button
        label="Cerrar sesión"
        variant="ghost"
        onPress={async () => {
          await signOut();
          router.replace('/login');
        }}
      />
      {/* Google Play exige poder borrar la cuenta desde dentro de la app. */}
      <Button
        label="Borrar mi cuenta"
        variant="danger"
        onPress={() => router.push('/parents/borrar-cuenta')}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  parentCard: {
    backgroundColor: colors.surface,
    borderColor: colors.parentBorder,
    gap: spacing.sm,
  },
  milestone: {
    borderTopWidth: 1,
    borderTopColor: colors.parentBorder,
    paddingTop: spacing.sm,
    gap: 2,
  },
  childRow: {
    padding: spacing.md,
    borderRadius: radii.sm,
    borderWidth: 1,
    borderColor: colors.parentBorder,
    gap: 2,
  },
  childRowActive: { borderColor: colors.accent, backgroundColor: '#F2FAFA' },
});
