/** Acceso del adulto. La única pantalla con credenciales de toda la app. */

import { router } from 'expo-router';
import React, { useState } from 'react';
import { View } from 'react-native';

import { ApiError } from '../src/api/client';
import { Body, Button, Display, ErrorNote, Field, Screen } from '../src/components/ui';
import { useSession } from '../src/context/SessionContext';
import { spacing } from '../src/theme';

export default function Login() {
  const { signIn } = useSession();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    setBusy(true);
    setError(null);
    try {
      await signIn(email.trim(), password);
      router.replace('/');
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'No hemos podido conectar');
    } finally {
      setBusy(false);
    }
  };

  return (
    <Screen>
      <View style={{ gap: spacing.sm, marginTop: spacing.xl }}>
        <Display>Retos</Display>
        <Body>Un reto a la semana. El niño lo hace fuera de la pantalla.</Body>
      </View>

      <View style={{ gap: spacing.md, marginTop: spacing.xl }}>
        <Field
          label="Correo"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          placeholder="tu@correo.com"
        />
        <Field
          label="Contraseña"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          placeholder="Tu contraseña"
        />
        {error ? <ErrorNote message={error} /> : null}
        <Button label="Entrar" onPress={submit} loading={busy} />
        <Button
          label="Crear una cuenta"
          variant="ghost"
          onPress={() => router.push('/register')}
        />
      </View>
    </Screen>
  );
}
