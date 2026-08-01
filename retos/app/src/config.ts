/**
 * Enlaces públicos.
 *
 * La política de privacidad tiene que estar alojada en una URL accesible sin
 * iniciar sesión: Google Play la pide en la ficha y, siendo una app dirigida a
 * menores, la revisa a mano.
 */

export const PRIVACY_POLICY_URL =
  process.env.EXPO_PUBLIC_PRIVACY_URL ?? 'https://ejemplo.com/privacidad';

export const SUPPORT_EMAIL = process.env.EXPO_PUBLIC_SUPPORT_EMAIL ?? 'hola@ejemplo.com';
