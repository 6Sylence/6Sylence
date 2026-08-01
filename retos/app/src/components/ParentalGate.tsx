/**
 * Verificación de adulto.
 *
 * Google Play exige una barrera antes de cualquier zona de compra, enlace
 * externo o ajuste en una app dirigida a menores. La pregunta va escrita con
 * números en letra a propósito: un niño de 3 a 6 años no lee "catorce" ni
 * resuelve la suma, y no basta con pulsar al azar.
 *
 * Se usa en dos sitios: al entrar en la zona de adultos y al validar un reto,
 * que es lo que garantiza que quien confirma que el niño lo ha hecho es un
 * adulto.
 */

import React, { useMemo, useState } from 'react';
import { Modal, StyleSheet, View } from 'react-native';

import { colors, radii, spacing } from '../theme';
import { Body, Button, Caption, Field, Title } from './ui';

const NUMBER_WORDS = [
  'cero', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve',
  'diez', 'once', 'doce', 'trece', 'catorce', 'quince', 'dieciséis', 'diecisiete',
  'dieciocho', 'diecinueve',
];

function buildChallenge() {
  const a = 3 + Math.floor(Math.random() * 7); // 3..9
  const b = 3 + Math.floor(Math.random() * 7);
  return { question: `${NUMBER_WORDS[a]} + ${NUMBER_WORDS[b]}`, answer: a + b };
}

export function ParentalGate({
  visible,
  title = 'Un momento, adultos',
  description = 'Resuelve la suma para continuar.',
  onSuccess,
  onCancel,
}: {
  visible: boolean;
  title?: string;
  description?: string;
  onSuccess: () => void;
  onCancel: () => void;
}) {
  const challenge = useMemo(buildChallenge, [visible]);
  const [value, setValue] = useState('');
  const [failed, setFailed] = useState(false);

  const submit = () => {
    if (Number(value.trim()) === challenge.answer) {
      setValue('');
      setFailed(false);
      onSuccess();
    } else {
      setFailed(true);
      setValue('');
    }
  };

  const cancel = () => {
    setValue('');
    setFailed(false);
    onCancel();
  };

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={cancel}>
      <View style={styles.backdrop}>
        <View style={styles.sheet}>
          <Title>{title}</Title>
          <Body>{description}</Body>
          <Title style={styles.question}>{challenge.question}</Title>
          <Field
            label="Resultado"
            value={value}
            onChangeText={setValue}
            keyboardType="default"
            placeholder="Escribe el número"
          />
          {failed ? <Caption>No es correcto. Inténtalo otra vez.</Caption> : null}
          <Button label="Continuar" onPress={submit} />
          <Button label="Cancelar" variant="ghost" onPress={cancel} />
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(20,16,12,0.55)',
    justifyContent: 'center',
    padding: spacing.lg,
  },
  sheet: {
    backgroundColor: colors.surface,
    borderRadius: radii.lg,
    padding: spacing.lg,
    gap: spacing.md,
  },
  question: { textAlign: 'center', color: colors.primary },
});
