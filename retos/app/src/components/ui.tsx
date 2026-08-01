/** Piezas de interfaz compartidas. */

import React from 'react';
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
  type StyleProp,
  type TextStyle,
  type ViewStyle,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { TOUCH_MIN, colors, radii, spacing, type } from '../theme';

export function Screen({
  children,
  scroll = true,
  tone = 'kid',
}: {
  children: React.ReactNode;
  scroll?: boolean;
  tone?: 'kid' | 'parent';
}) {
  const background = tone === 'kid' ? colors.bg : colors.parentBg;
  const content = (
    <View style={styles.screenInner}>{children}</View>
  );
  return (
    <SafeAreaView style={[styles.screen, { backgroundColor: background }]} edges={['top', 'bottom']}>
      {scroll ? (
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          {content}
        </ScrollView>
      ) : (
        content
      )}
    </SafeAreaView>
  );
}

export function Title({ children, style }: { children: React.ReactNode; style?: StyleProp<TextStyle> }) {
  return <Text style={[type.title, { color: colors.ink }, style]}>{children}</Text>;
}

export function Display({ children }: { children: React.ReactNode }) {
  return <Text style={[type.display, { color: colors.ink }]}>{children}</Text>;
}

export function Body({ children, style }: { children: React.ReactNode; style?: StyleProp<TextStyle> }) {
  return <Text style={[type.body, { color: colors.inkSoft }, style]}>{children}</Text>;
}

export function Caption({ children, style }: { children: React.ReactNode; style?: StyleProp<TextStyle> }) {
  return <Text style={[type.caption, { color: colors.inkSoft }, style]}>{children}</Text>;
}

export function Card({
  children,
  style,
  onPress,
}: {
  children: React.ReactNode;
  style?: StyleProp<ViewStyle>;
  onPress?: () => void;
}) {
  if (onPress) {
    return (
      <Pressable
        onPress={onPress}
        style={({ pressed }) => [styles.card, pressed && styles.pressed, style]}
      >
        {children}
      </Pressable>
    );
  }
  return <View style={[styles.card, style]}>{children}</View>;
}

export function Button({
  label,
  onPress,
  variant = 'primary',
  disabled = false,
  loading = false,
}: {
  label: string;
  onPress: () => void;
  variant?: 'primary' | 'ghost' | 'danger';
  disabled?: boolean;
  loading?: boolean;
}) {
  const isDisabled = disabled || loading;
  return (
    <Pressable
      onPress={onPress}
      disabled={isDisabled}
      accessibilityRole="button"
      style={({ pressed }) => [
        styles.button,
        variant === 'primary' && styles.buttonPrimary,
        variant === 'ghost' && styles.buttonGhost,
        variant === 'danger' && styles.buttonDanger,
        pressed && !isDisabled && styles.pressed,
        isDisabled && styles.buttonDisabled,
      ]}
    >
      {loading ? (
        <ActivityIndicator color={variant === 'ghost' ? colors.ink : '#FFFFFF'} />
      ) : (
        <Text
          style={[
            type.label,
            styles.buttonLabel,
            variant === 'ghost' && { color: colors.ink },
          ]}
        >
          {label}
        </Text>
      )}
    </Pressable>
  );
}

export function Field({
  label,
  value,
  onChangeText,
  placeholder,
  secureTextEntry,
  keyboardType,
  autoCapitalize = 'none',
}: {
  label: string;
  value: string;
  onChangeText: (value: string) => void;
  placeholder?: string;
  secureTextEntry?: boolean;
  keyboardType?: 'default' | 'email-address';
  autoCapitalize?: 'none' | 'words';
}) {
  return (
    <View style={styles.field}>
      <Text style={[type.label, { color: colors.ink }]}>{label}</Text>
      <TextInput
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor={colors.locked}
        secureTextEntry={secureTextEntry}
        keyboardType={keyboardType}
        autoCapitalize={autoCapitalize}
        autoCorrect={false}
        style={styles.input}
      />
    </View>
  );
}

/** Progreso de la semana. Puntos, no porcentajes: se lee de un vistazo. */
export function ProgressPips({ total, done }: { total: number; done: number }) {
  return (
    <View style={styles.pips}>
      {Array.from({ length: total }).map((_, index) => (
        <View
          key={index}
          style={[styles.pip, index < done && { backgroundColor: colors.done }]}
        />
      ))}
    </View>
  );
}

export function ErrorNote({ message }: { message: string }) {
  return (
    <View style={styles.errorNote}>
      <Text style={[type.label, { color: colors.danger }]}>{message}</Text>
    </View>
  );
}

export function Loading() {
  return (
    <View style={styles.loading}>
      <ActivityIndicator size="large" color={colors.primary} />
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  screenInner: { padding: spacing.lg, gap: spacing.md, flex: 1 },
  scrollContent: { flexGrow: 1 },
  card: {
    backgroundColor: colors.surface,
    borderRadius: radii.md,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    gap: spacing.sm,
  },
  pressed: { opacity: 0.85, transform: [{ scale: 0.99 }] },
  button: {
    minHeight: TOUCH_MIN,
    borderRadius: radii.pill,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.lg,
  },
  buttonPrimary: { backgroundColor: colors.primary },
  buttonGhost: { backgroundColor: 'transparent', borderWidth: 2, borderColor: colors.border },
  buttonDanger: { backgroundColor: colors.danger },
  buttonDisabled: { backgroundColor: colors.locked },
  buttonLabel: { color: '#FFFFFF', fontSize: 18 },
  field: { gap: spacing.xs },
  input: {
    minHeight: 52,
    borderRadius: radii.sm,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
    paddingHorizontal: spacing.md,
    fontSize: 17,
    color: colors.ink,
  },
  pips: { flexDirection: 'row', gap: spacing.sm },
  pip: {
    width: 22,
    height: 22,
    borderRadius: radii.pill,
    backgroundColor: colors.border,
  },
  errorNote: {
    backgroundColor: '#FDECEA',
    borderRadius: radii.sm,
    padding: spacing.md,
  },
  loading: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: spacing.xxl },
});
