/** Alta del adulto. Incluye la prueba gratuita de 7 días. */

import { router } from 'expo-router';
import React, { useState } from 'react';
import { View } from 'react-native';

import { ApiError } from '../src/api/client';
import { Body, Button, Caption, Display, ErrorNote, Field, Screen } from '../src/components/ui';
import { useSession } from '../src/context/SessionContext';
import { spacing } from '../src/theme';

export default function Register() {
  const { signUp } = useSession();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    if (password.length < 8) {
      setError('La contraseña necesita al menos 8 caracteres');
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await signUp(email.trim(), password);
      router.replace('/onboarding/child');
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'No hemos podido conectar');
    } finally {
      setBusy(false);
    }
  };

  return (
    <Screen>
      <View style={{ gap: spacing.sm, marginTop: spacing.xl }}>
        <Display>Crear cuenta</Display>
        <Body>
          La cuenta es tuya, no de tu hijo. Él no necesita usuario ni contraseña en ningún
          momento.
        </Body>
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
          placeholder="Mínimo 8 caracteres"
        />
        {error ? <ErrorNote message={error} /> : null}
        <Button label="Empezar la prueba de 7 días" onPress={submit} loading={busy} />
        <Caption>
          La primera semana de retos es gratis y no caduca. La prueba solo hace falta para
          continuar a partir de la semana 2.
        </Caption>
        <Button label="Ya tengo cuenta" variant="ghost" onPress={() => router.replace('/login')} />
      </View>
    </Screen>
  );
}
