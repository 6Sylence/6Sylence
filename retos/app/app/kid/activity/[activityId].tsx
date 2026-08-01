/**
 * Detalle de una actividad y su validación.
 *
 * El botón de "hecho" abre la verificación de adulto. Es lo que sostiene la
 * promesa del producto: quien confirma que el reto está hecho es una persona
 * adulta que lo ha visto, no el niño pulsando.
 *
 * Si el adulto quiere hacer una foto del momento, que la haga con su cámara.
 * La app no la pide, no la sube y no la guarda.
 */

import { router, useLocalSearchParams } from 'expo-router';
import React, { useState } from 'react';
import { StyleSheet, View } from 'react-native';

import { useCompleteActivity, useUndoActivity, useWeek } from '../../../src/api/hooks';
import { ParentalGate } from '../../../src/components/ParentalGate';
import {
  Body,
  Button,
  Caption,
  Card,
  Display,
  ErrorNote,
  Loading,
  Screen,
  Title,
} from '../../../src/components/ui';
import { useSession } from '../../../src/context/SessionContext';
import { spacing } from '../../../src/theme';

export default function ActivityScreen() {
  const { activityId, weekIndex } = useLocalSearchParams<{
    activityId: string;
    weekIndex: string;
  }>();
  const { activeChildId } = useSession();
  const parsedWeek = Number(weekIndex);

  const week = useWeek(activeChildId, Number.isFinite(parsedWeek) ? parsedWeek : null);
  const complete = useCompleteActivity(activeChildId, parsedWeek);
  const undo = useUndoActivity(activeChildId, parsedWeek);
  const [gateOpen, setGateOpen] = useState(false);

  if (week.isLoading) return <Loading />;

  const item = week.data?.activities.find((a) => a.activity.activity_id === activityId);
  if (!item) {
    return (
      <Screen>
        <ErrorNote message="No encontramos esta actividad." />
        <Button label="Volver" onPress={() => router.back()} />
      </Screen>
    );
  }

  const { activity, completed } = item;

  const confirmDone = async () => {
    setGateOpen(false);
    await complete.mutateAsync(activity.activity_id);
    router.back();
  };

  return (
    <Screen>
      <Display>{activity.title}</Display>

      <Card style={{ gap: spacing.md }}>
        <Title>Qué hacer</Title>
        <Body>{activity.instructions}</Body>
        <Caption>Unos {activity.est_minutes} minutos.</Caption>
      </Card>

      <Card style={{ gap: spacing.sm }}>
        <Title>Qué necesitáis</Title>
        {activity.materials.length > 0 ? (
          activity.materials.map((material) => <Body key={material}>· {material}</Body>)
        ) : (
          <Body>Nada. Solo vosotros.</Body>
        )}
      </Card>

      {complete.error || undo.error ? (
        <ErrorNote message="No hemos podido guardarlo. Inténtalo otra vez." />
      ) : null}

      <View style={styles.actions}>
        {completed ? (
          <>
            <Card style={{ gap: spacing.xs }}>
              <Title>¡Hecho!</Title>
              <Body>Esta actividad ya está validada.</Body>
            </Card>
            <Button
              label="Deshacer"
              variant="ghost"
              loading={undo.isPending}
              onPress={async () => {
                await undo.mutateAsync(activity.activity_id);
                router.back();
              }}
            />
          </>
        ) : (
          <Button
            label="Ya lo hemos hecho"
            loading={complete.isPending}
            onPress={() => setGateOpen(true)}
          />
        )}
        <Button label="Volver" variant="ghost" onPress={() => router.back()} />
      </View>

      <ParentalGate
        visible={gateOpen}
        title="¿Lo ha hecho de verdad?"
        description="Que lo confirme un adulto que lo haya visto."
        onCancel={() => setGateOpen(false)}
        onSuccess={confirmDone}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  actions: { gap: spacing.md, marginTop: spacing.md },
});
