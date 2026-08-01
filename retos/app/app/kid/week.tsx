/**
 * Pantalla principal: el reto de esta semana.
 *
 * Es la que ve el niño. Reglas de diseño que hay que mantener al iterar:
 * texto grande, tres tarjetas y nada más; ninguna cuenta atrás; ningún
 * contador de días perdidos; ninguna comparación. Lo que no está hecho no se
 * pinta en rojo, se pinta en gris.
 */

import { router } from 'expo-router';
import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { useCurrentWeek, usePlan } from '../../src/api/hooks';
import type { ActivityStatus } from '../../src/api/types';
import {
  Body,
  Button,
  Caption,
  Card,
  Display,
  ErrorNote,
  Loading,
  ProgressPips,
  Screen,
  Title,
} from '../../src/components/ui';
import { useSession } from '../../src/context/SessionContext';
import { colors, radii, spacing, type } from '../../src/theme';

function formatDate(value: string | null): string {
  if (!value) return '';
  return new Date(value).toLocaleDateString('es-ES', { day: 'numeric', month: 'long' });
}

function ActivityRow({ item, onPress }: { item: ActivityStatus; onPress: () => void }) {
  return (
    <Card onPress={onPress} style={item.completed ? styles.activityDone : undefined}>
      <View style={styles.activityHeader}>
        <View style={[styles.marker, item.completed && styles.markerDone]}>
          <Text style={styles.markerText}>{item.completed ? '✓' : ''}</Text>
        </View>
        <View style={styles.activityText}>
          <Text style={[type.heading, { color: colors.ink }]}>{item.activity.title}</Text>
          <Caption>{item.activity.est_minutes} minutos · sin pantalla</Caption>
        </View>
      </View>
    </Card>
  );
}

export default function WeekScreen() {
  const { activeChildId } = useSession();
  const plan = usePlan(activeChildId);
  const week = useCurrentWeek(activeChildId);

  if (plan.isLoading || week.isLoading) return <Loading />;
  if (plan.error || week.error || !plan.data || !week.data) {
    return (
      <Screen>
        <ErrorNote message="No hemos podido cargar el reto. Comprueba la conexión." />
        <Button label="Reintentar" onPress={() => { plan.refetch(); week.refetch(); }} />
      </Screen>
    );
  }

  const { data: planData } = plan;
  const { data: weekData } = week;
  const allDoneWaiting =
    weekData.week_completed && planData.unlocked_week < planData.total_weeks;

  return (
    <Screen>
      <View style={styles.topBar}>
        <View>
          <Caption>{planData.child.name}</Caption>
          <Text style={[type.label, { color: colors.inkSoft }]}>
            Semana {weekData.week_index} de {planData.total_weeks}
          </Text>
        </View>
        {/* Discreto a propósito: no queremos que el niño entre aquí. La
            verificación de adulto la hace la propia pantalla de destino. */}
        <Pressable onPress={() => router.push('/parents')} style={styles.parentButton}>
          <Text style={[type.caption, { color: colors.inkSoft }]}>Adultos</Text>
        </Pressable>
      </View>

      <View style={{ gap: spacing.xs }}>
        <Display>{weekData.title}</Display>
        <Body>{weekData.subtitle}</Body>
      </View>

      {weekData.accessible ? (
        <>
          <View style={styles.progressRow}>
            <ProgressPips total={weekData.activities.length} done={weekData.completed_count} />
            <Caption>
              {weekData.completed_count} de {weekData.activities_required} para completar
            </Caption>
          </View>

          <View style={{ gap: spacing.md }}>
            {weekData.activities.map((item) => (
              <ActivityRow
                key={item.activity.activity_id}
                item={item}
                onPress={() =>
                  router.push({
                    pathname: '/kid/activity/[activityId]',
                    params: {
                      activityId: item.activity.activity_id,
                      weekIndex: String(weekData.week_index),
                    },
                  })
                }
              />
            ))}
          </View>

          {weekData.week_completed && !weekData.reward.claimed ? (
            <Button
              label="¡Elige tu premio!"
              onPress={() =>
                router.push({
                  pathname: '/kid/reward',
                  params: { weekIndex: String(weekData.week_index) },
                })
              }
            />
          ) : null}

          {weekData.reward.claimed ? (
            <Card style={styles.rewardCard}>
              <Title>Premio elegido</Title>
              <Body>
                {weekData.reward.options.find(
                  (option) => option.option_id === weekData.reward.chosen_option_id,
                )?.title ?? 'Tu premio de esta semana'}
              </Body>
            </Card>
          ) : null}

          {allDoneWaiting && weekData.reward.claimed ? (
            <Caption>
              Has terminado esta semana. La siguiente llega el{' '}
              {formatDate(planData.next_unlock_at)}.
            </Caption>
          ) : null}

          {planData.catchup_weeks.length > 0 ? (
            <Caption>
              Tienes {planData.catchup_weeks.length} semana
              {planData.catchup_weeks.length > 1 ? 's' : ''} guardada
              {planData.catchup_weeks.length > 1 ? 's' : ''} para cuando quieras. No caducan.
            </Caption>
          ) : null}
        </>
      ) : (
        <Card style={{ gap: spacing.md }}>
          <Title>Todavía no</Title>
          <Body>{weekData.locked_reason}</Body>
          <Button
            label="Zona de adultos"
            variant="ghost"
            onPress={() => router.push('/parents')}
          />
        </Card>
      )}
    </Screen>
  );
}

const styles = StyleSheet.create({
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  parentButton: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: radii.pill,
    borderWidth: 1,
    borderColor: colors.border,
  },
  progressRow: { gap: spacing.sm },
  activityHeader: { flexDirection: 'row', alignItems: 'center', gap: spacing.md },
  activityText: { flex: 1, gap: 2 },
  activityDone: { borderColor: colors.done, backgroundColor: '#F3FAF4' },
  marker: {
    width: 40,
    height: 40,
    borderRadius: radii.pill,
    borderWidth: 2,
    borderColor: colors.border,
    alignItems: 'center',
    justifyContent: 'center',
  },
  markerDone: { backgroundColor: colors.done, borderColor: colors.done },
  markerText: { color: '#FFFFFF', fontSize: 20, fontWeight: '800' },
  rewardCard: { borderColor: colors.accent, backgroundColor: '#F2FAFA' },
});
