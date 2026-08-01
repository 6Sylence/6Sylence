/**
 * Creación del perfil del niño.
 *
 * Se piden dos cosas y solo dos: un nombre —vale un mote— y una franja de
 * edad. No se pide fecha de nacimiento, ni foto, ni sexo, ni colegio. Todo lo
 * que no se pregunta es dato que no hay que proteger después.
 */

import { router } from 'expo-router';
import React, { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { ApiError } from '../../src/api/client';
import { useCreateChild } from '../../src/api/hooks';
import type { AgeBand } from '../../src/api/types';
import { Body, Button, Caption, Display, ErrorNote, Field, Screen } from '../../src/components/ui';
import { useSession } from '../../src/context/SessionContext';
import { colors, radii, spacing, type } from '../../src/theme';

const AVATARS = ['zorro', 'búho', 'nutria', 'erizo', 'ballena', 'mapache'];
const AGE_BANDS: AgeBand[] = ['3-4', '5-6'];

export default function CreateChild() {
  const { setActiveChild } = useSession();
  const createChild = useCreateChild();

  const [name, setName] = useState('');
  const [ageBand, setAgeBand] = useState<AgeBand>('3-4');
  const [avatar, setAvatar] = useState(AVATARS[0]);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    if (!name.trim()) {
      setError('Escribe un nombre');
      return;
    }
    setError(null);
    try {
      const child = await createChild.mutateAsync({
        name: name.trim(),
        age_band: ageBand,
        avatar_key: avatar,
      });
      await setActiveChild(child.child_id);
      router.replace('/kid/week');
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'No hemos podido conectar');
    }
  };

  return (
    <Screen>
      <View style={{ gap: spacing.sm, marginTop: spacing.lg }}>
        <Display>¿Quién juega?</Display>
        <Body>Con esto basta para empezar. Puedes cambiarlo cuando quieras.</Body>
      </View>

      <View style={{ gap: spacing.lg, marginTop: spacing.lg }}>
        <Field
          label="Nombre"
          value={name}
          onChangeText={setName}
          placeholder="Como le llames en casa"
          autoCapitalize="words"
        />

        <View style={{ gap: spacing.sm }}>
          <Text style={[type.label, { color: colors.ink }]}>Edad</Text>
          <View style={styles.row}>
            {AGE_BANDS.map((band) => (
              <Pressable
                key={band}
                onPress={() => setAgeBand(band)}
                style={[styles.chip, ageBand === band && styles.chipActive]}
              >
                <Text style={[type.label, ageBand === band && { color: '#FFFFFF' }]}>
                  {band} años
                </Text>
              </Pressable>
            ))}
          </View>
          <Caption>Solo la franja. No necesitamos la fecha de nacimiento.</Caption>
        </View>

        <View style={{ gap: spacing.sm }}>
          <Text style={[type.label, { color: colors.ink }]}>Su animal</Text>
          <View style={styles.row}>
            {AVATARS.map((option) => (
              <Pressable
                key={option}
                onPress={() => setAvatar(option)}
                style={[styles.chip, avatar === option && styles.chipActive]}
              >
                <Text style={[type.label, avatar === option && { color: '#FFFFFF' }]}>
                  {option}
                </Text>
              </Pressable>
            ))}
          </View>
        </View>

        {error ? <ErrorNote message={error} /> : null}
        <Button label="Empezar" onPress={submit} loading={createChild.isPending} />
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  chip: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: radii.pill,
    borderWidth: 2,
    borderColor: colors.border,
    backgroundColor: colors.surface,
    minHeight: 48,
    justifyContent: 'center',
  },
  chipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
});
