/**
 * Borrado de la cuenta.
 *
 * Google Play exige que una app que permite crear una cuenta permita también
 * borrarla desde dentro, sin escribir a nadie. Esta pantalla es ese camino.
 *
 * Pide escribir una palabra en lugar de un diálogo de sí/no: es irreversible y
 * se llega hasta aquí desde la zona de adultos, que ya está tras la barrera.
 * Un botón suelto lo pulsa un niño; escribir BORRAR, no.
 */

import { router } from 'expo-router';
import React, { useState } from 'react';
import { View } from 'react-native';

import { ApiError } from '../../src/api/client';
import { useDeleteAccount } from '../../src/api/hooks';
import {
  Body,
  Button,
  Caption,
  Card,
  Display,
  ErrorNote,
  Field,
  Screen,
  Title,
} from '../../src/components/ui';
import { useSession } from '../../src/context/SessionContext';
import { spacing } from '../../src/theme';

const CONFIRMATION = 'BORRAR';

export default function DeleteAccount() {
  const { signOut } = useSession();
  const deleteAccount = useDeleteAccount();
  const [typed, setTyped] = useState('');
  const [error, setError] = useState<string | null>(null);

  const confirmed = typed.trim().toUpperCase() === CONFIRMATION;

  const submit = async () => {
    setError(null);
    try {
      await deleteAccount.mutateAsync();
      await signOut();
      router.replace('/login');
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'No hemos podido conectar');
    }
  };

  return (
    <Screen tone="parent">
      <Display>Borrar la cuenta</Display>

      <Card style={{ gap: spacing.sm }}>
        <Title>Qué se borra</Title>
        <Body>· Tu cuenta y tu correo.</Body>
        <Body>· Los perfiles de tus hijos, con su nombre y su edad.</Body>
        <Body>· Todo su progreso: retos validados y premios elegidos.</Body>
        <Body>· Los códigos de recompensa que aún no hayas canjeado.</Body>
        <Caption>
          Es inmediato y no se puede deshacer. No guardamos copia ni queda nada marcado como
          borrado.
        </Caption>
      </Card>

      <Card style={{ gap: spacing.sm }}>
        <Title>Qué no se borra aquí</Title>
        <Body>
          La suscripción se contrata con Google Play y solo puedes cancelarla tú, desde Play
          en Pagos y suscripciones. Bórrala antes o seguirá cobrándose.
        </Body>
      </Card>

      <View style={{ gap: spacing.md }}>
        <Field
          label={`Escribe ${CONFIRMATION} para confirmar`}
          value={typed}
          onChangeText={setTyped}
          placeholder={CONFIRMATION}
          autoCapitalize="words"
        />
        {error ? <ErrorNote message={error} /> : null}
        <Button
          label="Borrar mi cuenta para siempre"
          variant="danger"
          disabled={!confirmed}
          loading={deleteAccount.isPending}
          onPress={submit}
        />
        <Button label="Cancelar" variant="ghost" onPress={() => router.back()} />
      </View>
    </Screen>
  );
}
