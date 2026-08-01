/**
 * Elección de recompensa.
 *
 * El momento del producto. Es la única decisión que el niño toma solo, así que
 * la pantalla no lleva verificación de adulto, no tiene opción "mejor",
 * ninguna opción cuesta dinero y ninguna está bloqueada. Tres cartas iguales
 * en jerarquía: se elige por gusto, no por valor.
 */

import { router, useLocalSearchParams } from 'expo-router';
import React, { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { useChooseReward, useWeek } from '../../src/api/hooks';
import type { RewardOption } from '../../src/api/types';
import {
  Body,
  Button,
  Caption,
  Display,
  ErrorNote,
  Loading,
  Screen,
  Title,
} from '../../src/components/ui';
import { useSession } from '../../src/context/SessionContext';
import { colors, radii, spacing, type } from '../../src/theme';

const KIND_LABEL: Record<RewardOption['kind'], string> = {
  personaje: 'Un amigo',
  historia: 'Un cuento',
  imprimible: 'Para imprimir',
};

export default function RewardScreen() {
  const { weekIndex } = useLocalSearchParams<{ weekIndex: string }>();
  const { activeChildId } = useSession();
  const parsedWeek = Number(weekIndex);

  const week = useWeek(activeChildId, Number.isFinite(parsedWeek) ? parsedWeek : null);
  const choose = useChooseReward(activeChildId, parsedWeek);
  const [selected, setSelected] = useState<string | null>(null);

  if (week.isLoading) return <Loading />;
  if (!week.data) {
    return (
      <Screen>
        <ErrorNote message="No hemos podido cargar los premios." />
        <Button label="Volver" onPress={() => router.back()} />
      </Screen>
    );
  }

  const { reward } = week.data;

  if (reward.claimed) {
    const chosen = reward.options.find((o) => o.option_id === reward.chosen_option_id);
    return (
      <Screen>
        <Display>Tu premio</Display>
        <View style={[styles.option, styles.optionChosen]}>
          <Caption>{chosen ? KIND_LABEL[chosen.kind] : ''}</Caption>
          <Title>{chosen?.title}</Title>
          <Body>{chosen?.description}</Body>
        </View>
        <Button label="Volver" onPress={() => router.replace('/kid/week')} />
      </Screen>
    );
  }

  const confirm = async () => {
    if (!selected) return;
    await choose.mutateAsync(selected);
    router.replace('/kid/week');
  };

  return (
    <Screen>
      <View style={{ gap: spacing.xs }}>
        <Display>¡Lo has conseguido!</Display>
        <Body>Elige tu premio de esta semana. Solo uno.</Body>
      </View>

      <View style={{ gap: spacing.md }}>
        {reward.options.map((option) => {
          const active = selected === option.option_id;
          return (
            <Pressable
              key={option.option_id}
              onPress={() => setSelected(option.option_id)}
              style={[styles.option, active && styles.optionActive]}
            >
              <Caption>{KIND_LABEL[option.kind]}</Caption>
              <Text style={[type.heading, { color: colors.ink }]}>{option.title}</Text>
              <Body>{option.description}</Body>
            </Pressable>
          );
        })}
      </View>

      {choose.error ? <ErrorNote message="No hemos podido guardar tu elección." /> : null}

      <Button
        label={selected ? '¡Este quiero!' : 'Elige uno'}
        disabled={!selected}
        loading={choose.isPending}
        onPress={confirm}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  option: {
    backgroundColor: colors.surface,
    borderRadius: radii.lg,
    borderWidth: 3,
    borderColor: colors.border,
    padding: spacing.lg,
    gap: spacing.xs,
    minHeight: 120,
    justifyContent: 'center',
  },
  optionActive: { borderColor: colors.primary, backgroundColor: '#FFF3EC' },
  optionChosen: { borderColor: colors.accent, backgroundColor: '#F2FAFA' },
});
