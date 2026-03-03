import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../src/services/api';

const COLORS = {
  primary: '#1A1A2E',
  accent: '#E94560',
  gold: '#D4AF37',
  white: '#FFFFFF',
  lightGray: '#F5F5F5',
  text: '#333333',
};

export default function CategoriesScreen() {
  const router = useRouter();

  const { data: categories, isLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: api.getCategories,
  });

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Categorías</Text>
        <Text style={styles.headerSubtitle}>Explora por categoría</Text>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {isLoading ? (
          <ActivityIndicator color={COLORS.accent} size="large" style={{ marginTop: 40 }} />
        ) : (
          <View style={styles.categoriesGrid}>
            {categories?.map((category: any) => (
              <TouchableOpacity
                key={category.category_id}
                style={[styles.categoryCard, { borderColor: category.color }]}
                onPress={() => router.push(`/category/${category.category_id}`)}
                activeOpacity={0.7}
              >
                <View style={[styles.iconContainer, { backgroundColor: category.color + '20' }]}>
                  <Ionicons name={category.icon as any} size={32} color={category.color} />
                </View>
                <Text style={styles.categoryName}>{category.name}</Text>
                <Ionicons name="chevron-forward" size={20} color={COLORS.text} />
              </TouchableOpacity>
            ))}
          </View>
        )}
        <View style={{ height: 100 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.primary,
  },
  header: {
    paddingHorizontal: 16,
    paddingVertical: 20,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: COLORS.white,
  },
  headerSubtitle: {
    fontSize: 14,
    color: COLORS.gold,
    marginTop: 4,
  },
  content: {
    flex: 1,
    backgroundColor: COLORS.lightGray,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingTop: 20,
  },
  categoriesGrid: {
    paddingHorizontal: 16,
  },
  categoryCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.white,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  iconContainer: {
    width: 56,
    height: 56,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  categoryName: {
    flex: 1,
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
  },
});
