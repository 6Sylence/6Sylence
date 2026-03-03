import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { api } from '../src/services/api';
import { useAuth } from '../src/context/AuthContext';

const COLORS = {
  primary: '#1A1A2E',
  accent: '#E94560',
  white: '#FFFFFF',
};

export default function AuthCallback() {
  const router = useRouter();
  const { checkAuth } = useAuth();
  const hasProcessed = useRef(false);

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processAuth = async () => {
      try {
        // Get session_id from URL fragment
        const url = window.location.href;
        const hashIndex = url.indexOf('#');
        if (hashIndex === -1) {
          router.replace('/(tabs)');
          return;
        }

        const fragment = url.substring(hashIndex + 1);
        const params = new URLSearchParams(fragment);
        const sessionId = params.get('session_id');

        if (!sessionId) {
          router.replace('/(tabs)');
          return;
        }

        // Exchange session_id for session_token
        await api.exchangeSession(sessionId);
        
        // Refresh auth state
        await checkAuth();
        
        // Clear URL and redirect
        window.history.replaceState({}, '', window.location.pathname);
        router.replace('/(tabs)');
      } catch (error) {
        console.error('Auth error:', error);
        router.replace('/(tabs)');
      }
    };

    processAuth();
  }, []);

  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color={COLORS.accent} />
      <Text style={styles.text}>Iniciando sesión...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  text: {
    color: COLORS.white,
    fontSize: 16,
    marginTop: 16,
  },
});
